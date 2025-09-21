"""Tests for docma.lib.jinja."""

import pytest
from jinja2.exceptions import TemplateSyntaxError

from docma.jinja import *
from docma.jinja.extensions import StoreGlobalsExtension


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

    env = DocmaJinjaEnvironment()

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

    env = DocmaJinjaEnvironment()
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
    ext = StoreGlobalsExtension(DocmaJinjaEnvironment())
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

    env = DocmaJinjaEnvironment()
    with pytest.raises(error, match=match):
        env.from_string(template).render()


# ------------------------------------------------------------------------------
def test_dump_params_extension_ok():
    env = DocmaJinjaEnvironment()
    result =  env.from_string('{% dump_params %}').render(a=10, b='Hello')
    assert "'a': 10," in result
    assert "'b': 'Hello'," in result

# ------------------------------------------------------------------------------
def test_jext_decorator_wrong_type():

    with pytest.raises(TypeError, match='must be a subclass of .*Extension'):
        @jext
        class C:
            """Dummy class."""
            ...
