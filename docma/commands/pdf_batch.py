"""Handler for batch PDF render CLI command."""

from __future__ import annotations

import logging
import os
from argparse import Namespace
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from logging import getLogger
from typing import Any

import yaml
from tqdm import tqdm

from docma import render_template_to_pdf, safe_render_path
from docma.config import LOGNAME
from docma.data_providers import DataSourceSpec, load_data
from docma.docma_core import PKG_CONFIG_FILE, coalesce_docma_render_params
from docma.jinja import DocmaRenderContext
from docma.lib.logging import setup_logging
from docma.lib.misc import deep_update_dict
from docma.lib.packager import PackageReader
from .__common__ import CliCommand, add_rendering_param_args, marshal_rendering_params

LOG = getLogger(LOGNAME)


# ------------------------------------------------------------------------------
def renderer(
    batch_params: dict[str, Any], output_file: str, common_params: dict[str, Any], **kwargs: Any
) -> None:
    """
    Work function for the multiprocessing pool.

    :param batch_params: Rendering parameters for one batch item coming from
                        the batch generator.
    :param output_file: Name of the PDF output file.
    :param common_params: Common (non batch item specific) parameters for the
                        rendering process.
    :param kwargs:      Passed directly to render_template_to_pdf(),.
    """

    LOG.debug('PID=%d: Output to %s', os.getpid(), output_file)
    pdf = render_template_to_pdf(
        render_params=deep_update_dict({}, common_params, batch_params), **kwargs
    )
    pdf.write(output_file)
    LOG.info('Created %s', output_file)


# ------------------------------------------------------------------------------
@CliCommand.register('pdf-batch')
class PdfBatch(CliCommand):
    """Render a batch of PDF documents from a single document template."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument(
            '-d',
            '--data-source-spec',
            metavar='DATA-SOURCE-SPEC',
            required=True,
            action='store',
            help=(
                'A docma data source specification to provide a series of records'
                ' for the batch. Data source specifications are in the form'
                ' "<TYPE>;<LOCATION>[;QUERY]".'
            ),
        )

        self.argp.add_argument(
            '-n',
            '--nproc',
            type=int,
            metavar='PROCESS-COUNT',
            default=os.cpu_count(),
            action='store',
            help=(
                'Number of processes to use for rendering the batch.'
                f' Defaults to the CPU count ({os.cpu_count()}).'
            ),
        )

        self.argp.add_argument(
            '--no-progress',
            dest='progress',
            action='store_false',
            help=(
                'Don\'t show the progress bar. The bar is only shown when the'
                ' log level is "warning" or higher.'
            ),
        )

        self.argp.add_argument(
            '-o',
            '--output',
            metavar='TEMPLATE',
            required=True,
            help=(
                'A Jinja template to generate filenames for output PDFs.'
                ' Each path component is individually rendered and there'
                ' are tight restrictions on the characters that the rendered'
                ' component can contain. These restrictions won\'t be a'
                ' problem for most sensible operations.'
            ),
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

        overlayp = self.argp.add_argument_group('overlay options')

        overlayp.add_argument(
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

        overlayp.add_argument(
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

        pdfp = self.argp.add_argument_group('PDF options')

        pdfp.add_argument(
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
        """Execute the CLI command with the specified arguments."""

        if args.realm:
            os.environ['LAVA_REALM'] = args.realm

        data_source_spec = DataSourceSpec.from_string(args.data_source_spec)
        init = partial(setup_logging, args.level, name=LOGNAME, colour=args.colour)
        cli_params = marshal_rendering_params(args)
        with PackageReader.new(args.template) as tpkg:
            # We need to create a full rendering context for the data source spec
            # specified on the command line used to generate iteration data.
            render_params = coalesce_docma_render_params(
                yaml.safe_load(tpkg.read_text(PKG_CONFIG_FILE)), cli_params
            )
            context = DocmaRenderContext(tpkg, render_params)
            batch_data = load_data(data_source_spec, context)
            # We don't need to pass the full context params to the workers as
            # they will create their own. They just need the CLI params and
            # the batch row data.
            batch_worker_fn = partial(
                renderer,
                common_params=cli_params,
                template_pkg_name=args.template,
                watermark=args.watermark,
                stamp=args.stamp,
                compression=args.compress,
            )
            progress = (
                partial(tqdm, colour='green', total=len(batch_data))
                if args.progress and LOG.getEffectiveLevel() >= logging.WARNING
                else lambda x: x
            )
            output_files = (safe_render_path(args.output, context, row) for row in batch_data)
            with ProcessPoolExecutor(
                max_workers=min(len(batch_data), args.nproc), initializer=init
            ) as executor:
                for _ in progress(executor.map(batch_worker_fn, batch_data, output_files)):
                    pass
