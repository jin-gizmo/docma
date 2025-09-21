"""Test general utility filters."""

import pytest


# ------------------------------------------------------------------------------
def test_require(jfilters):
    assert jfilters['require']('abcd', 'Nothing else required') == 'abcd'
    with pytest.raises(Exception, match='something required'):
        jfilters['require'](None, 'something required')


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's,expected',
    [
        ('abcd', 'abcd'),
        ('a b cd', 'a-b-cd'),
        ('9a b cd', '_9a-b-cd'),
        ('a/()=*&bcd', 'abcd'),
    ],
)
def test_css_id(s, expected, jfilters):
    assert jfilters['css_id'](s) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's',
    [
        'schema.table',
        'table',
    ],
)
def test_sql_safe_ok(s, jfilters):
    assert jfilters['sql_safe'](s) == s


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's',
    [
        'schema..table',
        'schema/table',
        'bad"to"the"bone',
        "bad'to'the'bone",
    ],
)
def test_sql_safe_fail(s, jfilters):
    with pytest.raises(ValueError):
        jfilters['sql_safe'](s)
