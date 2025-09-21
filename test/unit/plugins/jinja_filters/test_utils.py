"""Test jinja related utilities."""

import pytest
from jinja2 import Environment, pass_context

from docma.jinja.utils import *


# ------------------------------------------------------------------------------
# noinspection PyTestUnpassedFixture
@pytest.mark.parametrize(
    'template,render_param_value,expected',
    [
        # The render var is the selected value here
        ('{{ "myvar" | grab_from_context }}', 'xyzzy', 'xyzzy'),
        # The render var is overridden by the embedded value
        ('{% set myvar="plugh" %}{{ "myvar" | grab_from_context }}', 'xyzzy', 'plugh'),
        # The var will not be found at all here.
        ('{{ "y2" | grab_from_context }}', 'xyzzy', 'None'),
    ],
)
def test_get_context_var_ok(template, render_param_value, expected):

    @pass_context
    def grab_from_context(ctx: jinja2.runtime.Context, var_name: str):
        """Grab a variable from the Jinja2 runtime context."""
        return get_context_var(ctx, var_name)

    env = Environment()
    env.filters['grab_from_context'] = grab_from_context
    assert env.from_string(template).render(myvar=render_param_value) == expected
