"""Handler for info CLI command."""

from __future__ import annotations

import sys
from argparse import Namespace

import yaml

from docma import get_template_info
from docma.lib.packager import PackageReader
from .__common__ import CliCommand


# ------------------------------------------------------------------------------
@CliCommand.register('info')
class Info(CliCommand):
    """Print information about a document template."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument(
            '-t',
            '--template',
            required=True,
            metavar='DIR-OR-ZIP',
            help='Name of a template package.',
        )

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> None:
        """Execute the CLI command with the specified arguments."""
        with PackageReader.new(args.template) as tpkg:
            yaml.safe_dump(get_template_info(tpkg), sys.stdout, default_flow_style=False, indent=2)
