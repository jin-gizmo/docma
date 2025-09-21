"""General utility Jinja filters."""

from __future__ import annotations

import re
from typing import Any

from docma.lib.misc import css_id as _css_id
from docma.lib.plugin import jfilter

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@jfilter('css_id')
def css_id(value: str) -> str:
    """Sanitise a string to be a valid CSS identifier."""

    return _css_id(value)


# ------------------------------------------------------------------------------
@jfilter('sql_safe')
def sql_safe(value: str) -> str:
    """
    Ensure a string is a safe SQL identifier.

    We accept "name" and "name.name" forms so it will also work on basic numbers
    where needed.

    This takes a very restrictive view on what is safe and will rule out some
    valid names but what is allowed is safe.
    """

    if not re.match(r'^\w+(\.\w+)?$', value):
        raise ValueError(f'Bad SQL name: {value}')

    return value


# ------------------------------------------------------------------------------
@jfilter('require')
def require(value: Any, message: str):
    """Ensure a value is specified."""

    if not value:
        raise Exception(message)
    return value
