"""Test Australian company ID format checkers."""

from __future__ import annotations

import jsonschema
import pytest  # noqa
from jsonschema import ValidationError

from docma.lib.jsonschema import FORMAT_CHECKER
from docma.plugins.format_checkers.au.company_ids import *

test_data = [
    # ----------------------------------------
    # ABN ✅
    (is_abn, 'au.ABN', '51 824 753 556', True),
    (is_abn, 'au.ABN', '70 326 883 043', True),
    (is_abn, 'au.abn', '51   824 753 556  ', True),
    (is_abn, 'au.Abn', '51824753556', True),
    (is_abn, 'au.abn', 51824753556, True),  # int
    (is_abn, 'au.ABN', '58 896 144 542', True),
    (is_abn, 'au.ABN', '21 582 637 628', True),
    (is_abn, 'au.ABN', '70 138 591 901', True),
    (is_abn, 'au.ABN', '21 047 727 425', True),
    (is_abn, 'au.ABN', '11 283 251 728', True),
    (is_abn, 'au.ABN', '94 135 025 341', True),
    # ABN ❌
    (is_abn, 'au.ABN', '41 824 753 556', False),
    (is_abn, 'au.ABN', '1 824 753 556', False),  # ABNs are 11 digits
    (is_abn, 'au.ABN', '+1 824 753 556', False),  # Non int char
    # ----------------------------------------
    # ACN ✅
    (is_acn, 'au.acn', '000 000 019', True),
    (is_acn, 'au.Acn', '000000019', True),
    (is_acn, 'au.ACN', '000   000019', True),
    (is_acn, 'au.ACN', '000 250 000', True),
    (is_acn, 'au.ACN', '000 500 005', True),
    (is_acn, 'au.ACN', '000 750 005', True),
    (is_acn, 'au.ACN', '001 000 004', True),
    (is_acn, 'au.ACN', '001 250 004', True),
    (is_acn, 'au.ACN', '001 500 009', True),
    (is_acn, 'au.ACN', '001 749 999', True),
    (is_acn, 'au.ACN', '001 999 999', True),
    (is_acn, 'au.ACN', '002 249 998', True),
    (is_acn, 'au.ACN', '002 499 998', True),
    (is_acn, 'au.ACN', '002 749 993', True),
    # ACN ❌
    (is_acn, 'au.ACN', '102 749 993', False),
    (is_acn, 'au.ACN', 102749993, False),
    (is_acn, 'au.ACN', '00 000 019', False),  # ACNs are 9 digits
    (is_acn, 'au.ACN', '+00 000 019', False),  # Non int char
]


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('func, format_, value, expected', test_data)
def test_json_format_checkers_au_company_ids_direct(func, format_, value: str | int, expected):
    """Test the checker by direct invocation."""
    assert func(value) is expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('func, format_, value, expected', test_data)
def test_json_format_checkers_au_company_ids_jsonschema(func, format_, value: str | int, expected):
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
