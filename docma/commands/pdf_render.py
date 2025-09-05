"""Handler for render to PDF CLI command."""

from __future__ import annotations

import os
from argparse import Namespace

from docma import render_template_to_pdf
from .__common__ import CliCommand, add_rendering_param_args, marshal_rendering_params


# ------------------------------------------------------------------------------
@CliCommand.register('pdf')
class Render(CliCommand):
    """Render a document template to PDF."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument(
            '-o',
            '--output',
            required=True,
            metavar='PDF-FILE',
            help='Name of output PDF file.',
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

        c_render_overlay = self.argp.add_argument_group('overlay options')

        c_render_overlay.add_argument(
            '-s',
            '--stamp',
            metavar='OVERLAY_NAME',
            action='append',
            default=[],
            help=(
                'Apply the specified overlay name(s) as a stamp on top of the final PDF.'
                ' Multiple overlay names can be specified using multiple -s/--stamp arguments.'
            ),
        )

        c_render_overlay.add_argument(
            '-w',
            '--watermark',
            metavar='OVERLAY_NAME',
            action='append',
            default=[],
            help=(
                'Apply the specified overlay name(s) as a watermark underneath the final PDF.'
                ' Multiple overlay names can be specified using multiple'
                ' -w/--watermark arguments.'
            ),
        )

        c_render_pdf = self.argp.add_argument_group('PDF options')

        c_render_pdf.add_argument(
            '--compress',
            metavar='0..9',
            type=int,
            default=0,
            help=(
                'Apply lossless compression to the PDF. Default is 0 (no compression).'
                ' Maximum compression is 9.'
            ),
        )

        add_rendering_param_args(self.argp)

    # --------------------------------------------------------------------------
    @staticmethod
    def check_arguments(args: Namespace):
        """Validate arguments."""
        if hasattr(args, 'compress') and not 0 <= args.compress <= 9:
            raise ValueError('PDF compression must be between 0 and 9.')

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> None:
        """Execute the command."""

        if args.realm:
            os.environ['LAVA_REALM'] = args.realm

        output_pdf = render_template_to_pdf(
            template_pkg_name=args.template,
            render_params=marshal_rendering_params(args),
            watermark=args.watermark,
            stamp=args.stamp,
            compression=args.compress,
        )
        output_pdf.write(args.output)
