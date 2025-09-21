"""Test Jinja plugin mgmt."""

import warnings
from uuid import uuid4

import pytest  # noqa

from docma.lib.plugin import (
    MappingResolver,
    PLUGIN_JINJA_FILTER,
    PLUGIN_JINJA_TEST,
    PackageResolver,
    PluginRouter,
    jfilter,
    jtest,
)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('plugin', ['tojson', 'au.acn', 'AU.Acn', 'phone'])
def test_plugin_router_getitem_ok(plugin, jfilters):
    assert jfilters[plugin]


def test_plugin_router_getitem_fail(jfilters):
    with pytest.raises(KeyError, match='no-such-filter'):
        _ = jfilters['no-such-filter']

    # The second check will hit the plugin router cache
    with pytest.raises(KeyError, match='no-such-filter'):
        _ = jfilters['no-such-filter']


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('plugin', ['tojson', 'au.acn', 'AU.Acn', 'phone'])
def test_plugin_router_get_ok(plugin, jfilters):
    assert jfilters.get(plugin)


# ------------------------------------------------------------------------------
def test_plugin_router_get_fail(jfilters):
    assert jfilters.get(uuid4().hex, 'dummy') == 'dummy'


# ------------------------------------------------------------------------------
def test_plugin_router_setitem(jfilters):
    name = uuid4().hex
    count = len(jfilters)  # Currently loaded filters
    assert name not in jfilters

    jfilters[name] = lambda _: 'test'

    assert name in jfilters
    assert len(jfilters) == count + 1


# ------------------------------------------------------------------------------
def test_plugin_router_delitem(jfilters):
    name = uuid4().hex
    count = len(jfilters)  # Currently loaded filters
    assert name not in jfilters

    jfilters[name] = lambda _: 'test'

    assert name in jfilters
    assert len(jfilters) == count + 1

    del jfilters[name]

    assert name not in jfilters
    assert len(jfilters) == count


# ------------------------------------------------------------------------------
def test_plugin_router_iter(jfilters):
    # Force some filters be loaded into the cache
    assert jfilters.get('tojson')
    assert jfilters['au.acn']
    assert jfilters['phone']

    loaded = list(jfilters.keys())
    assert 'tojson' in loaded


# ------------------------------------------------------------------------------
def test_jfilter():

    # noinspection PyUnusedLocal
    @jfilter('name', 'alias1', 'alias2')
    def f(value):
        """Echo (dummy filter)."""
        raise NotImplementedError

    assert f._plugin_names == {'name', 'alias1', 'alias2'}
    assert PLUGIN_JINJA_FILTER in f._plugin_types


# ------------------------------------------------------------------------------
def test_jtest():

    # noinspection PyUnusedLocal
    @jtest('name', 'alias1', 'alias2')
    def f(*args, **kwargs):
        """Echo (dummy filter)."""
        raise NotImplementedError

    assert f._plugin_names == {'name', 'alias1', 'alias2'}
    assert PLUGIN_JINJA_TEST in f._plugin_types


# ------------------------------------------------------------------------------
def test_deprecated_decorator_on_plugin_ok():
    """Ensure deprecation decorator emits a warning."""

    @jfilter('test', deprecation='Deprecation test')
    def f(s: str) -> str:
        """Echo (deprecated)."""
        return s

    plugger = PluginRouter([MappingResolver({'test': f})])

    # Doing a lookup on a deprecated plugin is enough to issue the warning.
    with pytest.warns(DeprecationWarning, match='Deprecation test'):
        assert plugger.get('test') is f
        assert f('test') == 'test'

    # Only one warning should be issued
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        assert plugger.get('test') is f
        assert len(w) == 0


# ------------------------------------------------------------------------------
class TestPackageResolver:
    # --------------------------------------------------------------------------
    def test_package_resolver_lookup_fail(self):

        res = PackageResolver('docma.plugins.jinja_filters', PLUGIN_JINJA_FILTER)

        assert res.resolve('bad-bad-bad.something') is None

    # --------------------------------------------------------------------------
    def test_package_resolver_unknown_package_fail(self):

        with pytest.raises(ModuleNotFoundError, match=r'No module named'):
            PackageResolver('no.such.package', PLUGIN_JINJA_FILTER)

    # --------------------------------------------------------------------------
    def test_package_resolver_module_not_package_ok(self, tmp_path, capsys, monkeypatch):
        """
        Test where the resolver is pointed at a module not a package.

        The PackageResolver does import these but deliberately ignores them.
        """

        (tmp_path / 'module.py').write_text(
            """
from docma.lib.plugin import jfilter

print('IMPORT WHIZBANG')

@jfilter('whizbang')
def f(value):
    return f'Whizbang {value}'

        """
        )
        monkeypatch.syspath_prepend(str(tmp_path))

        res = PackageResolver('module', PLUGIN_JINJA_FILTER)
        assert 'IMPORT WHIZBANG' in capsys.readouterr().out
        assert len(res._plugins) == 0

    # --------------------------------------------------------------------------
    def test_package_resolver_namespace_package(self, tmp_path, monkeypatch):
        """
        Test where the resolver is pointed at a namespace package not a package.

        The PackageResolver deliberately ignores these. They don't even get imported.
        This is a bit tricky to setup as a test case.
        """

        (tmp_path / 'package' / 'l1' / 'l2').mkdir(parents=True)
        (tmp_path / 'package' / 'l1' / 'l2' / 'module.py').write_text(
            """
from docma.lib.plugin import jfilter

@jfilter('whizbang')
def f(value):
    return f'Whizbang {value}'

        """
        )
        monkeypatch.syspath_prepend(str(tmp_path))

        res = PackageResolver('package', PLUGIN_JINJA_FILTER)
        # This doesn't prove much at this point as sub categories are lazy loaded.
        assert len(res._plugins) == 0

        # Try to load the sub category
        assert res.resolve('l1.l2.whizbang') is None

    # --------------------------------------------------------------------------
    def test_package_resolver_load_ok(self, tmp_path, monkeypatch):

        (tmp_path / 'package' / 'l1' / 'l2').mkdir(parents=True)
        # This __init__.py makes it a non-namespace package
        (tmp_path / 'package' / 'l1' / 'l2' / '__init__.py').write_text('\n')
        (tmp_path / 'package' / 'l1' / 'l2' / 'module.py').write_text(
            """
from docma.lib.plugin import jfilter

@jfilter('whizbang')
def f(value):
    return f'Whizbang {value}'

        """
        )
        monkeypatch.syspath_prepend(str(tmp_path))

        res = PackageResolver('package', PLUGIN_JINJA_FILTER)
        # This doesn't prove much at this point as sub categories are lazy loaded.
        assert len(res._plugins) == 0

        # Try to load the sub category
        assert res.resolve('l1.l2.whizbang')('gizmo') == 'Whizbang gizmo'
        assert len(res._plugins) == 1
