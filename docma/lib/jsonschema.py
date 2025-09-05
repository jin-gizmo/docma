"""JSONschema utilities."""

from __future__ import annotations

import re
from datetime import datetime
from itertools import product

import jsonschema

FORMAT_CHECKER = jsonschema.FormatChecker()

ABN_WEIGHTS = (10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19)
ACN_WEIGHTS = (8, 7, 6, 5, 4, 3, 2, 1)

UNIT_SCALE_FACTORS = ('', 'k', 'M', 'G', 'T')
ENERGY_UNITS = [
    scale + unit for scale, unit in product(UNIT_SCALE_FACTORS, ('J', 'Wh', 'VArh', 'VAh'))
]
POWER_UNITS = [scale + unit for scale, unit in product(UNIT_SCALE_FACTORS, ('W', 'VAr', 'VA'))]

# See https://semver.org.
SEMVER_RE = re.compile(
    r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)'
    r'(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][\da-zA-Z-]*)'
    r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][\da-zA-Z-]*))*))'
    r'?(?:\+(?P<buildmetadata>[\da-zA-Z-]+(?:\.[\da-zA-Z-]+)*))?$'
)


# ------------------------------------------------------------------------------
@FORMAT_CHECKER.checks('NMI', raises=(ValueError,))
def is_nmi(value: str) -> bool:
    """Check if a string is a 10 digit NMI (no checksum)."""
    if not isinstance(value, str):
        raise ValueError(f'NMIs are strings not {type(value)}')

    if len(value) != 10:
        raise ValueError('NMIs are 10 characters long')

    if value[0] == '5':
        raise ValueError('NMIs don\'t start with 5, MIRNs do')

    return True


# ------------------------------------------------------------------------------
@FORMAT_CHECKER.checks('MIRN', raises=(ValueError,))
def is_mirn(value: str) -> bool:
    """Check if a string is a 10 digit MIRN (no checksum)."""
    if not isinstance(value, str):
        raise ValueError(f'MIRNs are strings not {type(value)}')

    if len(value) != 10:
        raise ValueError('MIRNs are 10 characters long')

    if value[0] != '5':
        raise ValueError('MIRNs must start with 5')

    return True


# ------------------------------------------------------------------------------
@FORMAT_CHECKER.checks('ABN', raises=(ValueError,))
def is_abn(value: str) -> bool:
    """Check if a string is a valid ABN."""

    if isinstance(value, int):
        value = str(value)
    digits = [int(c) for c in value if c != ' ']
    if len(digits) != 11:
        raise ValueError('ABNs are 11 digits long')
    digits[0] -= 1
    return sum(d * w for d, w in zip(digits, ABN_WEIGHTS)) % 89 == 0


# ------------------------------------------------------------------------------
@FORMAT_CHECKER.checks('ACN', raises=(ValueError,))
def is_acn(value: str | int) -> bool:
    """Check if a string is a valid ABN."""

    if isinstance(value, int):
        value = str(value)
    digits = [int(c) for c in value if c != ' ']
    if len(digits) != 9:
        raise ValueError('ACNs are 9 digits long')
    remainder = sum(d * w for d, w in zip(digits, ACN_WEIGHTS)) % 10
    return (10 - remainder) % 10 == digits[-1]


# ------------------------------------------------------------------------------
@FORMAT_CHECKER.checks('DD/MM/YYYY', raises=(ValueError,))
def is_date_ddmmyyyy(value: str) -> bool:
    """Check if a string is a valid date in the form DD/MM/YYYY."""
    datetime.strptime(value, '%d/%m/%Y')
    return True


# ------------------------------------------------------------------------------
@FORMAT_CHECKER.checks('energy_unit', raises=(ValueError,))
def is_energy_unit(value: str) -> bool:
    """Check if a unit of measure is a valid energy unit."""
    return value in ENERGY_UNITS


# ------------------------------------------------------------------------------
@FORMAT_CHECKER.checks('power_unit', raises=(ValueError,))
def is_power_unit(value: str) -> bool:
    """Check if a unit of measure is a valid power unit."""
    return value in POWER_UNITS


# ------------------------------------------------------------------------------
@FORMAT_CHECKER.checks('semantic_version')
def is_semantic_version(value: str) -> bool:
    """Check if a string is a valid semantic version as per https://semver.org."""
    return bool(SEMVER_RE.match(value))
