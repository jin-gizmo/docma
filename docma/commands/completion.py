"""Handler for completion CLI command."""

from __future__ import annotations

import os
import sys
from argparse import Namespace

from argcomplete import shellcode

from .__common__ import CliCommand

SHELL = os.path.basename(os.getenv('SHELL', 'bash'))


# ------------------------------------------------------------------------------
@CliCommand.register('completion')
class Info(CliCommand):
    """Generate the command line completion script."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument(
            '-s',
            '--shell',
            default=SHELL,
            help=(
                'Output code for the specified shell. Defaults to the current shell,'
                ' if that can be determined, otherwise "bash".'
            ),
        )

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> None:
        """Execute the CLI command with the specified arguments."""

        print(shellcode([os.path.basename(sys.argv[0])], shell=args.shell))
