"""Tests for docma.lib.db."""

from __future__ import annotations

import duckdb
import pg8000

from docma.lib.db import *


# ------------------------------------------------------------------------------
def test_get_paramstyle_from_conn_pg8000(tc, env):
    conn_info = {
        param: env[f'{tc.postgres.id}_{param}'.upper()]
        for param in ('host', 'port', 'database', 'user', 'password', 'database')
    }
    with pg8000.connect(**conn_info) as conn:
        assert get_paramstyle_from_conn(conn) == pg8000.paramstyle


# ------------------------------------------------------------------------------
def test_get_paramstyle_from_conn_duckdb(tc):
    with duckdb.connect() as conn:
        assert get_paramstyle_from_conn(conn) == duckdb.paramstyle
