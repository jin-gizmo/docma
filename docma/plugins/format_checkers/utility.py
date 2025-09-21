"""General utility format checkers."""

import re
from itertools import product

from babel.localedata import locale_identifiers  # noqa

from docma.lib.jsonschema import format_checker

__author__ = 'Murray Andrews'


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
@format_checker('energy_unit')
def is_energy_unit(value: str) -> bool:
    """Check if a unit of measure is a valid energy unit."""
    return value in ENERGY_UNITS


# ------------------------------------------------------------------------------
@format_checker('power_unit')
def is_power_unit(value: str) -> bool:
    """Check if a unit of measure is a valid power unit."""
    return value in POWER_UNITS


# ------------------------------------------------------------------------------
@format_checker('semantic_version')
def is_semantic_version(value: str) -> bool:
    """Check if a string is a valid semantic version as per https://semver.org."""
    return bool(SEMVER_RE.match(value))


# ------------------------------------------------------------------------------
@format_checker('locale')
def is_locale(value: str) -> bool:
    """Check if a string is a valid locale (as defined in Babel)."""
    return value in locale_identifiers()
