"""Test deprecated format checkers."""

from __future__ import annotations

import jsonschema
import pytest  # noqa
from jinja2 import Environment
from jsonschema import ValidationError

from docma.lib.jsonschema import (
    JsonSchemaBuiltinsResolver,
    PluginFormatChecker,
)
from docma.lib.plugin import PLUGIN_JSONSCHEMA_FORMAT, PackageResolver
from docma.plugins.format_checkers.deprecated import *

test_data = [
    # ----------------------------------------
    # ABN ✅
    (is_abn, 'ABN', '51 824 753 556', True),
    (is_abn, 'ABN', '70 326 883 043', True),
    (is_abn, 'abn', '51   824 753 556  ', True),
    (is_abn, 'Abn', '51824753556', True),
    (is_abn, 'abn', 51824753556, True),  # int
    (is_abn, 'ABN', '58 896 144 542', True),
    (is_abn, 'ABN', '21 582 637 628', True),
    (is_abn, 'ABN', '70 138 591 901', True),
    (is_abn, 'ABN', '21 047 727 425', True),
    (is_abn, 'ABN', '11 283 251 728', True),
    (is_abn, 'ABN', '94 135 025 341', True),
    # ABN ❌
    (is_abn, 'ABN', '41 824 753 556', False),
    (is_abn, 'ABN', '1 824 753 556', False),  # ABNs are 11 digits
    (is_abn, 'ABN', '+1 824 753 556', False),  # Non int char
    # ----------------------------------------
    # ACN ✅
    (is_acn, 'acn', '000 000 019', True),
    (is_acn, 'Acn', '000000019', True),
    (is_acn, 'ACN', '000   000019', True),
    (is_acn, 'ACN', '000 250 000', True),
    (is_acn, 'ACN', '000 500 005', True),
    (is_acn, 'ACN', '000 750 005', True),
    (is_acn, 'ACN', '001 000 004', True),
    (is_acn, 'ACN', '001 250 004', True),
    (is_acn, 'ACN', '001 500 009', True),
    (is_acn, 'ACN', '001 749 999', True),
    (is_acn, 'ACN', '001 999 999', True),
    (is_acn, 'ACN', '002 249 998', True),
    (is_acn, 'ACN', '002 499 998', True),
    (is_acn, 'ACN', '002 749 993', True),
    # ACN ❌
    (is_acn, 'ACN', '102 749 993', False),
    (is_acn, 'ACN', 102749993, False),
    (is_acn, 'ACN', '00 000 019', False),  # ACNs are 9 digits
    (is_acn, 'ACN', '+00 000 019', False),  # Non int char
    # ----------------------------------------
    # NMI ✅
    (is_nmi, 'NMI', '4123456789', True),
    (is_nmi, 'nmi', '4123456789', True),  # Case insensitive plugin names
    # NMI ❌
    (is_nmi, 'NMI', '5123456789', False),  # NMIs don't start with 5
    (is_nmi, 'NMI', '412345678', False),  # NMIs are 10 characters long
    # ----------------------------------------
    # MIRN ✅
    (is_mirn, 'MIRN', '5123456789', True),
    # MIRN ❌
    (is_mirn, 'mirn', '4123456789', False),  # MIRNs start with 5
    (is_mirn, 'MIRN', '512345678', False),  # MIRNs are 10 characters long
    # ----------------------------------------
    # jsonschema is not fussy but Jinja tests don't like / in names so alias / with _
    # DD/MM/YYYY ✅
    (is_date_ddmmyyyy, '_dmy', '1/3/2024', True),
    (is_date_ddmmyyyy, '_dmy', '1-3-2024', True),
    (is_date_ddmmyyyy, '_dmy', '01-03-2024', True),
    (is_date_ddmmyyyy, '_dmy', '01/3/2024', True),
    (is_date_ddmmyyyy, '_dmy', '0132024', True),
    (is_date_ddmmyyyy, '_dmy', '01032024', True),
    # DD/MM/YYYY ❌
    (is_date_ddmmyyyy, '_dmy', '31/2/2024', False),
    (is_date_ddmmyyyy, '_dmy', '2024/10/20', False),
]


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('func, format_, value, expected', test_data)
def test_json_format_checkers_deprecated_direct(func, format_, value, expected):
    """Test the checker by direct invocation."""

    # This will not trigger a deprecation warning as deprecation is not handled
    # at the format checker function level.
    assert func(value) is expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('func, format_, value, expected', test_data)
def test_json_format_checkers_deprecated_jsonschema(func, format_, value, expected):
    """Check the checker via jsonschema validation process."""

    schema = {
        'type': 'string',
        'format': format_,
    }

    # Have to create a new PluginFormatChecker for each test to reset the warning
    # duplication prevention cache.
    checker = PluginFormatChecker(
        resolvers=[
            JsonSchemaBuiltinsResolver(),
            PackageResolver('docma.plugins.format_checkers', PLUGIN_JSONSCHEMA_FORMAT),
        ]
    )
    with pytest.warns(DeprecationWarning, match=f'Plugin {format_} is deprecated.'):
        if expected:
            # This will raise a jsonschema.FormatError if it fails so no assert needed.
            jsonschema.validate(str(value), schema, format_checker=checker)
        else:
            with pytest.raises(ValidationError):
                jsonschema.validate(str(value), schema, format_checker=checker)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('func, format_, value, expected', test_data)
def test_format_checkers_date_jinja_test(func, format_, value, expected, jtests):
    """Test the checker Test when used as a jinja test."""

    env = Environment()
    env.tests = jtests

    template = f'{{{{ value is {format_} }}}}'
    with pytest.warns(DeprecationWarning, match=f'Plugin {format_} is deprecated.'):
        assert env.from_string(template).render(value=value) == str(expected)
