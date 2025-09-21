"""Babel-based decimal / percent filters."""

from __future__ import annotations

from typing import Callable

from babel.numbers import decimal, format_compact_decimal, format_decimal, format_percent
from jinja2 import pass_context, runtime

from docma.jinja.utils import get_context_var
from docma.lib.plugin import jfilter

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@jfilter('decimal')
@pass_context
def decimal_filter(*args, **kwargs) -> str:
    """Provide a thin pass-thru to babel format_decimal()."""
    return _number_filter(format_decimal, *args, **kwargs)


# ------------------------------------------------------------------------------
@jfilter('compact_decimal')
@pass_context
def compact_decimal_filter(*args, **kwargs) -> str:
    """Provide a thin pass-thru to babel format_compact_decimal()."""
    return _number_filter(format_compact_decimal, *args, **kwargs)


# # ------------------------------------------------------------------------------
@jfilter('percent')
@pass_context
def percent_filter(*args, **kwargs) -> str:
    """Provide a thin pass-thru to babel format_percent()."""
    return _number_filter(format_percent, *args, **kwargs)


# ------------------------------------------------------------------------------
def _number_filter(
    formatter: Callable,
    ctx: runtime.Context,
    value: str | int | float,
    *args,
    rounding: str = 'half-up',
    default: int | float | str | None = None,
    **kwargs,
) -> str:
    """
    Provide a thin pass-thru to a babel number formatter.

    :param formatter:   A babel formatter that matches the signature of
                        format_decimal().
    :param ctx:         The Jinja context.
    :param value:       The value to be formatted.
    :param rounding:    How to round the value. This must be one of the
                        rounding modes decimal.ROUND_*, with the `ROUND_`
                        prefix removed. Case insensitive and hyphens become
                        underscores. Defaults to 'half-up' (Excel style
                        rounding), instead of `half-even` (Bankers rounding)
                        which is Python's normal default.
    :param default:     The default value to use for the filter if the value is
                        empty (i.e. None or an empty string). If value is empty
                        and default is a string, the default is used as-is as
                        the the return value. If value is wmpty and default is
                        not specified, a ValueError is raised.  Otherwise, the
                        default is assumed to be numberic and is used as the
                        input to the filter.
    :param args:        Passed to the babel formatter.
    :param kwargs:      Passed to the babel formatter.

    """

    if value in (None, ''):
        if default is None:
            raise ValueError('Value is empty and no default specified')
        if isinstance(default, str):
            return default
        value = default

    rounding_mode = f'ROUND_{rounding.upper().replace("-", "_")}'
    try:
        r = getattr(decimal, rounding_mode)
    except AttributeError:
        raise ValueError(f'Unknown rounding mode: {rounding}')

    ctx_locale = get_context_var(ctx, 'locale')
    with decimal.localcontext(rounding=r):
        return formatter(value, *args, **({'locale': ctx_locale} | kwargs))
