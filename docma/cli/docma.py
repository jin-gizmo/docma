#!/usr/bin/env python3

"""Command line utility to manufacture PDF documents."""

from __future__ import annotations

import argparse
import sys
from logging import getLogger
from pathlib import Path

from docma.commands import CliCommand
from docma.config import LOGNAME
from docma.exceptions import DocmaInternalError
from docma.lib.logging import setup_logging
from docma.version import __version__

__author__ = 'Murray Andrews'

PROG = Path(sys.argv[0]).stem
LOG = getLogger(LOGNAME)
LOGLEVEL = 'warning'


# ------------------------------------------------------------------------------
def process_cli_args() -> argparse.Namespace:
    """
    Process the command line arguments.

    :return:    The args namespace.
    """

    argp = argparse.ArgumentParser(prog=PROG, description='Manufacture documents.')

    argp.add_argument('-v', '--version', action='version', version=__version__)

    # ----------------------------------------
    # Logging args

    logp = argp.add_argument_group('logging arguments')
    logp.add_argument(
        '--no-colour',
        '--no-color',
        dest='colour',
        action='store_false',
        default=True,
        help='Don\'t use colour in log messages.',
    )

    logp.add_argument(
        '-l',
        '--level',
        metavar='LEVEL',
        default=LOGLEVEL,
        help=(
            'Print messages of a given severity level or above. The standard'
            ' logging level names are available but debug, info, warning and'
            f' error are most useful. The default is {LOGLEVEL}.'
        ),
    )

    # ----------------------------------------
    # Add the sub-commonads
    subp = argp.add_subparsers(title='subcommands', required=True)
    for cmd in sorted(CliCommand.commands.values(), key=lambda c: c.name):
        cmd(subp).add_arguments()

    args = argp.parse_args()

    if not hasattr(args, 'handler'):
        raise DocmaInternalError('Args namespace missing handler entry')

    try:
        args.handler.check_arguments(args)
    except ValueError as e:
        argp.error(str(e))

    return args


# ------------------------------------------------------------------------------
def main() -> int:
    """Show time."""

    try:
        setup_logging(LOGLEVEL, name=LOGNAME, prefix=PROG)
        args = process_cli_args()
        setup_logging(args.level, name=LOGNAME, colour=args.colour)
        args.handler.execute(args)
        return 0
    except Exception as e:
        LOG.error(str(e))
        return 1
    except KeyboardInterrupt:
        LOG.warning('Interrupt')
        return 2


# ------------------------------------------------------------------------------
# This only gets used during dev/test. Once deployed as a package, main() gets
# imported and run directly.
if __name__ == '__main__':
    exit(main())  # pragma: no cover
