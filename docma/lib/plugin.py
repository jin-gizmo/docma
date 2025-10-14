"""
Generic plugin mechanism for frameworks that lookup plugins using a dict.

e.g. Jinja filters and tests, and JSONschema format checkers use dicts to hold
their plugins.

The dictionary object that the framework normally uses for looking up plugins
gets replaced by a `PluginRouter` object. This appears as a dictionary that
returns a callable that implements the plugin.

The plugin router must be initialised with one or more `PluginResolver`
instances. A resolvers maps a plugin name to the callable that implements it,
or None if it is not known to the resolver. The PluginResolver instance
tries each of its resolvers in turn until it either finds the plugin or exhausts
all resolvers.

Resolvers don't have to worry about cacheing. PluginRouter does that.

In the case of JInja filters, this gets used like so ...

```python
from jinja2 import Environment
from docma.lib.plugin import MappingResolver, PackageResolver, PluginRouter

e = Environment()
e.filters = PluginRouter(
    [
        MappingResolver(e.filters),  # Preserve Jinja built-in filters
        PackageResolver('docma.plugins.jinja_filters'),
    ],
)
```

"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from types import ModuleType
from typing import Any, Callable
from warnings import warn

__author__ = 'Murray Andrews'

PluginType = Callable[..., Any]

# These constants are plugin types. Each plugin needs to be annotated with the
# types that it supports (can be one or more). The PackageResolver will look for
# plugins that have any of the types it is told to use.
PLUGIN_JINJA_FILTER = 'jinja-filter'
PLUGIN_JINJA_TEST = 'jinja-test'
PLUGIN_JSONSCHEMA_FORMAT = 'jsonschema-format-checker'


# ------------------------------------------------------------------------------
def jfilter(*args, **kwargs) -> PluginType:
    """Mark a callable as a Jinja filter."""
    return Plugin.plugin(PLUGIN_JINJA_FILTER, *args, **kwargs)


# ------------------------------------------------------------------------------
def jtest(*args, **kwargs) -> PluginType:
    """Mark a callable as a Jinja test."""
    return Plugin.plugin(PLUGIN_JINJA_TEST, *args, **kwargs)


# ------------------------------------------------------------------------------
class PluginError(Exception):
    """Exception to raise when a plugin or plugin category cannot be loaded."""

    pass


# ------------------------------------------------------------------------------
class PluginResolver(ABC):
    """Base class for plugin resolvers."""

    @abstractmethod
    def resolve(self, name: str) -> PluginType | None:
        """Resolve a plugin name into a callable or return None."""
        raise NotImplementedError


# ------------------------------------------------------------------------------
class Plugin:
    """Container for plugin related functionality."""

    # --------------------------------------------------------------------------
    @staticmethod
    def plugin(
        plugin_types: str | Iterable[str], name: str, *aliases: str, deprecation: str | None = None
    ) -> PluginType:
        """
        Decorate a plugin so we know its name and to which families it belongs.

        :param plugin_types:    Indicates the families to which this plugin belongs.
        :param name:            Plugin name.
        :param aliases:         Alternative names. No need to use this for case
                                variations as these are supported natively.
        :param deprecation:     Optional deprecation warning.

        """

        # ----------------------------------------------------------------------
        def decorate(func: PluginType) -> PluginType:
            """Annotate the callable."""

            func._plugin_id = name  # noqa: SLF001
            func._plugin_names = {name.lower()}.union(a.lower() for a in aliases)  # noqa: SLF001
            func._plugin_types = (  # noqa: SLF001
                {plugin_types} if isinstance(plugin_types, str) else set(plugin_types)
            )
            func._plugin_deprecation = deprecation  # noqa: SLF001
            return func

        return decorate


# ------------------------------------------------------------------------------
class PluginRouter(MutableMapping[str, PluginType]):
    """
    A dict-like object for dict lookup that delegates resolution to resolvers.

    :param resolvers:   An iterable of PluginResolver instances. Plugin
                        lookups will try each resolver in turn.

    """

    # --------------------------------------------------------------------------
    def __init__(self, resolvers: Sequence[PluginResolver]):
        """Create a new PluginResolver instance."""
        self._resolvers = list(resolvers)
        # Internal cache. Also allows later addition of plugins (__setitem__)
        self._plugins: dict[str, PluginType | None] = {}
        # Keep track of deprecation warnings to avoid duplicate warnings.
        self._warned = set()

    # --------------------------------------------------------------------------
    @staticmethod
    def _canonical(key: str) -> str:
        """Return canonical lowercase key for lookup."""
        return key.lower()

    # --------------------------------------------------------------------------
    def _deprecation_check(self, key: str, plugin: PluginType) -> PluginType:
        """
        Raise a deprecation warning for deprecated plugins.

        :param key:     The key used to resolve the plugin.
        :param plugin:  The plugin to check.

        :return:        The plugin (unmodified).
        """

        ckey = self._canonical(key)
        if (
            deprecation := getattr(plugin, '_plugin_deprecation', None)
        ) and ckey not in self._warned:
            warn(
                f'Plugin {key} is deprecated. {deprecation}',
                category=DeprecationWarning,
                stacklevel=2,
            )
            self._warned.add(ckey)

        return plugin

    # --------------------------------------------------------------------------
    def get(self, key: str, default=None) -> PluginType:
        """Get a plugin by name."""
        try:
            return self[key]
        except KeyError:
            return default

    # --------------------------------------------------------------------------
    def __getitem__(self, key: str) -> PluginType:
        """Get a plugin by name."""

        # The deprecation logic here is a bit of a tradeoff. One option is to
        # handle that via a wrapper in the registration decorator. That is neat
        # because the warning process is as close as it can be to the point of
        # invocation. Problem with that is, the fully qualified name used to
        # invoke a plugin is only known here. So to avoid ambiguity about the
        # subject of the warning, we handle deprecation here.

        if (ckey := self._canonical(key)) in self._plugins:
            if (plugin := self._plugins[ckey]) is None:
                # This can occur if a lookup of this key failed previously.
                raise KeyError(key)
            return self._deprecation_check(key, plugin)

        # Try resolvers in order; when found, cache and emit deprecation once
        for resolver in self._resolvers:
            if (plugin := resolver.resolve(ckey)) is None:
                continue
            self._plugins[ckey] = plugin
            return self._deprecation_check(key, plugin)

        # Cache miss -- may as well remember this as well.
        self._plugins[ckey] = None
        raise KeyError(key)

    # --------------------------------------------------------------------------
    def __setitem__(self, key: str, value: PluginType) -> None:
        """Set a plugin by name."""
        self._plugins[self._canonical(key)] = value

    def __delitem__(self, key: str) -> None:
        """Remove a plugin by name."""
        del self._plugins[self._canonical(key)]

    def __iter__(self):
        """Iterate over currently loaded plugins."""
        return (k for k, v in self._plugins.items() if v is not None)

    def __len__(self) -> int:
        """Return number of loaded plugins."""
        return sum(1 for v in self._plugins.values() if v is not None)

    def __contains__(self, key: str) -> bool:
        """
        Check if a plugin exists in the currently loaded plugins.

        Note that our self._plugins cache can also hold previous failed lookups
        which will hve a None plugin value. We have to ignore those.

        """
        if (ckey := self._canonical(key)) in self._plugins:
            return self._plugins[ckey] is not None

        for resolver in self._resolvers:
            if (plugin := resolver.resolve(ckey)) is not None:
                self._plugins[ckey] = plugin
                return True

        # Remember failed lookup for later. Debatable optimisation but whatever.
        self._plugins[ckey] = None
        return False


# ------------------------------------------------------------------------------
class MappingResolver(PluginResolver):
    """
    Resolver that looks up plugins from a plain dictionary.

    In the case of Jinja filters, for example, This can be used to hold Jinja's
    factory-fitted filters. e.g.

    ```python
    env = jinja2.Environment()
    env.filters = PluginRouter([MappingResolver(env.filters)])
    ```

    """

    def __init__(self, mapping: Mapping[str, PluginType]):
        """Create a MappingResolver instance."""
        self._mapping = dict(mapping)

    def resolve(self, name: str) -> PluginType | None:
        """Return the plugin if present, else None."""
        return self._mapping.get(name)


# ------------------------------------------------------------------------------
class PackageResolver(PluginResolver):
    """
    Resolve plugins from a Python package hierarchy.

    - Top-level plugins (directly in the base package) are loaded eagerly.
    - Category plugins (subpackages) are loaded lazily when first accessed.

    Plugins are organised as a standard python package hierarchy with the plugin
    callables (typically functions) marked with a decorator, `plugin_marker()`.
    The package hierarchy (excluding the final Python filename) is used
    to form the prefix for the plugin name. The last component of the name is
    specified in the decorator.

    The plugin_decorator annotates the plugin with two attributes:

    *  `_plugin_types`:
        A set of strings that is used to determine if a resolver instance should
        notice the plugin.
    * `_plugin_names`:
        A tuple of strings containing the trailing component of the plugin names.

    This is a sample hierarchy for a plugin package.

    ```text
        .
        ├── __init__.py
        └── filters                 (Base for all plugins)
            ├── __init__.py
            ├── whatever.py         (Plagins with no category)
            └── au                  (Base for all "au.*" plugins
                ├── __init__.py
                ├── company_ids.py  (Can contain multiple plugins, eg. "abn", "acn")
                └── tax             (Base for all "au.tax.*" plugins)
                    ├── __init__.py
                    └── tax.py      (Can contain multiple plugins, eg. "tfn")
    ```

    In this example, we are defining plugins named `au.abn` and `au.tax.tfn`.
    The "category" here is `au`.

    Filters at the top level (e.g. in `whatever.py`) are preloaded. The nested
    plugins are lazy loaded at the category level when invoked.

    """

    # --------------------------------------------------------------------------
    def __init__(self, package: str, plugin_types: str | set[str]) -> None:
        """
        Create a PackageResolver instance.

        :param package:     A Python package name (e.g. `jinja.filters`).
        :param plugin_types: A set of strings indicating the type of plugins to load.
        """

        self._package = package
        self._categories: set[str] = set()
        self._plugins: dict[str, PluginType] = {}
        self._plugin_types: set[str] = (
            {plugin_types} if isinstance(plugin_types, str) else plugin_types
        )

        # Eagerly load top-level modules
        self._load_top_level()

    # --------------------------------------------------------------------------
    def resolve(self, name: str) -> PluginType | None:
        """Resolve a plugin name into a callable or return None."""

        if name in self._plugins:
            return self._plugins[name]

        # Look up by category
        category = name.split('.', 1)[0] if '.' in name else None
        if category and category not in self._categories:
            try:
                self._load_category(category)
            except (ImportError, ModuleNotFoundError):
                return None

        return self._plugins.get(name)

    # --------------------------------------------------------------------------
    def _load_top_level(self) -> None:
        """Load plugins from modules directly under the package (no category)."""

        pkg = importlib.import_module(self._package)
        # pkgutil.iter_modules needs a path list, not the module itself
        # We can still use pkgutil since it works with __path__ attribute
        search_path = getattr(pkg, '__path__', None)
        if search_path is None:
            return

        for _, modname, ispkg in pkgutil.iter_modules(search_path, self._package + '.'):
            if ispkg:
                continue
            module = importlib.import_module(modname)
            self._register_module_plugins(module, prefix='')

    # --------------------------------------------------------------------------
    def _load_category(self, category: str) -> None:
        """Import and register all plugins in a category package."""

        pkg_name = f'{self._package}.{category}'
        pkg = importlib.import_module(pkg_name)
        modules: list[ModuleType] = [pkg]

        # Import submodules under this category
        search_path = getattr(pkg, '__path__', None)
        if search_path is not None:
            for _, modname, _ in pkgutil.walk_packages(search_path, pkg_name + '.'):
                modules.append(importlib.import_module(modname))

        for module in modules:
            # Use module.__name__ to derive the prefix instead of __file__
            prefix = self._module_prefix_from_name(module.__name__)
            self._register_module_plugins(module, prefix)

        self._categories.add(category)

    # --------------------------------------------------------------------------
    def _register_module_plugins(self, module: ModuleType, prefix: str) -> None:
        """Find and register plugin callables from a module."""
        for _, obj in inspect.getmembers(module, callable):
            if not (names := getattr(obj, '_plugin_names', None)):
                continue
            if not getattr(obj, '_plugin_types', set()) & self._plugin_types:
                # This plugin is not a type of interest.
                continue
            for member in names:
                fqname = f'{prefix}.{member}' if prefix else member
                self._plugins[fqname] = obj

    # --------------------------------------------------------------------------
    def _module_prefix_from_name(self, module_name: str) -> str:
        """
        Return the namespace prefix for plugins in a module based on its name.

        For example:
        - Base package: 'docma.plugins.filters'
        - Module name: 'docma.plugins.filters.au.tax.tax'
        - Result: 'au.tax'

        The module filename (last component) is not included in the prefix.
        """
        base_parts = self._package.split('.')
        module_parts = module_name.split('.')

        # Everything between the base package and the module name itself forms the prefix
        if len(module_parts) <= len(base_parts):
            return ''

        # Get the package path (exclude the base and the module filename)
        # For 'docma.plugins.filters.au.tax.tax', we want 'au.tax'
        prefix_parts = module_parts[len(base_parts) : -1]
        return '.'.join(prefix_parts)
