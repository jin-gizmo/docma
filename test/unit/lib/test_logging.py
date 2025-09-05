"""Test logging utils."""

import pytest

from docma.lib.logging import *


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'level, expected',
    [
        ('Debug', logging.DEBUG),
        ('info', logging.INFO),
        ('WARNING', logging.WARNING),
    ],
)
def test_get_log_level(level: str, expected: int):
    assert get_log_level(level) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('level', ['', 'unknown'])
def test_get_log_level_fail(level: str):
    with pytest.raises(ValueError, match='Bad log level'):
        get_log_level(level)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('setup_kwargs', [{}, {'colour': False}, {'prefix': 'WOOF'}])
def test_setup_logging_to_stderr(setup_kwargs: dict, capsys):
    """
    Test logging to stderr.

    The caplog fixture doesn't work too well here because of the way we fiddle
    with root logger.
    """
    setup_logging(level='debug', name='docma-test', **setup_kwargs)
    logger = logging.getLogger('docma-test')
    for level in ('debug', 'info', 'warning', 'error', 'critical'):
        logger.log(get_log_level(level), f'{level}: Hello world')
        assert f'{level}: Hello world' in capsys.readouterr().err
