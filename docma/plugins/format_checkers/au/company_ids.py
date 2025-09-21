"""Depreecated format checkers that have been renamed."""

from docma.lib.jsonschema import format_checker

__author__ = 'Murray Andrews'


ABN_WEIGHTS = (10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19)
ACN_WEIGHTS = (8, 7, 6, 5, 4, 3, 2, 1)


# ------------------------------------------------------------------------------
@format_checker('ABN')
def is_abn(value: str) -> bool:
    """Check if a string is a valid ABN."""

    print('FROG', type(value))
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
@format_checker('ACN')
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
