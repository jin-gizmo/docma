"""Babel-based datetime filters for formatting, parsing etc."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Callable

from babel.dates import (
    format_date,
    format_datetime,
    format_time,
    format_timedelta,
    parse_date,
    parse_time,
)
from jinja2 import pass_context, runtime

from docma.jinja.utils import get_context_var
from docma.lib.plugin import jfilter

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@jfilter('date')
@pass_context
def date_filter(*args, **kwargs) -> str:
    """Provide a thin pass-thru to babel format_date()."""
    return _datetime_filter(format_date, *args, **kwargs)


# ------------------------------------------------------------------------------
@jfilter('datetime')
@pass_context
def datetime_filter(*args, **kwargs) -> str:
    """Provide a thin pass-thru to babel format_date()."""
    return _datetime_filter(format_datetime, *args, **kwargs)


# ------------------------------------------------------------------------------
@jfilter('time')
@pass_context
def time_filter(*args, **kwargs) -> str:
    """Provide a thin pass-thru to babel format_date()."""
    return _datetime_filter(format_time, *args, **kwargs)


# ------------------------------------------------------------------------------
@jfilter('timedelta')
@pass_context
def timedelta_filter(*args, **kwargs) -> str:
    """Provide a thin pass-thru to babel format_date()."""
    return _datetime_filter(format_timedelta, *args, **kwargs)


# ------------------------------------------------------------------------------
def _datetime_filter(
    formatter: Callable,
    ctx: runtime.Context,
    value: date | datetime | time | timedelta,
    *args,
    **kwargs,
) -> str:
    """
    Provide a thin pass-thru to a babel datetime formatter.

    :param formatter:   A babel formatter.
    :param ctx:         The Jinja context.
    :param value:       The value to be formatted.
    :param args:        Passed to the babel formatter.
    :param kwargs:      Passed to the babel formatter.

    """

    ctx_locale = get_context_var(ctx, 'locale')
    return formatter(value, *args, **({'locale': ctx_locale} | kwargs))


# ------------------------------------------------------------------------------
@jfilter('parse_date')
@pass_context
def parse_date_filter(ctx: runtime.Context, value: str, *args, **kwargs) -> date:
    """
    Provide a thin pass-thru to babel parse_date().

    :param ctx:         The Jinja context.
    :param value:       The value to be parsed.
    :param args:        Passed to the babel formatter.
    :param kwargs:      Passed to the babel formatter.
    """

    ctx_locale = get_context_var(ctx, 'locale')
    return parse_date(value, *args, **({'locale': ctx_locale} | kwargs))


# ------------------------------------------------------------------------------
@jfilter('parse_time')
@pass_context
def parse_time_filter(ctx: runtime.Context, value: str, *args, **kwargs) -> time:
    """
    Provide a thin pass-thru to babel parse_time().

    :param ctx:         The Jinja context.
    :param value:       The value to be parsed.
    :param args:        Passed to the babel formatter.
    :param kwargs:      Passed to the babel formatter.
    """

    ctx_locale = get_context_var(ctx, 'locale')
    return parse_time(value, *args, **({'locale': ctx_locale} | kwargs))
