"""Tests for docma.lib.jinja."""

import pytest

from docma.lib.jinja import *


# ------------------------------------------------------------------------------
def test_noloader():
    with pytest.raises(Exception, match='loading prohibited'):
        NoLoader().get_source(JinjaEnvironment(), 'whatever')


# ------------------------------------------------------------------------------
def test_abort():
    with pytest.raises(Exception, match='aborted'):
        docma_extras['abort']('aborted')


# ------------------------------------------------------------------------------
def test_require():
    assert filters['require']('abcd', 'Nothing else required') == 'abcd'
    with pytest.raises(Exception, match='something required'):
        filters['require'](None, 'something required')


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'params, expected',
    [
        (('1.23',), '$1.23'),
        (('1.',), '$1.00'),
        (('1.2345',), '$1.23'),  # round down
        (('1.2350',), '$1.24'),  # round up
        (('1.2350', 0), '$1'),
        (('1.2350', 4, 'AUD'), 'AUD1.2350'),
        (('1_234_567', 0), '$1,234,567'),
    ],
)
def test_dollars(params, expected):
    assert filters['dollars'](*params) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's, expected',
    [
        ('51 824 753 556', '51 824 753 556'),
        ('51824753556', '51 824 753 556'),
    ],
)
def test_abn_ok(s, expected):
    assert filters['abn'](s) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's',
    [
        '1 824 753 556',
    ],
)
def test_abn_fail(s):
    with pytest.raises(ValueError):
        filters['abn'](s)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's, expected',
    [
        ('001 749 999', '001 749 999'),
        ('001749999', '001 749 999'),
    ],
)
def test_acn_ok(s, expected):
    assert filters['acn'](s) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's',
    [
        '01 749 999',
    ],
)
def test_acn_fail(s):
    with pytest.raises(ValueError):
        filters['acn'](s)


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
def test_css_id(s, expected):
    assert filters['css_id'](s) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's',
    [
        'schema.table',
        'table',
    ],
)
def test_sql_safe_ok(s):
    assert filters['sql_safe'](s) == s


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
def test_sql_safe_fail(s):
    with pytest.raises(ValueError):
        filters['sql_safe'](s)


# ------------------------------------------------------------------------------
def test_jfunc():
    @jfunc('funky')
    def _():
        """Placeholder."""
        return 42

    assert docma_extras['funky']() == 42


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'put_template, params, get_template, expected',
    [
        ('{% global x=10, y=20 %}', {}, '{{ globals.x + globals.y }}', '30'),
        ('{% set z=10 %}{% global x=z, y=20 %}', {}, '{{ globals.x + globals.y }}', '30'),
        ('{% global x="X", y="Y" %}', {}, '{{ globals.x + globals.y }}', 'XY'),
        ('{% global x=10 %}', {'y': 20}, '{{ globals.x + y }}', '30'),
    ],
)
def test_storeglobals_extension_ok(put_template, params, get_template, expected):

    env = JinjaEnvironment()

    # We have 2 distinct rendering events here. Make sure the globals span them.
    env.from_string(put_template).render(**params)
    assert env.from_string(get_template).render(**params) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'template, error, match',
    [
        ('{% global %}', TemplateSyntaxError, 'Expected at least one assignment'),
        ('{% global 1 %}', TemplateSyntaxError, 'Expected variable name'),
        ('{% global x + %}', TemplateSyntaxError, 'Expected "=" in global'),
        ('{% global x = %}', TemplateSyntaxError, 'Invalid expression after .*='),
        ('{% global x=10 y=20 %}', TemplateSyntaxError, 'Expected "," or end of block'),
        ('{% global x=10, %}', TemplateSyntaxError, f'Unexpected trailing comma'),
    ],
)
def test_storeglobals_extension_fail(template, error, match):

    env = JinjaEnvironment()
    with pytest.raises(error, match=match):
        env.from_string(template).render()


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'assignments, error, match',
    [
        (
            [
                (10, 10),
            ],
            TemplateSyntaxError,
            'Global name must be a string',
        ),
        (
            [
                ('+bad+', 10),
            ],
            TemplateSyntaxError,
            'Global name .* not a valid Python identifier',
        ),
    ],
)
def test_storeglobals_extension_store_multiple_fail(assignments, error, match):
    ext = StoreGlobalsExtension(JinjaEnvironment())
    with pytest.raises(error, match=match):
        ext._store_multiple(assignments, 0, None)  # noqa


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'template, error, match',
    [
        ('{% abort "Oh no!" %}', RuntimeError, 'Oh no!'),
        ('{% abort %}', TemplateSyntaxError, 'abort tag requires a message argument'),
        ('{% abort [1,2,3 %}', TemplateSyntaxError, 'abort tag requires a valid string message'),
    ],
)
def test_abort_extension(template, error, match):

    env = JinjaEnvironment()
    with pytest.raises(error, match=match):
        env.from_string(template).render()
