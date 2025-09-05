"""Logging related stuff."""

from __future__ import annotations

__author__ = 'Murray Andrews'

import logging
import sys

import colorama


# ------------------------------------------------------------------------------
def get_log_level(s: str) -> int:
    """
    Convert string log level to the corresponding integer log level.

    Raises ValueError if a bad string is provided.

    :param s:       A string version of a log level (e.g. 'error', 'info').
                    Case is not significant.

    :return:        The numeric logLevel equivalent.

    :raises:        ValueError if the supplied string cannot be converted.
    """

    if not s or not isinstance(s, str):
        raise ValueError('Bad log level:' + str(s))

    t = s.upper()

    if not hasattr(logging, t):
        raise ValueError('Bad log level: ' + s)

    return getattr(logging, t)


# ------------------------------------------------------------------------------
class ColourLogHandler(logging.Handler):
    """Basic stream handler that writes to stderr with colours for log levels."""

    # --------------------------------------------------------------------------
    def __init__(self, colour: bool = True):
        """Allow colour to be enabled or disabled."""

        super().__init__()
        self.colour = colour

    # --------------------------------------------------------------------------
    def emit(self, record: logging.LogRecord) -> None:
        """Print the record to stderr with some colour enhancement."""

        if self.colour:
            if record.levelno >= logging.ERROR:
                colour = colorama.Style.BRIGHT + colorama.Fore.RED
            elif record.levelno >= logging.WARNING:
                colour = colorama.Fore.MAGENTA
            elif record.levelno >= logging.INFO:
                colour = colorama.Fore.BLUE
            else:
                colour = colorama.Style.DIM + colorama.Fore.BLACK

            print(
                colour + self.format(record) + colorama.Fore.RESET + colorama.Style.RESET_ALL,
                file=sys.stderr,
            )
        else:
            print(self.format(record), file=sys.stderr)


# ------------------------------------------------------------------------------
def setup_logging(
    level: str, colour: bool = True, name: str | None = None, prefix: str | None = None
) -> None:
    """
    Set up logging.

    :param level:   Logging level. The string format of a level (eg 'debug').
    :param colour:  If True and logging to the terminal, colourise messages for
                    different logging levels. Default True.
    :param name:    The name of the logger to configure. If None, configure the
                    root logger.
    :param prefix:  Messages are prefixed by this string (with colon+space
                    appended). Default None.

    :raise ValueError: If an invalid log level or syslog facility is specified.
    """

    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(get_log_level(level))

    # Get rid of unwanted handlers.
    for h in logger.handlers:
        logger.removeHandler(h)

    h = ColourLogHandler(colour=colour)
    h.setFormatter(logging.Formatter((prefix + ': ' if prefix else '') + '%(message)s'))
    logger.addHandler(h)
    logger.debug('Log level set to %s (%d)', level, logger.getEffectiveLevel())
