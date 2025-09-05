"""Handler for CLI command to render to HTML."""

from __future__ import annotations

import os
from argparse import Namespace

from docma import render_template_to_html
from .__common__ import CliCommand, add_rendering_param_args, marshal_rendering_params


# ------------------------------------------------------------------------------
@CliCommand.register('html')
class Render(CliCommand):
    """Render a document template to HTML."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument(
            '-o',
            '--output',
            required=True,
            metavar='HTML-FILE',
            help='Name of output HTML file.',
        )

        self.argp.add_argument(
            '-t',
            '--template',
            required=True,
            metavar='DIR-OR-ZIP',
            help='Name of a template package.',
        )

        self.argp.add_argument(
            '-r',
            '--realm',
            help=(
                'Specify the lava realm. This is required when using lava to connect'
                ' to data providers. Defaults to the value of the LAVA_REALM'
                ' environment variable.'
            ),
        )

        add_rendering_param_args(self.argp)

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> None:
        """Execute the command."""

        if args.realm:
            os.environ['LAVA_REALM'] = args.realm

        output_html = render_template_to_html(
            template_pkg_name=args.template, render_params=marshal_rendering_params(args)
        )
        with open(args.output, 'w') as f:
            f.write(output_html.prettify(formatter='html'))
