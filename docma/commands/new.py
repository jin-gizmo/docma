"""Handler for new docma project CLI command."""

from __future__ import annotations

import os
from argparse import Namespace
from contextlib import contextmanager
from pathlib import Path

from cookiecutter.main import cookiecutter

import docma
from docma.lib import lib_path
from docma.lib.misc import StoreNameValuePair
from .__common__ import CliCommand


# ------------------------------------------------------------------------------
@CliCommand.register('new')
class New(CliCommand):
    """Create a new docma template source directory."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument(
            '--no-input',
            action='store_true',
            help=(
                'Do not prompt for user input. The -p / --param option should'
                ' be used to specify parameter values.'
            ),
        )

        self.argp.add_argument(
            '-p',
            '--param',
            dest='params',
            default={},
            action=StoreNameValuePair,
            metavar='KEY=VALUE',
            help=(
                'Specify default parameters for the underlying cookiecutter used'
                ' to create the new docma template. Can be used multiple times.'
                f' See {lib_path / "cookiecutter/cookiecutter.json"} for available parameters.'
            ),
        )

        self.argp.add_argument(
            'directory',
            help=(
                'Create the template source in the specified directory'
                ' (which must not already exist).'
            ),
        )

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> None:
        """Execute the command."""

        if (d := Path(args.directory)).exists():
            raise ValueError(f'{args.directory} already exists')

        # We want to make the docma package available to the cookiecutter
        # validation scripts. As cookiecutter runs in a subprocess we need to
        # mutate PYTHONPATH.
        with pythonpath_prepended(Path(docma.__file__).resolve().parent.parent):
            new_dir = cookiecutter(
                str(lib_path / 'cookiecutter'),
                overwrite_if_exists=False,
                extra_context={'template_id': d.stem, 'template_src_dir': args.directory}
                | args.params,
                no_input=args.no_input,
            )
        print(f'Created {new_dir}')


# ------------------------------------------------------------------------------
@contextmanager
def pythonpath_prepended(path: str | Path):
    """Temporarily prepend a path to PYTHONPATH."""

    if not isinstance(path, str):
        path = str(path)
    path_orig = os.environ.get('PYTHONPATH')
    try:
        os.environ['PYTHONPATH'] = os.pathsep.join([path, path_orig]) if path_orig else path
        yield
    finally:
        if path_orig is None:
            os.environ.pop('PYTHONPATH', None)
        else:
            os.environ['PYTHONPATH'] = path_orig
