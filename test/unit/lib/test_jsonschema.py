"""
Tests for docma.lib.jsonschema.

Most of this is exercised by the tests that exercises the format checker plugins.
Just need to pick up some generic edge cases here.

"""

from __future__ import annotations

import jsonschema
import pytest  # noqa
from jsonschema import ValidationError

from docma.lib.jsonschema import FORMAT_CHECKER

# Test data for checking we haven't broken the jsonschema builtins.
test_data = [
    # Miscellaneous builtins ✅
    ('email', 'x@gmail.com', True),
    ('ipv4', '127.0.0.1', True),
    # Miscellaneous builtins ❌
    ('email', 'not-an-email', False),
    ('ipv4', '10.20.30.257', False),
]

# ------------------------------------------------------------------------------
@pytest.mark.parametrize('format_, value, expected', test_data)
def test_json_format_checkers_builtin_jsonschema(format_, value, expected):
    """Check the checker via jsonschema validation process."""

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
def test_unknown_jsonformat_checker():
    schema = {
        'type': 'string',
        'format': 'xx_unknown',
    }
    with pytest.raises(KeyError, match="Unknown format 'xx_unknown'"):
        jsonschema.validate('whatever', schema, format_checker=FORMAT_CHECKER)
