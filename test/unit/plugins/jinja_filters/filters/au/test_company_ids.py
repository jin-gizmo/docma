"""Test AU specific filters."""

import pytest  # noqa


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's, expected',
    [
        ('51 824 753 556', '51 824 753 556'),
        ('51824753556', '51 824 753 556'),
    ],
)
def test_au_abn_ok(s, expected, jfilters):
    assert jfilters['au.abn'](s) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's',
    [
        '1 824 753 556',
    ],
)
def test_au_abn_fail(s, jfilters):
    with pytest.raises(ValueError):
        jfilters['au.abn'](s)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's, expected',
    [
        ('001 749 999', '001 749 999'),
        ('001749999', '001 749 999'),
    ],
)
def test_au_acn_ok(s, expected, jfilters):
    assert jfilters['au.acn'](s) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's',
    [
        '01 749 999',
    ],
)
def test_au_acn_fail(s, jfilters):
    with pytest.raises(ValueError):
        jfilters['au.acn'](s)
