"""Test the docma main CLI entry point."""

import sys

import pytest

from docma import __version__
from docma.cli import docma
from subprocess import check_output


# ------------------------------------------------------------------------------
def test_docma_cli_version(capsys, monkeypatch) -> None:
    """Test the "version" command."""

    monkeypatch.setattr(sys, 'argv', ['docma', '--version'])

    # argparse will exit on it's own for --version option (grrr)
    with pytest.raises(SystemExit) as exc_info:
        docma.main()

    assert exc_info.value.code == 0
    assert capsys.readouterr().out.strip() == __version__


# ------------------------------------------------------------------------------
def test_docma_cli_cmd_ok(monkeypatch, tmp_path) -> None:
    """
    Test the successful invocation of a command.

    We are not actually testing the command itself but rather the invocation
    sequence for a successful command.
    """

    new_dir = tmp_path / 'new'
    monkeypatch.setattr(
        sys,
        'argv',
        [
            'docma',
            'new',
            '--no-input',
            '--param',
            'description=Something',
            '--param',
            'owner=Someone',
            str(new_dir),
        ],
    )

    assert docma.main() == 0
    assert new_dir.is_dir()
    assert (new_dir / 'config.yaml').exists()


# ------------------------------------------------------------------------------
def test_docma_cli_cmd_fail(capsys, monkeypatch, tmp_path) -> None:
    """
    Test the invocation of the "new" command.

    We are not actually testing the new command itself but rather the invocation
    sequence for a successful command.
    """

    # We create a file and try to run the "new" command over the top of it.
    # This should fail.
    new_file = tmp_path / 'a_file'
    new_file.write_text('hello')

    monkeypatch.setattr(sys, 'argv', ['docma', '--no-colour', 'new', '--no-input', str(new_file)])

    assert docma.main() == 1
    assert capsys.readouterr().err.strip() == f'{new_file} already exists'


# ------------------------------------------------------------------------------
def test_docma_cli_cmd_args_fail_validation(capsys, monkeypatch, tmp_path) -> None:
    """Test CLI invocation with invalid args for a subcommand."""

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'docma',
            '--no-colour',
            'pdf',
            '-t',
            'whatever.zip',
            '--output',
            str(tmp_path / 'does-not-matter.pdf'),
            '--compress',
            # 300 is invalid -- must be 0..9
            '300',
        ],
    )
    with pytest.raises(SystemExit) as exc_info:
        docma.main()
    assert exc_info.value.code == 2
    assert 'compression must be between 0 and 9' in capsys.readouterr().err.strip()


# ------------------------------------------------------------------------------
def test_docma_cli_normal_invocation():

    result = check_output([sys.executable, '-m', 'docma.cli.docma', '--version'])
    assert result.decode('utf-8').strip() == __version__
