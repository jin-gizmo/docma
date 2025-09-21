"""
Dollars filter.

This one is not actually deprecated (yet) but it probably could be. It's a bit
of a lazy, non-locale-aware approach that was originally done as a quick and
dirty. The Babel-bsed currency filter is the preferred approach.
"""

__author__ = 'Murray Andrews'

from decimal import Decimal, ROUND_HALF_UP

from docma.lib.plugin import jfilter


@jfilter('dollars')
def _dollars(value: str | int | float, precision: int = 2, symbol: str = '$') -> str:
    """
    Format dollars using round up not bankers rounding.

    .. deprecated:: 2.1.0
        Use the country specific filters instead (e.g. au.currency).
    """

    rounded = Decimal(str(value)).quantize(Decimal(f'0.{precision * "0"}'), ROUND_HALF_UP)
    return f'{symbol or ""}{rounded:,}'
