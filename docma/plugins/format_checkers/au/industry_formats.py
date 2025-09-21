"""Format checkers for industry specific formats."""

from docma.lib.jsonschema import format_checker

__author__ = 'Murray Andrews'


ABN_WEIGHTS = (10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19)
ACN_WEIGHTS = (8, 7, 6, 5, 4, 3, 2, 1)


# ------------------------------------------------------------------------------
@format_checker('NMI')
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
@format_checker('MIRN')
def is_mirn(value: str) -> bool:
    """Check if a string is a 10 digit MIRN (no checksum)."""

    return all(
        (
            isinstance(value, str),
            len(value) == 10,
            value[0] == '5',
        )
    )
