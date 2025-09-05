"""Test `docma new` command."""

from __future__ import annotations

import sys
from uuid import uuid4

import yaml

from docma.cli import docma


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
