"""DB utilities."""

from __future__ import annotations

import inspect
from importlib import import_module


# ------------------------------------------------------------------------------
def get_paramstyle_from_conn(conn) -> str:
    """
    Hack to get the DBAPI paramstyle from a database connection in a driver independent way.

    DBAPI 2.0 implementations show very little consistency. Dodgy as. Works for
    a few of the common ones.
    """

    db_module = inspect.getmodule(conn.__class__)
    base_module_name, *_ = db_module.__name__.split('.', 1)
    base_db_module = import_module(base_module_name)
    return base_db_module.paramstyle
