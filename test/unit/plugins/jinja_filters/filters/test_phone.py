"""
Test phone filter.

We can't just call this directly as we do for the simpler filters because it also needs
the Jinja2 context as the first parameter, so we go through a proper rendering.

See:

AU: https://www.acma.gov.au/phone-numbers-use-tv-shows-films-and-creative-works
US: https://developers.google.com/style/phone-numbers
"""

import pytest
from jinja2 import Environment


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,country,style,expected',
    [
        ('0491 570 006', 'AU', '', '0491 570 006'),  # Aus # in Aus --> national format
        ('+61 491 570 006', 'AU', '', '0491 570 006'),  # Aus # in Aus --> national format
        (491570006, 'AU', '', '0491 570 006'),  # Int's are discouraged but are accepted
        ('+61 491 570 006', 'SE', '', '+61 491 570 006'),  # Aus # in Sweden --> international
        ('+61 491 570 006', 'AU', 'e164', '+61491570006'),  # Force xe164
        ('+61 491 570 006', 'SE', 'National', '0491 570 006'),  # Force national
        ('bad-to-the-phone', 'AU', '', 'bad-to-the-phone'),  # Last resort - return the original
    ],
)
def test_phone_named_country_ok(value, country, style, expected, jfilters):
    env = Environment()
    quoted_value = f'"{value}"' if isinstance(value, str) else value
    env.filters = jfilters
    template = f'{{{{ {quoted_value} | phone("{country}", format="{style}") }}}}'
    assert env.from_string(template).render() == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,style,expected',
    [
        ('+61 491 570 006', 'en_AU', '', '0491 570 006'),  # Aus # in Aus --> national format
        ('0491 570 006', 'en_AU', '', '0491 570 006'),  # Aus # in Aus --> national format
    ],
)
def test_phone_country_from_external_locale_ok(value, locale, style, expected, jfilters):
    """Test reliance on locale provided as external render var to get country."""
    env = Environment()
    quoted_value = f'"{value}"' if isinstance(value, str) else value
    env.filters = jfilters
    template = f'{{{{ {quoted_value} | phone(format="{style}") }}}}'
    assert env.from_string(template).render(locale=locale) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,locale,style,expected',
    [
        ('+61 491 570 006', 'en_AU', '', '0491 570 006'),  # Aus # in Aus --> national format
        ('0491 570 006', 'en_AU', '', '0491 570 006'),  # Aus # in Aus --> national format
    ],
)
def test_phone_country_from_internal_locale_ok(value, locale, style, expected, jfilters):
    """Test reliance on locale provided as internal render var to get country."""
    env = Environment()
    quoted_value = f'"{value}"' if isinstance(value, str) else value
    env.filters = jfilters
    template = f'{{% set locale="{locale}" %}}{{{{ {quoted_value} | phone(format="{style}") }}}}'
    assert env.from_string(template).render(locale='garbage') == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'value,country,style,error,message',
    [
        ('does not matter', 'ZZ', '', ValueError, 'Unsupported phone number region'),
        ('does not matter', 'AU', 'BAD-FORMAT', ValueError, 'Unknown phone number format'),
    ],
)
def test_phone_named_country_fail(value, country, style, error, message, jfilters):
    env = Environment()
    env.filters = jfilters
    template = f'{{{{ "{value}" | phone("{country}", format="{style}") }}}}'
    # env.from_string(template).render(locale=locale, value=value, currency=currency) == expected
    with pytest.raises(error, match=message):
        env.from_string(template).render()
