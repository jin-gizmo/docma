"""Tests for docma.lib.jsonschema."""

from __future__ import annotations

import pytest

from docma.lib.jsonschema import *


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's',
    [
        '4123456789',
    ],
)
def test_is_nmi_ok(s):
    assert is_nmi(s)


@pytest.mark.parametrize(
    's,error',
    [
        (4123456789, 'NMIs are strings'),
        ('5123456789', 'NMIs don\'t start with 5'),
        ('412345678', 'NMIs are 10 characters long'),
    ],
)
def test_is_nmi_fail(s, error):
    with pytest.raises(ValueError, match=error):
        is_nmi(s)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's',
    [
        '5123456789',
    ],
)
def test_is_mirn_ok(s):
    assert is_mirn(s)


@pytest.mark.parametrize(
    's,error',
    [
        (5123456789, 'MIRNs are strings'),
        ('4123456789', 'MIRNs must start with 5'),
        ('512345678', 'MIRNs are 10 characters long'),
    ],
)
def test_is_mirn_fail(s, error):
    with pytest.raises(ValueError, match=error):
        is_mirn(s)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's,expected',
    [
        ('51 824 753 556', True),
        ('51   824 753 556  ', True),
        ('51824753556', True),
        (51824753556, True),
        ('70 326 883 043', True),
        ('58 896 144 542', True),
        ('21 582 637 628', True),
        ('70 138 591 901', True),
        ('21 047 727 425', True),
        ('11 283 251 728', True),
        ('94 135 025 341', True),
        ('41 824 753 556', False),
    ],
)
def test_is_abn_ok(s, expected):
    assert is_abn(s) == expected


@pytest.mark.parametrize(
    's,error',
    [
        ('1 824 753 556', 'ABNs are 11 digits'),
    ],
)
def test_is_abn_fail(s, error):
    with pytest.raises(ValueError, match=error):
        is_abn(s)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's,expected',
    [
        ('000 000 019', True),
        ('000000019', True),
        ('000   000019   ', True),
        ('000 250 000', True),
        ('000 500 005', True),
        ('000 750 005', True),
        ('001 000 004', True),
        ('001 250 004', True),
        ('001 500 009', True),
        ('001 749 999', True),
        ('001 999 999', True),
        ('002 249 998', True),
        ('002 499 998', True),
        ('002 749 993', True),
        ('102 749 993', False),
        (102749993, False),
    ],
)
def test_is_acn_ok(s, expected):
    assert is_acn(s) == expected


@pytest.mark.parametrize(
    's,error',
    [
        ('00 000 019', 'ACNs are 9 digits'),
    ],
)
def test_is_acn_fail(s, error):
    with pytest.raises(ValueError, match=error):
        is_acn(s)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's',
    [
        '1/3/2024',
        '01/3/2024',
    ],
)
def test_is_date_ddmmyyyy_ok(s):
    assert is_date_ddmmyyyy(s)


@pytest.mark.parametrize(
    's',
    [
        '31/2/2024',
        '2024/10/20',
    ],
)
def test_is_date_ddmmyyyy_fail(s):
    with pytest.raises(ValueError):
        is_date_ddmmyyyy(s)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's, expected',
    [
        ('J', True),
        ('kJ', True),
        ('MWh', True),
        ('GVArh', True),
        ('KJ', False),
        ('MW', False),
        ('GVA', False),
    ],
)
def test_is_energy_unit(s, expected):
    assert is_energy_unit(s) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's, expected',
    [
        ('W', True),
        ('kW', True),
        ('MW', True),
        ('GVA', True),
        ('J', False),
        ('MWh', False),
        ('GVAh', False),
    ],
)
def test_is_power_unit(s, expected):
    assert is_power_unit(s) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's, expected',
    [
        ('1.0.0', True),
        ('10.20.30', True),
        ('1.0', False),
        ('Wotcha', False),
    ],
)
def test_is_semantic_version(s, expected):
    assert is_semantic_version(s) == expected
