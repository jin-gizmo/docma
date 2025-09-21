"""Test Australian industry ID format checkers."""

from __future__ import annotations

import jsonschema
import pytest  # noqa
from jsonschema import ValidationError

from docma.lib.jsonschema import FORMAT_CHECKER
from docma.plugins.format_checkers.au.industry_formats import *

test_data = [
    # ----------------------------------------
    # NMI ✅
    (is_nmi, 'au.nmi', '4123456789', True),
    (is_nmi, 'Au.NMI', '4123456789', True),  # Case insensitive plugin names
    # NMI ❌
    (is_nmi, 'au.NMI', '5123456789', False),  # NMIs don't start with 5
    (is_nmi, 'au.NMI', '412345678', False),  # NMIs are 10 characters long
    # ----------------------------------------
    # MIRN ✅
    (is_mirn, 'au.MIRN', '5123456789', True),
    # MIEN ❌
    (is_mirn, 'au.MIRN', '4123456789', False),  # MIRNs start with 5
    (is_mirn, 'au.MIRN', '512345678', False),  # MIRNs are 10 characters long
]


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('func, format_, value, expected', test_data)
def test_format_checkers_au_industry_ids_direct(func, format_, value, expected):
    """Test the checker by direct invocation."""
    assert func(value) is expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('func, format_, value, expected', test_data)
def test_format_checkers_au_industry_ids_jsonschema(func, format_, value, expected):
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
