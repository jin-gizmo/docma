"""
Test the dynamic currency filters implemented by the CurrencyResolver.

We can't just call these directly as we do for the simpler filters because they also need
the Jinja2 context as the first parameter, so we go through a proper rendering.

"""

import pytest  # noqa
from jinja2 import Environment


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,currency,expected',
    [
        (1234567.45, 'en_AU', 'AUD', '$1,234,567.45'),
        ('1234567.45', 'en_AU', 'AUD', '$1,234,567.45'),
        (1234567.45, 'en_AU', 'USD', 'USD1,234,567.45'),
        (1234567.45, 'en_US', 'USD', '$1,234,567.45'),
        (1234567.45, 'en_US', 'AUD', 'A$1,234,567.45'),
        (1234567.45, 'fr_FR', 'EUR', '1\u202f234\u202f567,45\u00a0€'),
        # Test default half-up rounding
        (1234567.454, 'en_AU', 'AUD', '$1,234,567.45'),
        (1234567.464, 'en_AU', 'AUD', '$1,234,567.46'),
        (1234567.455, 'en_AU', 'AUD', '$1,234,567.46'),
        (1234567.465, 'en_AU', 'AUD', '$1,234,567.47'),
    ],
)
def test_currency_render_var_locale_ok(value, locale, currency, expected, jfilters):
    """Test the generic currency() filter with locale from a render var.."""

    env = Environment()
    env.filters = jfilters
    # This looks weird but filters and variables don't clash in Jinja2
    template = f'{{{{ {value} | currency(currency) }}}}'
    assert (
        env.from_string(template).render(locale=locale, value=value, currency=currency) == expected
    )


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,currency,expected',
    [
        (1234567.45, 'en_AU', 'AUD', '$1,234,567.45'),
        ('1234567.45', 'en_AU', 'AUD', '$1,234,567.45'),
        (1234567.45, 'en_AU', 'USD', 'USD1,234,567.45'),
        (1234567.45, 'en_US', 'USD', '$1,234,567.45'),
        (1234567.45, 'en_US', 'AUD', 'A$1,234,567.45'),
        (1234567.45, 'fr_FR', 'EUR', '1\u202f234\u202f567,45\u00a0€'),
        # Test default half-up rounding
        (1234567.454, 'en_AU', 'AUD', '$1,234,567.45'),
        (1234567.464, 'en_AU', 'AUD', '$1,234,567.46'),
        (1234567.455, 'en_AU', 'AUD', '$1,234,567.46'),
        (1234567.465, 'en_AU', 'AUD', '$1,234,567.47'),
    ],
)
def test_currency_embedded_locale_ok(value, locale, currency, expected, jfilters):
    """Test the generic currency() filter with locale specified in the template."""

    env = Environment()
    env.filters = jfilters
    # This looks weird but filters and variables don't clash in Jinja2
    template = f'{{% set locale="{locale}" %}}{{{{ {value} | currency("{currency}") }}}}'
    assert (
        env.from_string(template).render(locale='IGNORE', value=value, currency=currency)
        == expected
    )


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,currency,expected',
    [
        (1234567.45, 'en_AU', 'AUD', '$1,234,567.45'),
        ('1234567.45', 'en_AU', 'AUD', '$1,234,567.45'),
        (1234567.45, 'en_AU', 'USD', 'USD1,234,567.45'),
        (1234567.45, 'en_US', 'USD', '$1,234,567.45'),
        (1234567.45, 'en_US', 'AUD', 'A$1,234,567.45'),
        (1234567.45, 'fr_FR', 'EUR', '1\u202f234\u202f567,45\u00a0€'),
        # Test default half-up rounding
        (1234567.454, 'en_AU', 'AUD', '$1,234,567.45'),
        (1234567.464, 'en_AU', 'AUD', '$1,234,567.46'),
        (1234567.455, 'en_AU', 'AUD', '$1,234,567.46'),
        (1234567.465, 'en_AU', 'AUD', '$1,234,567.47'),
    ],
)
def test_named_currency_ok(value, locale, currency, expected, jfilters):
    """Test the named currency filters (eg. aud(), eur() etc.)"""

    env = Environment()
    env.filters = jfilters
    template = f'{{{{ {value} | {currency.lower()} }}}}'
    assert (
        env.from_string(template).render(locale=locale, value=value, currency=currency) == expected
    )


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,currency,expected',
    [
        (1234567.454, 'en_AU', 'AUD', '$1,234,567.45'),
        (1234567.464, 'en_AU', 'AUD', '$1,234,567.46'),
        (1234567.455, 'en_AU', 'AUD', '$1,234,567.46'),
        (1234567.465, 'en_AU', 'AUD', '$1,234,567.46'),  # Evens round down so .46 not .47
    ],
)
def test_named_currency_half_even_ok(value, locale, currency, expected, jfilters):
    """Test overriding the default rounding mode."""

    env = Environment()
    env.filters = jfilters
    template = f'{{{{ {value} | {currency.lower()}(rounding="half-even") }}}}'
    assert env.from_string(template).render(locale=locale, value=value) == expected


# ------------------------------------------------------------------------------
def test_currency_bad_rounding_mode(jfilters):
    env = Environment()
    env.filters = jfilters
    template = f'{{{{ 123 | aud(rounding="bad-rounding-mode") }}}}'
    with pytest.raises(ValueError, match='Unknown rounding mode'):
        env.from_string(template).render()


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,currency,default,expected',
    [
        (None, 'en_AU', 'AUD', 0, '$0.00'),
        ('', 'en_AU', 'AUD', 0, '$0.00'),
        ('', 'fr_FR', 'EUR', 0, '0,00\u00a0\u20ac'),
        (99, 'en_AU', 'AUD', 0, '$99.00'),
        (None, 'en_AU', 'AUD', 'FREE!!', 'FREE!!'),
    ],
)
def test_currency_default_ok(value, locale, currency, default, expected, jfilters):
    env = Environment()
    env.filters = jfilters
    template = f'{{{{ value | {currency.lower()}(default=default) }}}}'
    assert env.from_string(template).render(locale=locale, value=value, default=default) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,currency',
    [(None, 'en_AU', 'AUD'), ('', 'en_AU', 'AUD'), (None, 'fr_FR', 'EUR')],
)
def test_currency_default_fail(value, locale, currency, jfilters):
    """Test with no default value."""
    env = Environment()
    env.filters = jfilters
    template = f'{{{{ value | {currency.lower()} }}}}'
    with pytest.raises(ValueError, match='Value is empty and no default specified'):
        env.from_string(template).render(locale=locale, value=value)
