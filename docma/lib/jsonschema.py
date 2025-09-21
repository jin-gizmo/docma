"""JSONschema utilities."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from jsonschema import FormatChecker
from jsonschema.exceptions import FormatError

from docma.jinja.resolvers import DateFormatResolver
from .plugin import (
    PLUGIN_JINJA_TEST,
    PLUGIN_JSONSCHEMA_FORMAT,
    PackageResolver,
    Plugin,
    PluginResolver,
    PluginRouter,
    PluginType,
)


# ------------------------------------------------------------------------------
def format_checker(*args, **kwargs) -> PluginType:
    """Mark a callable as a format checker suitable for Jinja or JSONschema."""
    return Plugin.plugin({PLUGIN_JINJA_TEST, PLUGIN_JSONSCHEMA_FORMAT}, *args, **kwargs)


# ------------------------------------------------------------------------------
class PluginFormatChecker(FormatChecker):
    """
    A JSONschema FormatChecker that uses PluginRouter to look up format checkers.

    Expects all format plugins to be boolean-returning callables. i.e. they
    must not use an exception to flag that the value does not comply with the
    format.

    :param resolvers:       An iterable of PluginResolver instances. Plugin
                            lookups will try each resolver in turn.
    """

    # --------------------------------------------------------------------------
    def __init__(self, resolvers: Sequence[PluginResolver]):
        """Create a new PluginResolver instance."""
        super().__init__()
        self._router = PluginRouter(resolvers)
        # There is a deliberate type mismatch here. jsonschema.FormatChecker.checkers
        # is normally a dict but we are replacing it with dict-emulating PluginRouter.
        # noinspection PyTypeChecker
        self.checkers = self._router

    # --------------------------------------------------------------------------
    def check(self, instance: Any, format: str) -> None:  # noqa A002
        """Check whether the instance conforms to the given format."""

        if format not in self._router:
            # Design decision: Using KeyError instead of FormatError causes a
            # deliberate blowup here.
            raise KeyError(f'Unknown format {format!r}')

        func = self._router[format]
        ok = func(instance)
        if not ok:
            raise FormatError(f'{instance!r} is not a {format!r}')


# ------------------------------------------------------------------------------
class JsonSchemaBuiltinsResolver(PluginResolver):
    """
    Adapts builtin jsonschema.FormatChecker checkers into boolean-returning callables.

    This is required because we are using our own plugin registration and lookup
    system and it just registers the callable implementing the plugin. The
    JSONschema version of this for format checkers registers the callable as well
    as exceptions it may raise that indicate a negative format match. We need to
    adapt that style to our own plugin style.
    """

    # --------------------------------------------------------------------------
    def __init__(self, base: FormatChecker | None = None) -> None:
        """
        Create a new PluginResolver instance.

        :param base:    A base FormatChecker instance from which to obtain the
                        checkers. Defaults to a clean FormatChecker instance.
        """

        self._base = base or FormatChecker()
        self._checkers = dict(self._base.checkers)

    # --------------------------------------------------------------------------
    def resolve(self, name: str) -> PluginType | None:
        """Resolve a plugin name into a callable or return None."""

        if name not in self._checkers:
            return None

        func, raises = self._checkers.get(name)

        # ----------------------------------------
        def wrapped(instance: Any) -> bool:
            """
            Wrap the native checker to handle exceptions.

            In order to adapt the JSONschema style to our plugin system, we wrap
            the JSONschema checkers to catch the exceptions and have it return
            False when that occurs.
            """
            try:
                return bool(func(instance))
            except raises:
                return False

        # ----------------------------------------
        # Mark as a plugin. Probably not necessary.
        return Plugin.plugin(PLUGIN_JSONSCHEMA_FORMAT, name)(wrapped)


FORMAT_CHECKER = PluginFormatChecker(
    resolvers=[
        JsonSchemaBuiltinsResolver(),
        DateFormatResolver(),
        PackageResolver('docma.plugins.format_checkers', PLUGIN_JSONSCHEMA_FORMAT),
    ]
)
