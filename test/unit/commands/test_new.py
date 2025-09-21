"""Test `docma new` command."""

from __future__ import annotations

import os
import sys
from uuid import uuid4

import pytest
import yaml

from docma.cli import docma
from docma.commands.new import pythonpath_prepended


# ------------------------------------------------------------------------------
def test_cmd_new_ok(monkeypatch, tmp_path):

    # Generate some random param values.
    description = str(uuid4())
    owner = str(uuid4())
    new_dir = tmp_path / 'new'

    monkeypatch.setattr(
        sys,
        'argv',
        [
            '*',
            'new',
            '--no-input',
            '--param',
            f'description={description}',
            '--param',
            f'owner={owner}',
            str(new_dir),
        ],
    )
    docma.main()
    assert new_dir.is_dir()
    config = yaml.safe_load((new_dir / 'config.yaml').read_text())
    assert config['description'] == description
    assert config['owner'] == owner


# ------------------------------------------------------------------------------
def test_cmd_new_fail(monkeypatch, tmp_path, capsys):

    # Generate some random param values.
    description = str(uuid4())
    owner = str(uuid4())
    new_dir = tmp_path

    monkeypatch.setattr(
        sys,
        'argv',
        [
            '*',
            'new',
            '--no-input',
            '--param',
            f'description={description}',
            '--param',
            f'owner={owner}',
            str(new_dir),
        ],
    )
    result = docma.main()
    assert result == 1
    assert f'{new_dir} already exists' in capsys.readouterr().err


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'pythonpath',
    [
        None,
        'path1:path2',
    ],
)
def test_pythonpath_prepended(pythonpath, monkeypatch, tmp_path):
    if pythonpath:
        monkeypatch.setenv('PYTHONPATH', pythonpath)  # noqa
    else:
        monkeypatch.delenv('PYTHONPATH', raising=False)

    existing_pythonpath = os.environ.get('PYTHONPATH')
    with pythonpath_prepended('some/path'):
        assert os.environ.get('PYTHONPATH') == (
            f'some/path:{existing_pythonpath}' if existing_pythonpath else 'some/path'
        )

    # Confirm path restored
    assert os.environ.get('PYTHONPATH') == existing_pythonpath
