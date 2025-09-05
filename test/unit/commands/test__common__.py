"""Test __common__.py."""

from argparse import Namespace

import pytest

from docma.commands import CliCommand


# ------------------------------------------------------------------------------
def test_cli_command_no_docstring():

    with pytest.raises(Exception, match='must have a docstring'):

        @CliCommand.register('no-docstring')
        class TestCommand(CliCommand):
            def execute(self, args: Namespace) -> None:
                pass
