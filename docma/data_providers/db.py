"""Database data providers."""

from __future__ import annotations

import atexit
import os
from contextlib import suppress
from functools import cache
from logging import getLogger
from pathlib import Path
from ssl import SSLContext
from typing import Any

import boto3
import pg8000
import yaml
from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, computed_field, model_validator

from docma.config import LOGNAME
from docma.exceptions import DocmaDataProviderError
from docma.jinja import DocmaRenderContext
from docma.lib.db import get_paramstyle_from_conn
from docma.lib.misc import env_config, str2bool
from docma.lib.path import relative_path
from docma.lib.query import DocmaQuerySpecification
from .__common__ import DataSourceSpec, data_provider

try:
    import duckdb
except ImportError:
    duckdb = None

try:
    # noinspection PyPackageRequirements
    from lava.connection import get_pysql_connection
except ImportError:
    get_pysql_connection = None

LOG = getLogger(LOGNAME)

# There is no good reason to set this to False. True allows multiple connections.
DUCKDB_READONLY = True


# ------------------------------------------------------------------------------
# TODO: This is Postgres specific because of the way ssl field is handled.
class ConnectionInfo(BaseModel):
    """Model for managing database connection info."""

    model_config = ConfigDict(extra='forbid', frozen=True, arbitrary_types_allowed=True)

    host: str
    port: NonNegativeInt
    user: str
    password: str
    database: str
    ssl: str = Field(default=None, exclude=True)

    @model_validator(mode='before')
    @classmethod
    def pwd(cls, values):
        """Get password from SSM if required."""
        if len({'password', 'password_param'} & set(values)) != 1:
            raise ValueError('Exactly one of password / password_param is required')
        if 'password_param' in values:
            ssm = boto3.Session().client('ssm')
            response = ssm.get_parameter(Name=values['password_param'], WithDecryption=True)
            values['password'] = response['Parameter']['Value']
            del values['password_param']
        return values

    @computed_field
    @property
    def ssl_context(self) -> SSLContext:  # noqa
        """Compute ssl context."""
        return SSLContext() if str2bool(self.ssl or False) else None


# ------------------------------------------------------------------------------
@cache
def postgress_connect(conn_info: ConnectionInfo) -> pg8000.Connection:
    """Connect to a PostgreSQL database."""

    def closer():
        """Close the connection atexit."""
        LOG.debug('Closing Postgres connection %s @ %s', conn_info.user, conn_info.host)
        try:
            conn.close()
        except Exception as _e:
            LOG.warning(
                'Failed to close Postgres connection %s @ %s : %s',
                conn_info.user,
                conn_info.host,
                _e,
            )

    LOG.debug('Connecting as %s to Postgres @ %s', conn_info.user, conn_info.host)

    try:
        conn = pg8000.connect(application_name='docma', **conn_info.model_dump())
    except Exception as e:
        raise DocmaDataProviderError(
            f'Postgres connection error: {conn_info.host}:{conn_info.port}: {e}'
        ) from e
    LOG.info('Connected as %s to Postgres @ %s', conn_info.user, conn_info.host)
    atexit.register(closer)
    return conn


# ------------------------------------------------------------------------------
@data_provider('postgres')
def postgres_loader(
    data_src: DataSourceSpec, context: DocmaRenderContext, params: dict[str, Any] = None, **kwargs
) -> list[dict[str, Any]]:
    """
    Load data from a Postgres database.

    Local passwords should only be used for dev/testing.

    The location component of the data source is a label for the DB used to identify
    environment variables (in .env or the environment) to connect to the DB. If the
    label is XYZ, then the connection vars in .env would be:

    *   XYZ_USER --> user
    *   XYZ_PASSWORD --> password ; or ...
    *   XYZ_PASSWORD_PARAM --> SSM parameter containing password --> passwor
    *   XYZ_HOST --> host
    *   XYZ_PORT --> port
    *   XYZ_DATABASE --> database

    For environment (not .env) versions of these add `DOCMA_` to the front.

    In the HTML for a Vega graph, this would look like this:

    .code::html
        <IMG src="docma:vega?spec=graph.yaml&data=postgres;mydb;myquery.yaml">

    :param data_src:    Data source specification.
    :param context:     Docma rendering context.
    :param params:      Additional rendering parameters when preparing the query.
    :param kwargs:      Keyword argument sponge. Should be empty.

    :return:            A list of data rows (as dicts).

    """

    if not data_src.query:
        raise DocmaDataProviderError('Query is required for "postgres" data source type')

    if kwargs:
        raise DocmaDataProviderError(
            f'Parameters not allowed for "postgres" data source type: {", ".join(kwargs.keys())}'
        )

    try:
        query_spec = DocmaQuerySpecification(
            name=data_src.query, **yaml.safe_load(context.tpkg.read_text(data_src.query))
        )
        query_txt, query_params = query_spec.prepare_query(
            context, params=params, paramstyle=pg8000.paramstyle
        )
    except Exception as e:
        raise DocmaDataProviderError(f'{data_src.query}: {e}') from e

    conn_info = ConnectionInfo(**env_config('DOCMA', data_src.location.upper()))
    # We deliberately don't close connection to allow reuse.
    conn = postgress_connect(conn_info)
    cursor = conn.cursor()

    try:
        cursor.execute(query_txt, query_params)
        return query_spec.fetch_from_cursor(cursor)
    except Exception as e:
        # Attempt a rollback (Mostly required for coverage tests)
        with suppress(Exception):
            conn.rollback()
        raise DocmaDataProviderError(f'{data_src.query}: {e}') from e


# ------------------------------------------------------------------------------
@data_provider('duckdb')
def duckdb_loader(
    data_src: DataSourceSpec, context: DocmaRenderContext, params: dict[str, Any] = None, **kwargs
) -> list[dict[str, Any]]:
    """
    Load data from a DuckDB database.

    In this case the location is a file in the local filesystem within the
    current directory or below it rather than from the document template package.
    This is mostly for dev / test.

    Why duckdb? It has a richer SQL implementation than SQLite3 and it goes like
    the clappers.

    :param data_src:    Data source specification.
    :param context:     Docma rendering context.
    :param params:      Additional rendering parameters when preparing the query.
    :param kwargs:      Keyword argument sponge. Should be empty.

    :return:            A list of data rows (as dicts).

    """

    if not duckdb:
        raise DocmaDataProviderError(
            'duckdb is required for "duckdb" data source type - try "pip install duckdb"'
        )

    if not data_src.query:
        raise DocmaDataProviderError('Query is required for "duckdb" data source type')

    if kwargs:
        raise DocmaDataProviderError(
            f'Parameters not allowed for "duckdb" data source type: {", ".join(kwargs.keys())}'
        )

    dbpath = Path(data_src.location)
    try:
        relative_path(Path('.'), dbpath)
    except ValueError:
        raise DocmaDataProviderError(
            f'DuckDB location not relative to current directory: {data_src.location}'
        )

    try:
        query_spec = DocmaQuerySpecification(
            name=data_src.query, **yaml.safe_load(context.tpkg.read_text(data_src.query))
        )
        query_txt, query_params = query_spec.prepare_query(
            context, params=params, paramstyle=duckdb.paramstyle
        )
        with duckdb.connect(data_src.location, read_only=DUCKDB_READONLY) as conn:
            LOG.info('Connected to DuckDB @ %s', data_src.location)
            conn.execute(query_txt, query_params)
            # Duckdb conn obeys cursor protocol.
            return query_spec.fetch_from_cursor(conn)
    except Exception as e:
        raise DocmaDataProviderError(f'{data_src.query}: {e}') from e


# ------------------------------------------------------------------------------
@cache
def get_lava_db_conn(conn_id: str, realm: str):
    """Get a lava database connection and cache it."""

    def closer():
        """Close the connection atexit."""
        LOG.debug('Closing lava connection %s @ %s', conn_id, realm)
        try:
            conn.close()
        except Exception as _e:
            LOG.warning('Failed to close lava connection %s @ %s : %s', conn_id, realm, _e)

    LOG.debug('Connecting via lava to %s @ %s', conn_id, realm)
    try:
        conn = get_pysql_connection(conn_id=conn_id, realm=realm)
    except Exception as e:
        raise DocmaDataProviderError(f'Lava connection error: {conn_id}: {e}') from e
    LOG.info('Connected via lava to %s @ %s', conn_id, realm)
    atexit.register(closer)
    return conn


# ------------------------------------------------------------------------------
@data_provider('lava')
def lava_loader(
    data_src: DataSourceSpec, context: DocmaRenderContext, params: dict[str, Any] = None, **kwargs
) -> list[dict[str, Any]]:
    """
    Load data via a lava connector.

    In this case the location is the lava conn_id. Connections are cached and
    reused.

    :param data_src:    Data source specification.
    :param context:     Docma rendering context.
    :param params:      Additional rendering parameters when preparing the query.
    :param kwargs:      Keyword argument sponge. Should be empty.

    :return:            A list of data rows (as dicts).

    """

    if not get_pysql_connection:
        raise DocmaDataProviderError(
            'jinlava is required for "lava" data source type - try "pip install jinlava"'
        )

    if not data_src.query:
        raise DocmaDataProviderError('Query is required for "lava" data source type')

    if kwargs:
        raise DocmaDataProviderError(
            f'Parameters not allowed for "lava" data source type: {", ".join(kwargs.keys())}'
        )

    try:
        realm = os.environ['LAVA_REALM']
    except KeyError:
        raise DocmaDataProviderError('Realm must be set for "lava" data source type')

    conn = get_lava_db_conn(conn_id=data_src.location, realm=realm)

    try:
        query_spec = DocmaQuerySpecification(
            name=data_src.query, **yaml.safe_load(context.tpkg.read_text(data_src.query))
        )
        query_txt, query_params = query_spec.prepare_query(
            context, params=params, paramstyle=get_paramstyle_from_conn(conn)
        )
        cursor = conn.cursor()
        cursor.execute(query_txt, query_params)
        return query_spec.fetch_from_cursor(cursor)
    except Exception as e:
        # Attempt a rollback (Mostly required for coverage tests)
        with suppress(Exception):
            conn.rollback()
        raise DocmaDataProviderError(f'{data_src.query}: {e}') from e
