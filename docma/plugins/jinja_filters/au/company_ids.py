"""Jinja2 filters for formatting Australian company IDs."""

from __future__ import annotations

from docma.lib.plugin import jfilter

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@jfilter('ABN')
def abn(value: str) -> str:
    """Format an ABN."""

    v = value.replace(' ', '')
    if len(v) != 11:
        raise ValueError(f'Bad ABN: {value}')
    return ' '.join([v[:2]] + [v[n : n + 3] for n in range(2, 11, 3)])


# ------------------------------------------------------------------------------
@jfilter('ACN')
def acn(value: str) -> str:
    """Format an ACN."""
    v = value.replace(' ', '')
    if len(v) != 9:
        raise ValueError(f'Bad ACN: {value}')
    return ' '.join(v[n : n + 3] for n in range(0, 9, 3))
