"""Tests for datetime formatting filters."""

from datetime import datetime, timedelta

import pytest  # noqa
from jinja2 import Environment


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filter_name, value,locale,expected',
    [
        ('datetime', datetime(2025, 9, 17, 14, 15, 16), 'en_AU', '17 Sept 2025, 2:15:16\u202fpm'),
        ('datetime', datetime(2025, 9, 17, 14, 15, 16), 'en_US', 'Sep 17, 2025, 2:15:16\u202fPM'),
        ('date', datetime(2025, 9, 17, 14, 15, 16), 'en_AU', '17 Sept 2025'),
        ('date', datetime(2025, 9, 17, 14, 15, 16), 'en_US', 'Sep 17, 2025'),
        ('time', datetime(2025, 9, 17, 14, 15, 16), 'en_AU', '2:15:16\u202fpm'),
        ('time', datetime(2025, 9, 17, 14, 15, 16), 'en_US', '2:15:16\u202fPM'),
        ('time', datetime(2025, 9, 17, 14, 15, 16), 'fr_FR', '14:15:16'),
        ('timedelta', timedelta(hours=80), 'en_AU', '3 days'),
        ('timedelta', timedelta(hours=80), 'fr_FR', '3\xa0jours'),
    ],
)
def test_datetime_render_var_locale_ok(filter_name, value, locale, expected, jfilters):
    """Test the datetime() / date() / time() filters with locale from a render var.."""

    env = Environment()
    env.filters = jfilters
    template = f'{{{{ value | {filter_name } }}}}'
    assert env.from_string(template).render(locale=locale, value=value) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filter_name, value,locale,expected',
    [
        ('datetime', datetime(2025, 9, 17, 14, 15, 16), 'en_AU', '17 Sept 2025, 2:15:16\u202fpm'),
        ('datetime', datetime(2025, 9, 17, 14, 15, 16), 'en_US', 'Sep 17, 2025, 2:15:16\u202fPM'),
        ('date', datetime(2025, 9, 17, 14, 15, 16), 'en_AU', '17 Sept 2025'),
        ('date', datetime(2025, 9, 17, 14, 15, 16), 'en_US', 'Sep 17, 2025'),
        ('time', datetime(2025, 9, 17, 14, 15, 16), 'en_AU', '2:15:16\u202fpm'),
        ('time', datetime(2025, 9, 17, 14, 15, 16), 'en_US', '2:15:16\u202fPM'),
        ('time', datetime(2025, 9, 17, 14, 15, 16), 'fr_FR', '14:15:16'),
        ('timedelta', timedelta(hours=80), 'en_AU', '3 days'),
        ('timedelta', timedelta(hours=80), 'fr_FR', '3\xa0jours'),
    ],
)
def test_datetime_embedded_locale_ok(filter_name, value, locale, expected, jfilters):
    """Test the datetime() / date() / time() filters with locale from a render var.."""

    env = Environment()
    env.filters = jfilters
    template = f'{{% set locale="{locale}" %}}{{{{ value | {filter_name } }}}}'
    assert env.from_string(template).render(locale='IGNORE', value=value) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'date_str,locale,expected',
    [
        ('2025-09-01', 'en_AU', '2025-09-01'),
        ('1/9/2025', 'en_AU', '2025-09-01'),
        ('1/9/2025', 'en_US', '2025-01-09'),
    ],
)
def test_parse_date_render_var_locale_ok(date_str: str, locale, expected, jfilters):
    env = Environment()
    env.filters = jfilters
    template = f'{{{{ (value | parse_date).isoformat() }}}}'
    assert env.from_string(template).render(locale=locale, value=date_str) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'date_str,locale,expected',
    [
        ('2025-09-01', 'en_AU', '2025-09-01'),
        ('1/9/2025', 'en_AU', '2025-09-01'),
        ('1/9/2025', 'en_US', '2025-01-09'),
    ],
)
def test_parse_date_embedded_locale_ok(date_str: str, locale, expected, jfilters):
    env = Environment()
    env.filters = jfilters
    template = f'{{% set locale="{locale}" %}}{{{{ (value | parse_date).isoformat() }}}}'
    assert env.from_string(template).render(locale='IGNORE', value=date_str) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "time_str,locale,expected",
    [
        ('2:15', 'en_AU', '02:15:00'),
        ('2:15 pm', 'en_AU', '14:15:00'),
        ('2 pm', 'en_US', '14:00:00'),
    ],
)
def test_parse_time_render_var_locale_ok(time_str, locale, expected, jfilters):
    env = Environment()
    env.filters = jfilters
    template = f'{{{{ (value | parse_time).isoformat() }}}}'
    assert env.from_string(template).render(locale=locale, value=time_str) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "time_str,locale,expected",
    [
        ('2:15', 'en_AU', '02:15:00'),
        ('2:15 pm', 'en_AU', '14:15:00'),
        ('2 pm', 'en_US', '14:00:00'),
    ],
)
def test_parse_time_embedded_locale_ok(time_str, locale, expected, jfilters):
    env = Environment()
    env.filters = jfilters
    template = f'{{% set locale="{locale}" %}}{{{{ (value | parse_time).isoformat() }}}}'
    assert env.from_string(template).render(locale='IGNORE', value=time_str) == expected
