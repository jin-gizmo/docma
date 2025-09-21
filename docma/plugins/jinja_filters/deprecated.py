"""Legacy (deprecated) Jinja filter."""

from docma.lib.plugin import jfilter

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@jfilter('ABN', deprecation='Use "au.ABN" instead.')
def _abn(value: str) -> str:
    """
    Format an ABN.

    .. deprecated:: 2.1.0
        Use au.abn (or au.ABN) instead.
    """

    v = value.replace(' ', '')
    if len(v) != 11:
        raise ValueError(f'Bad ABN: {value}')
    return ' '.join([v[:2]] + [v[n : n + 3] for n in range(2, 11, 3)])


# ------------------------------------------------------------------------------
@jfilter('ACN', deprecation='Use "au.ACN" instead.')
def _acn(value: str) -> str:
    """
    Format an ACN.

    .. deprecated:: 2.1.0
        Use au.acn (or au.ACN) instead.
    """

    v = value.replace(' ', '')
    if len(v) != 9:
        raise ValueError(f'Bad ACN: {value}')
    return ' '.join(v[n : n + 3] for n in range(0, 9, 3))
