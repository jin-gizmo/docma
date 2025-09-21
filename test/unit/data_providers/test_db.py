"""Tests for docma.data_providers.db."""

from __future__ import annotations

import builtins
import importlib

import pytest  # noqa
from moto import mock_aws  # noqa
from moto.core import patch_client  # noqa

from docma.data_providers.db import *
from docma.exceptions import DocmaDataProviderError
from docma.jinja import DocmaRenderContext
from docma.lib.packager import PackageReader


# ------------------------------------------------------------------------------
def test_postgres_connect_ok(tc, env):

    conn_info = {
        param: env[f'{tc.postgres.id}_{param}'.upper()]
        for param in ('host', 'port', 'database', 'user', 'password', 'database')
    }
    conn = postgress_connect(ConnectionInfo(**conn_info))
    cursor = conn.cursor()
    cursor.execute('SELECT 1')


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'params',
    [
        {'host': 'h', 'port': 123, 'database': 'db', 'user': 'user'},
        {
            'host': 'h',
            'port': 123,
            'database': 'd',
            'user': 'u',
            'password': 'p',
            'password_param': 'p',
        },
    ],
)
def test_connectioninfo_fail(params: dict):
    with pytest.raises(ValueError):
        ConnectionInfo(**params)


# ------------------------------------------------------------------------------
def test_postgres_connect_fail(tc, env):

    conn_info = {
        param: env[f'{tc.postgres.id}_{param}'.upper()]
        for param in ('host', 'port', 'database', 'user', 'password', 'database')
    }
    conn_info['password'] = 'wrong-password'
    # Need to override the connection cache otherwise when we run all the tests
    # in xdist a previous connection will put a working connection in the cache.
    postgress_connect.cache_clear()
    with pytest.raises(
        Exception, match='Postgres connection error:.*password authentication failed'
    ):
        postgress_connect(ConnectionInfo(**conn_info))


# ------------------------------------------------------------------------------
def test_postgres_loader_ok(tc, td, dirs):
    dsp = DataSourceSpec(
        src_type='postgres',
        location=tc.postgres.id,
        query='queries/custard.yaml',
        target='whatever',
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    data = postgres_loader(dsp, context)
    assert data


# ------------------------------------------------------------------------------
@mock_aws
def test_postgres_loader_ssm_password_ok(tc, td, dirs, env):
    # Fake our SSM password param
    name = env['PGREMOTE_PASSWORD_PARAM']
    value = env['PGLOCAL_PASSWORD']
    ssm = boto3.client('ssm')
    patch_client(ssm)
    ssm.put_parameter(
        Name=name,
        Description='For docma unit tests',
        Value=value,
        Type='String',
    )
    dsp = DataSourceSpec(src_type='postgres', location='pgremote', query='queries/custard.yaml')
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    data = postgres_loader(dsp, context)
    assert data


# ------------------------------------------------------------------------------
def test_postgres_loader_too_many_rows_fail(tc, td, dirs):
    dsp = DataSourceSpec(
        src_type='postgres',
        location=tc.postgres.id,
        query='queries/custard-row-limit.yaml',
        target='whatever',
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    with pytest.raises(DocmaDataProviderError, match=r'Row limit \(\d+\) reached'):
        postgres_loader(dsp, context)


# ------------------------------------------------------------------------------
def test_postgres_loader_bad_sql_fail(tc, td, dirs):
    dsp = DataSourceSpec(
        src_type='postgres',
        location=tc.postgres.id,
        query='bad-queries/custard-bad-sql.yaml',
        target='whatever',
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    with pytest.raises(
        DocmaDataProviderError,
        match='custard-bad-sql.yaml:.*column "unknown_column" does not exist',
    ):
        postgres_loader(dsp, context)


# ------------------------------------------------------------------------------
def test_postgres_loader_bad_validation_schema_fail(tc, td, dirs):
    dsp = DataSourceSpec(
        src_type='postgres',
        location=tc.postgres.id,
        query='bad-queries/custard-bad-schema.yaml',
        target='whatever',
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    with pytest.raises(DocmaDataProviderError, match='not valid under any of the given schemas'):
        postgres_loader(dsp, context)


# ------------------------------------------------------------------------------
def test_postgres_loader_data_violates_schema_fail(tc, td, dirs):
    dsp = DataSourceSpec(
        src_type='postgres',
        location=tc.postgres.id,
        query='queries/custard-bad-data.yaml',
        target='whatever',
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    with pytest.raises(DocmaDataProviderError, match='Bad data'):
        postgres_loader(dsp, context)


# ------------------------------------------------------------------------------
def test_postgres_loader_bad_args_fail(tc, td, dirs, env):
    dsp = DataSourceSpec(
        src_type='postgres',
        location=tc.postgres.id,
        query='queries/custard.yaml',
        target='whatever',
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    with pytest.raises(DocmaDataProviderError, match='Parameters not allowed for "postgres"'):
        postgres_loader(dsp, context, bad_args=True)


# ------------------------------------------------------------------------------
def test_postgres_loader_fail(tc, dirs):

    context = DocmaRenderContext(tpkg=PackageReader.new(dirs.templates / 'test1.src'))

    with pytest.raises(DocmaDataProviderError, match='Query is required'):
        postgres_loader(DataSourceSpec(src_type='postgres', location=tc.postgres.id), context)

    with pytest.raises(DocmaDataProviderError, match='No such file or directory'):
        postgres_loader(
            DataSourceSpec(src_type='postgres', location=tc.postgres.id, query='none-such.yaml'),
            context,
        )

    with pytest.raises(DocmaDataProviderError, match='Field required'):
        postgres_loader(
            # bad-query has no query field
            DataSourceSpec(
                src_type='postgres', location=tc.postgres.id, query='bad-queries/bad-query.yaml'
            ),
            context,
        )


# ------------------------------------------------------------------------------
def test_duckdb_loader_ok(tc, td, dirs):
    ds = DataSourceSpec(
        src_type='duckdb',
        location=str((dirs.services / 'duckdb/test.db').relative_to(dirs.cwd)),
        query='queries/custard.yaml',
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    data = duckdb_loader(ds, context)
    assert data


# ------------------------------------------------------------------------------
def test_duckdb_loader_bad_args_fail(tc, td, dirs, env):
    dsp = DataSourceSpec(
        src_type='duckdb',
        location=str((dirs.services / 'duckdb/test.db').relative_to(dirs.cwd)),
        query='queries/custard.yaml',
        target='whatever',
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    with pytest.raises(DocmaDataProviderError, match='Parameters not allowed for "duckdb"'):
        duckdb_loader(dsp, context, bad_args=True)


# ------------------------------------------------------------------------------
def test_duckdb_loader_missing_query_fail(tc, td, dirs):
    ds = DataSourceSpec(
        src_type='duckdb',
        location=str((dirs.services / 'duckdb/test.db').relative_to(dirs.cwd)),
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    with pytest.raises(DocmaDataProviderError, match='Query is required'):
        duckdb_loader(ds, context)


# ------------------------------------------------------------------------------
def test_duckdb_loader_absolute_path_fail(tc, td, dirs):
    ds = DataSourceSpec(
        src_type='duckdb',
        location=str((dirs.services / 'duckdb/test.db')),
        query='queries/custard.yaml',
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    with pytest.raises(DocmaDataProviderError, match='location not relative to current directory'):
        duckdb_loader(ds, context)


# ------------------------------------------------------------------------------
def make_mock_lava_get_pysql_connection(env):
    """Factory method to create mock lava get-pysql connection maker."""

    # noinspection PyUnusedLocal
    def mock_lava_get_pysql_connection(conn_id: str, *args, **kwargs):
        """Mock lava get-pysql connection maker."""
        conn_info = {
            param: env[f'{conn_id}_{param}'.upper()]
            for param in ('host', 'port', 'database', 'user', 'password', 'database')
        }
        return postgress_connect(ConnectionInfo(**conn_info))

    return mock_lava_get_pysql_connection


# ------------------------------------------------------------------------------
def test_get_lava_db_conn_ok(env, tc, monkeypatch):
    """Test lava connection by mocking lava's get_pysql_connection to open test Postges DB."""

    # ----------------------------------------
    import docma.data_providers.db

    monkeypatch.setattr(
        docma.data_providers.db, 'get_pysql_connection', make_mock_lava_get_pysql_connection(env)
    )
    conn = get_lava_db_conn(conn_id=tc.postgres.id, realm='whatever')
    cursor = conn.cursor()
    cursor.execute('SELECT count(*) from docma.custard')
    assert cursor.fetchone()[0] > 0


# ------------------------------------------------------------------------------
def test_get_lava_db_conn_fail(tc, monkeypatch):

    zenv = dict(os.environ)
    # Mangle the password to force login to fail
    zenv[f'{tc.postgres.id.upper()}_PASSWORD'] = 'wrong-password'

    # ----------------------------------------
    import docma.data_providers.db

    monkeypatch.setattr(
        docma.data_providers.db, 'get_pysql_connection', make_mock_lava_get_pysql_connection(zenv)
    )
    # Need to override the connection cache otherwise when we run all the tests
    # in xdist a previous connection will put a working connection in the cache.
    get_lava_db_conn.cache_clear()

    # ----------------------------------------
    with pytest.raises(Exception, match='Lava connection error:.*password authentication failed'):
        get_lava_db_conn(conn_id=tc.postgres.id, realm='whatever')


# ------------------------------------------------------------------------------
def test_lava_loader_ok(dirs, env, tc, monkeypatch):

    # ----------------------------------------
    import docma.data_providers.db

    monkeypatch.setattr(
        docma.data_providers.db, 'get_pysql_connection', make_mock_lava_get_pysql_connection(env)
    )
    monkeypatch.setenv('LAVA_REALM', 'whatever')

    # ----------------------------------------
    ds = DataSourceSpec(
        src_type='lava',
        location=tc.postgres.id,
        query='queries/custard.yaml',
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    data = lava_loader(ds, context)
    assert data


# ------------------------------------------------------------------------------
def test_lava_loader_bad_args_fail(tc, td, dirs, env):
    dsp = DataSourceSpec(
        src_type='lava',
        location='does-not-matter',
        query='queries/custard.yaml',
        target='whatever',
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    with pytest.raises(DocmaDataProviderError, match='Parameters not allowed for "lava"'):
        lava_loader(dsp, context, bad_args=True)


# ------------------------------------------------------------------------------
def test_lava_loader_bad_sql_fail(tc, td, dirs, env, monkeypatch):

    # ----------------------------------------
    import docma.data_providers.db

    monkeypatch.setattr(
        docma.data_providers.db, 'get_pysql_connection', make_mock_lava_get_pysql_connection(env)
    )
    monkeypatch.setenv('LAVA_REALM', 'whatever')

    # ----------------------------------------
    dsp = DataSourceSpec(
        src_type='lava',
        location=tc.postgres.id,
        query='bad-queries/custard-bad-sql.yaml',
        target='whatever',
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )

    with pytest.raises(
        DocmaDataProviderError,
        match='custard-bad-sql.yaml:.*column "unknown_column" does not exist',
    ):
        lava_loader(dsp, context)


# ------------------------------------------------------------------------------
def test_lava_loader_missing_query_fail(dirs, env, tc, monkeypatch):

    ds = DataSourceSpec(
        src_type='lava',
        location=tc.postgres.id,
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )
    with pytest.raises(DocmaDataProviderError, match='Query is required'):
        lava_loader(ds, context)


# ------------------------------------------------------------------------------
def test_lava_loader_no_realm_fail(dirs, env, tc, monkeypatch):

    ds = DataSourceSpec(
        src_type='lava',
        location=tc.postgres.id,
        query='queries/custard.yaml',
    )
    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )
    with pytest.raises(DocmaDataProviderError, match='Realm must be set'):
        lava_loader(ds, context)


# ------------------------------------------------------------------------------
def test_get_paramstyle_from_conn_duckdb(tc):
    with duckdb.connect() as conn:
        assert get_paramstyle_from_conn(conn) == duckdb.paramstyle


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'target,expected_attr,loader_fn,message',
    [
        ('duckdb', 'duckdb', duckdb_loader, 'duckdb is required'),
        ('lava.connection', 'get_pysql_connection', lava_loader, 'jinlava is required'),
    ],
)
def test_importerror_paths(target, expected_attr, loader_fn, message, monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, globals_=None, locals_=None, fromlist=(), level=0):
        """Simulate a missing import."""
        # Match either direct or from-import
        if name == target or name.startswith(target + '.'):
            raise ImportError(f'Simulated missing {name}')
        return real_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr(builtins, '__import__', fake_import)

    import docma.data_providers.db as db

    importlib.reload(db)

    assert getattr(db, expected_attr) is None

    # Try to run the data loader that is now crippled
    with pytest.raises(DocmaDataProviderError, match=message):
        loader_fn(None, None)  # noqa
