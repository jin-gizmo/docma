"""Test __common__.py."""

import sys
from argparse import Namespace
from io import StringIO

import pytest  # noqa

from docma.commands import CliCommand
from docma.commands.__common__ import marshal_rendering_params


# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
def test_cli_command_no_docstring():

    with pytest.raises(Exception, match='must have a docstring'):

        @CliCommand.register('no-docstring')
        class TestCommand(CliCommand):
            def execute(self, args: Namespace) -> None:
                pass


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'args,expected',
    [
        (
            Namespace(
                # This gets turned into a list of filenames with these contents
                file={
                    'f1.yaml': """
a: b
l2: ['this', 'will', 'be', 'overridden']
l3: [1, 2, 3]
                        """,
                    'f2.json': """
{
    "c": "d",
    "l2": [ "this", "will", "be", "overridden" ],
    "l3": [ 10, 20, 30 ]
}
                    """,
                },
                param={
                    'l1': ['this', 'will', 'be', 'overridden'],
                    'p1': 'Hello world',
                },
                list={
                    # These need to be put in files to be processed
                    'l1': ['a', 'b'],
                    # This one will be stdin
                    '-l2': ['from', 'stdin'],
                    'l4': ['x', 'y'],
                },
            ),
            # . . . . . . . . . .
            {
                'a': 'b',  # From f1
                'c': 'd',  # From f2
                'l1': ['a', 'b'],  # From l1
                'l2': ['from', 'stdin'],  # l2 (stdin)
                'l3': [10, 20, 30],  # Fron f2
                'l4': ['x', 'y'],  # From l4
                'p1': 'Hello world',  # From p1
            },
        )
        # ------------------------------
    ],
)
def test_marshal_rendering_params(args, expected, tmp_path, monkeypatch):
    """
    Test parameter marshalling / merging.

    This is a bit of half-hearted test. Doesn't really test deep merging well.
    """
    # First need to convert the file and list items into references to files.
    param_files = []
    for k, v in args.file.items():  # noqa
        param_file = tmp_path / k
        param_file.write_text(v)
        param_files.append(param_file)
    args.file = param_files

    stdin = ''
    for k, v in list(args.list.items()):
        list_content = '\n'.join(v) + '\n'
        if k.startswith('-'):
            # This list will be fed from stdin
            args.list[k[1:]] = '-'
            del args.list[k]
            stdin = list_content
            continue
        (tmp_path / k).write_text(list_content)
        args.list[k] = str(tmp_path / k)

    monkeypatch.setattr(sys, 'stdin', StringIO(stdin))
    assert marshal_rendering_params(args) == expected
