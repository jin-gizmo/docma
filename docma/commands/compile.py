"""Handler for compile CLI command."""

from __future__ import annotations

from argparse import Namespace

from docma import compile_template
from .__common__ import CliCommand


# ------------------------------------------------------------------------------
@CliCommand.register('compile')
class Compile(CliCommand):
    """Compile a source directory into a document template."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument(
            '-i',
            '--input',
            metavar='DIR',
            required=True,
            help='Name of directory containing source files.',
        )
        self.argp.add_argument(
            '-t',
            '--template',
            metavar='DIR-OR-ZIP',
            required=True,
            help='Either an output directory or the name of a ZIP file to be created.',
        )

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> None:
        """Execute the command."""
        compile_template(src_dir=args.input, tpkg=args.template)
