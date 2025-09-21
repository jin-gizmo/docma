"""
Test date format checkers.

The date formats are handled by a resolver so no direct function tests, which is
fine.
"""

from __future__ import annotations

import jsonschema
import pytest  # noqa
from jinja2 import Environment
from jsonschema import ValidationError

from docma.lib.jsonschema import FORMAT_CHECKER

# Keeping same test data structure as other checker tests. Hence initial None.
test_data = [
    # ----------------------------------------
    # date.dmy ✅
    (None, 'date.dmy', '17/3/2024', True),
    (None, 'date.dmy', '17-3-2024', True),
    (None, 'date.dmy', '17-03-2024', True),
    (None, 'date.dmy', '17.03.2024', True),
    (None, 'date.dmy', '17/3/2024', True),
    (None, 'date.dmy', '17032024', True),
    (None, 'date.dmy', 17032024, True),  # int is dodgy but we allow it
    # date.dmy ❌
    (None, 'date.dmy', '31/2/2024', False),
    (None, 'date.dmy', '2024/10/20', False),
    # ----------------------------------------
    # date.ymd ✅
    (None, 'date.ymd', '2024/03/17', True),
    (None, 'date.ymd', '20240317', True),
    # ----------------------------------------
    # date.ymd ❌
    (None, 'date.ymd', '2024/17/03', False),
    # ----------------------------------------
    # date.mdy ✅
    (None, 'date.mdy', '3/17/2024', True),
    # ----------------------------------------
    # date.mdy ❌
    (None, 'date.mdy', '17/03/2024', False),
]


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('func, format_, value, expected', test_data)
def test_format_checkers_date_jsonschema(func, format_, value, expected):
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


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('func, format_, value, expected', test_data)
def test_format_checkers_date_jinja_test(func, format_, value, expected, jtests):
    """Test the checker Test when used as a jinja test."""

    env = Environment()
    env.tests = jtests

    template = f'{{{{ value is {format_} }}}}'
    assert env.from_string(template).render(value=value) == str(expected)


# ------------------------------------------------------------------------------
def test_format_checkers_date_unknown():
    """Test the checker with unknown format."""
    schema = {
        'type': 'string',
        'format': 'date.unknown'
    }
    with pytest.raises(KeyError, match='Unknown format'):
        jsonschema.validate('does not matter', schema, format_checker=FORMAT_CHECKER)
