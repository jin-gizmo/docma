"""Test general utility format checkers."""

from __future__ import annotations

import jsonschema
import pytest  # noqa
from jinja2 import Environment
from jsonschema import ValidationError

from docma.lib.jsonschema import FORMAT_CHECKER
from docma.plugins.format_checkers.utility import *

test_data = [
    # ----------------------------------------
    # Energy unit ✅
    (is_energy_unit, 'energy_unit', 'J', True),
    (is_energy_unit, 'energy_unit', 'kJ', True),
    (is_energy_unit, 'energy_unit', 'MWh', True),
    (is_energy_unit, 'energy_unit', 'GVArh', True),
    # Energy unit ❌
    (is_energy_unit, 'energy_unit', 'KJ', False),
    (is_energy_unit, 'energy_unit', 'MW', False),
    (is_energy_unit, 'energy_unit', 'GVA', False),
    # ----------------------------------------
    # Power unit ✅
    (is_power_unit, 'power_unit', 'W', True),
    (is_power_unit, 'power_unit', 'kW', True),
    (is_power_unit, 'power_unit', 'MW', True),
    (is_power_unit, 'power_unit', 'GVA', True),
    # Power unit ❌
    (is_power_unit, 'power_unit', 'J', False),
    (is_power_unit, 'power_unit', 'MWh', False),
    (is_power_unit, 'power_unit', 'GVAh', False),
    # ----------------------------------------
    # Semantic version ✅
    (is_semantic_version, 'semantic_version', '1.0.0', True),
    (is_semantic_version, 'semantic_version', '10.20.30', True),
    # Semantic version ❌
    (is_semantic_version, 'semantic_version', '1.0', False),
    (is_semantic_version, 'semantic_version', 'Wotcha', False),
    # ----------------------------------------
    # Locale ✅
    (is_locale, 'locale', 'en', True),
    (is_locale, 'locale', 'en_AU', True),
    (is_locale, 'locale', 'fr', True),
    (is_locale, 'locale', 'fr_FR', True),
    # Locale ❌
    (is_locale, 'locale', 'en-AU', False),  # Underscores, not dashes
    (is_locale, 'locale', 'woop_woop', False),
]


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('func, format_, value, expected', test_data)
def test_format_checkers_utility_direct(func, format_, value, expected):
    """Test the checker by direct invocation."""

    # This will not trigger a deprecation warning as deprecation is not handled
    # at the format checker function level.
    assert func(value) is expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('func, format_, value, expected', test_data)
def test_format_checkers_utility_jsonschema(func, format_, value, expected):
    """Test the checker via jsonschema validation process."""

    schema = {
        'type': 'string',
        'format': format_,
    }

    if expected:
        # This will raise a jsonschema.FormatError if it fails so no assert needed.
        jsonschema.validate(str(value), schema, format_checker=FORMAT_CHECKER)
    else:
        with pytest.raises(ValidationError):
            jsonschema.validate(str(value), schema, format_checker=FORMAT_CHECKER)


@pytest.mark.parametrize('func, format_, value, expected', test_data)
def test_format_checkers_utility_jinja_test(func, format_, value, expected, jtests):
    """Test the checker Test when used as a jinja test."""

    env = Environment()
    env.tests = jtests

    template = f'{{{{ value is {format_} }}}}'
    assert env.from_string(template).render(value=value) == str(expected)
