"""Test legacy filters."""

import pytest  # noqa


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's, expected',
    [
        ('51 824 753 556', '51 824 753 556'),
        ('51824753556', '51 824 753 556'),
    ],
)
def test_abn_ok(s, expected, jfilters):
    with pytest.warns(DeprecationWarning, match='Plugin [^ ]+ is deprecated'):
        assert jfilters['abn'](s) == expected
        # Test case insensitivity
        assert jfilters['ABN'](s) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's',
    [
        '1 824 753 556',
    ],
)
def test_abn_fail(s, jfilters):
    with (
        pytest.warns(DeprecationWarning, match='Plugin [^ ]+ is deprecated'),
        pytest.raises(ValueError),
    ):
        jfilters['abn'](s)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's, expected',
    [
        ('001 749 999', '001 749 999'),
        ('001749999', '001 749 999'),
    ],
)
def test_acn_ok(s, expected, jfilters):
    with pytest.warns(DeprecationWarning, match='Plugin [^ ]+ is deprecated'):
        assert jfilters['acn'](s) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's',
    [
        '01 749 999',
    ],
)
def test_acn_fail(s, jfilters):
    with (
        pytest.warns(DeprecationWarning, match='Plugin [^ ]+ is deprecated'),
        pytest.raises(ValueError),
    ):
        jfilters['acn'](s)
