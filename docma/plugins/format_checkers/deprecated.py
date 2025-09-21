"""Depreecated format checkers that have been renamed."""

from contextlib import suppress
from datetime import datetime

from docma.lib.jsonschema import format_checker

__author__ = 'Murray Andrews'


ABN_WEIGHTS = (10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19)
ACN_WEIGHTS = (8, 7, 6, 5, 4, 3, 2, 1)


# ------------------------------------------------------------------------------
@format_checker('NMI', deprecation='Use au.NMI instead.')
def is_nmi(value: str) -> bool:
    """Check if a string is a 10 digit NMI (no checksum)."""
    return all(
        (
            isinstance(value, str),
            len(value) == 10,
            value[0] != '5',  # MIRNs start with 5
        )
    )


# ------------------------------------------------------------------------------
@format_checker('MIRN', deprecation='Use au.MIRN instead.')
def is_mirn(value: str) -> bool:
    """Check if a string is a 10 digit MIRN (no checksum)."""

    return all(
        (
            isinstance(value, str),
            len(value) == 10,
            value[0] == '5',
        )
    )


# ------------------------------------------------------------------------------
@format_checker('ABN', deprecation='Use au.ABN instead.')
def is_abn(value: str) -> bool:
    """Check if a string is a valid ABN."""

    if isinstance(value, int):
        value = str(value)
    try:
        digits = [int(c) for c in value if c != ' ']
    except ValueError:
        return False
    if len(digits) != 11:
        return False
    digits[0] -= 1
    return sum(d * w for d, w in zip(digits, ABN_WEIGHTS)) % 89 == 0


# ------------------------------------------------------------------------------
@format_checker('ACN', deprecation='Use au.ACN instead.')
def is_acn(value: str | int) -> bool:
    """Check if a string is a valid ABN."""

    if isinstance(value, int):
        value = str(value)
    try:
        digits = [int(c) for c in value if c != ' ']
    except ValueError:
        return False
    if len(digits) != 9:
        return False
    remainder = sum(d * w for d, w in zip(digits, ACN_WEIGHTS)) % 10
    return (10 - remainder) % 10 == digits[-1]


# ------------------------------------------------------------------------------
# jsonschema is not fussy but Jinja tests don't like / in names so alias _dmy
# is for testing.
@format_checker('DD/MM/YYYY', '_dmy', deprecation='Use "date.dmy" instead.')
def is_date_ddmmyyyy(value: str) -> bool:
    """Check if a string is a valid date in the form DD/MM/YYYY."""
    for sep in '', '/', '_', '.', '-':
        with suppress(ValueError):
            datetime.strptime(value, f'%d{sep}%m{sep}%Y')
            return True
    else:
        return False
