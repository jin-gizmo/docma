"""Test `docma info` command."""

from __future__ import annotations

import sys

import yaml

from docma import compile_template
from docma.cli import docma
from docma.version import __version__


# ------------------------------------------------------------------------------
def test_cmd_info_ok(monkeypatch, dirs, tmp_path, capsys):
    src_dir = dirs.templates / 'test1.src'
    config = yaml.safe_load((src_dir / 'config.yaml').read_text())
    compile_template(src_dir, str(tmp_path))
    monkeypatch.setattr(sys, 'argv', ['*', 'info', '--template', str(tmp_path)])
    docma.main()
    stdout = capsys.readouterr().out
    assert f'description: {config["description"]}\n' in stdout
    assert f'docma_compiler_version: {__version__}\n' in stdout
