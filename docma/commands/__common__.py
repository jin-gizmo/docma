"""Common components for docma CLI commands."""

from __future__ import annotations

import json
import sys
from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Callable

import yaml

from docma.lib.misc import StoreNameValuePair, deep_update_dict


# ------------------------------------------------------------------------------
class CliCommand(ABC):
    """
    CLI subcommand handler.

    CLI subcommands should be declared as a subclass and also registered using
    the `register` decorator so that they are automatically discovered.

    Subclasses may implement `add_arguments` and `check_arguments` methods and
    must implement the `execute` method.

    Thus:

    ```python
    @CliCommand.register('command-name')
    class Whatever(CliCommand):

        def add_arguments(self) -> None:
            self.argp.add_argument('--arg1', action='store')

        def execute(self, args: Namespace) -> None:
            print(f'The argument value for arg1 is {args.arg1}')
    ```

    """

    commands: dict[str, type[CliCommand]] = {}
    name = None  # Set by @register decorator for subclasses.
    help_ = None  # Set by @register from first line of docstring.

    # --------------------------------------------------------------------------
    @classmethod
    def register(cls, name: str) -> Callable:
        """
        Register a CLI command handler class.

        This is a decorator. Usage is:

        ```python
        @CliCommand.register('my_command')
        class MyCommand(CliCommand):
            ...
        ```

        The help for the command is taken from the first line of the docstring.
        """

        def decorate(cmd: type[CliCommand]):
            """Register the command handler class."""
            cmd.name = name
            try:
                cmd.help_ = cmd.__doc__.splitlines()[0]
            except (AttributeError, IndexError):
                raise Exception(f'Class {cmd.__name__} must have a docstring')
            cls.commands[name] = cmd
            return cmd

        return decorate

    # --------------------------------------------------------------------------
    def __init__(self, subparser) -> None:
        """Initialize the command handler."""
        self.argp = subparser.add_parser(self.name, help=self.help_, description=self.help_)
        self.argp.set_defaults(handler=self)

    # --------------------------------------------------------------------------
    def add_arguments(self):  # noqa B027
        """Add arguments to the command handler."""
        pass

    # --------------------------------------------------------------------------
    @staticmethod  # noqa B027
    def check_arguments(args: Namespace):
        """
        Validate arguments.

        :param args:        The namespace containing the arguments.
        :raise ValueError:  If the arguments are invalid.
        """

        pass

    # --------------------------------------------------------------------------
    @staticmethod
    @abstractmethod
    def execute(args: Namespace) -> None:
        """Execute the CLI command with the specified arguments."""
        raise NotImplementedError('execute')


# ------------------------------------------------------------------------------
def add_rendering_param_args(argp: ArgumentParser) -> None:
    """
    Add the standard docma rendering CLI arguments to an argument parser.

    Docma can have rendering parameters specified on the command line in a
    number of ways:
    *   As name=value
    *   As name=file-containing-list
    *   As a JSON or YAML file containing values.

    :param argp:    Argument parser.
    """

    renderp = argp.add_argument_group('rendering parameter options')

    renderp.add_argument(
        '-f',
        '--file',
        action='append',
        metavar='FILE',
        help=(
            'Get rendering parameters from the specified file. File names  with'
            ' a .json or .jsn suffix are assumed to be in JSON format, otherwise'
            ' YAML format is assumed. Any parameters specified by -p/--param'
            ' options or -l/--list options will override values in the param file.'
            ' Can be specified multiple times.'
        ),
    )

    renderp.add_argument(
        '-l',
        '--list',
        action=StoreNameValuePair,
        metavar='name=FILE',
        help=(
            'Get the values of a list rendering parameter from the specified file,'
            ' one value per line. Multiple list parameters can be specified using'
            ' multiple -l/--list arguments.'
        ),
    )

    renderp.add_argument(
        '-p',
        '--param',
        action=StoreNameValuePair,
        metavar='name=VALUE',
        help=(
            'Set the value of a rendering parameter to be fed in to the document'
            ' generator. Multiple parameters can be specified using multiple'
            ' -p/--param arguments.'
        ),
    )


# ------------------------------------------------------------------------------
def marshal_rendering_params(args: Namespace) -> dict[str, Any]:
    """
    Marshal rendering parameters provided on the command line.

    :param args:        The argparse arguments namespace from the CLI.
    :return:            Jinja rendering parameters.
    """

    render_params = {}
    if args.file:
        for paramfile in (Path(f) for f in args.file):
            loader = json.loads if paramfile.suffix.lower() in ('.json', '.jsn') else yaml.safe_load
            deep_update_dict(render_params, loader(paramfile.read_text()))
    if args.param:
        deep_update_dict(render_params, args.param)
    if args.list:
        for k, listfile in args.list.items():
            if listfile == '-':
                render_params[k] = [s.strip() for s in sys.stdin.readlines()]
                continue
            listpath = Path(listfile)
            if listpath.suffix in ('.json', '.jsn', '.jsonl', '.jsnl'):
                raise NotImplementedError('JSON List')
            with open(listfile) as fp:
                render_params[k] = [s.strip() for s in fp.readlines()]

    return render_params
