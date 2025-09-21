"""Test the legacy (but not yet deprecated) dollars filter."""

__author__ = 'Murray Andrews'

import pytest  # noqa


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
def test_dollars(params, expected, jfilters):
    assert jfilters['dollars'](*params) == expected
