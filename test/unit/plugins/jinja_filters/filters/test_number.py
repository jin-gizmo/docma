"""Tests for number filters."""

import pytest  # noqa

from jinja2 import Environment


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,expected',
    [
        (1234567.45, 'en_AU', '1,234,567.45'),
        ('1234567.4501', 'en_AU', '1,234,567.45'),  # default precision is 3 decimal places.
        ('1234567.4501', 'fr_FR', '1\u202f234\u202f567,45'),
        # # Test default half-up rounding
        (1234567.1145, 'en_AU', '1,234,567.115'),  # would be .114 for half-even
        (1234567.1155, 'en_AU', '1,234,567.116'),
    ],
)
def test_decimal_render_var_locale_ok(value, locale, expected, jfilters):
    """Test the decimal() filter with locale from a render var.."""

    env = Environment()
    env.filters = jfilters
    template = f'{{{{ {value} | decimal }}}}'
    assert env.from_string(template).render(locale=locale, value=value) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,expected',
    [
        (1234567.45, 'en_AU', '1,234,567.45'),
        ('1234567.4501', 'en_AU', '1,234,567.45'),  # default precision is 3 decimal places.
        ('1234567.4501', 'fr_FR', '1\u202f234\u202f567,45'),
        # # Test default half-up rounding
        (1234567.1145, 'en_AU', '1,234,567.115'),  # would be .114 for half-even
        (1234567.1155, 'en_AU', '1,234,567.116'),
    ],
)
def test_decimal_embedded_locale_ok(value, locale, expected, jfilters):
    """Test the decimal() filter with locale specified in the template."""

    env = Environment()
    env.filters = jfilters
    template = f'{{% set locale="{locale}" %}}{{{{ {value} | decimal }}}}'
    assert env.from_string(template).render(locale='IGNORE', value=value) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,expected',
    [
        (1234567.1145, 'en_AU', '1,234,567.114'),
        (1234567.1155, 'en_AU', '1,234,567.116'),
    ],
)
def test_decimal_half_even_ok(value, locale, expected, jfilters):
    """Test overriding the default rounding mode."""

    env = Environment()
    env.filters = jfilters
    template = f'{{{{ {value} | decimal(rounding="half-even") }}}}'
    assert env.from_string(template).render(locale=locale, value=value) == expected


# ------------------------------------------------------------------------------
def test_decimal_bad_rounding_mode(jfilters):
    env = Environment()
    env.filters = jfilters
    template = f'{{{{ 123 | decimal(rounding="bad-rounding-mode") }}}}'
    with pytest.raises(ValueError, match='Unknown rounding mode'):
        env.from_string(template).render()


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,default,expected',
    [
        (None, 'en_AU', 0, '0'),
        (None, 'en_AU', 0.0, '0'),
        ('', 'en_AU', 0, '0'),
        (99, 'en_AU', 0, '99'),
        (None, 'en_AU', '--', '--'),
    ],
)
def test_decimal_default_ok(value, locale, default, expected, jfilters):
    env = Environment()
    env.filters = jfilters
    template = f'{{{{ value | decimal(default=default) }}}}'
    assert env.from_string(template).render(locale=locale, value=value, default=default) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale',
    [(None, 'en_AU'), ('', 'en_AU'), (None, 'fr_FR')],
)
def test_decimal_default_fail(value, locale, jfilters):
    """Test with no default value."""
    env = Environment()
    env.filters = jfilters
    template = f'{{{{ value | decimal }}}}'
    with pytest.raises(ValueError, match='Value is empty and no default specified'):
        env.from_string(template).render(locale=locale, value=value)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,expected',
    [
        (123457.45, 'en_AU', '123K'),
        ('123457.45', 'en_AU', '123K'),
        ('123457.45', 'fr_FR', '123\u00a0k'),
    ],
)
def test_compact_decimal_render_var_locale_ok(value, locale, expected, jfilters):
    """Test the decimal() filter with locale from a render var.."""

    env = Environment()
    env.filters = jfilters
    template = f'{{{{ {value} | compact_decimal }}}}'
    assert env.from_string(template).render(locale=locale, value=value) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,expected',
    [
        (0.1234, 'en_AU', '12%'),
        ('0.1234', 'en_AU', '12%'),
        ('1.234', 'en_AU', '123%'),
        ('0.1234', 'fr_FR', '12\u00a0%'),
    ],
)
def test_percent_render_var_locale_ok(value, locale, expected, jfilters):
    """Test the percent() filter with locale from a render var.."""

    env = Environment()
    env.filters = jfilters
    template = f'{{{{ {value} | percent }}}}'
    assert env.from_string(template).render(locale=locale, value=value) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,default,expected',
    [
        (None, 'en_AU', 0, '0%'),
        (None, 'en_AU', 0.0, '0%'),
        ('', 'en_AU', 0, '0%'),
        (0.99, 'en_AU', 0, '99%'),
        (None, 'en_AU', '--', '--'),
    ],
)
def test_percent_default_ok(value, locale, default, expected, jfilters):
    env = Environment()
    env.filters = jfilters
    template = f'{{{{ value | percent(default=default) }}}}'
    assert env.from_string(template).render(locale=locale, value=value, default=default) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale',
    [(None, 'en_AU'), ('', 'en_AU'), (None, 'fr_FR')],
)
def test_percent_default_fail(value, locale, jfilters):
    """Test with no default value."""
    env = Environment()
    env.filters = jfilters
    template = f'{{{{ value | percent }}}}'
    with pytest.raises(ValueError, match='Value is empty and no default specified'):
        env.from_string(template).render(locale=locale, value=value)
