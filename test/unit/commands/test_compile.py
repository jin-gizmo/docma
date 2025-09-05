"""Test `docma compile` command."""

from __future__ import annotations

import sys

from docma.cli import docma


# ------------------------------------------------------------------------------
def test_cmd_compile_ok(dirs, monkeypatch, tmp_path):

    src_dir = dirs.templates / 'test1.src'

    monkeypatch.setattr(
        sys,
        'argv',
        [
            '*',
            'compile',
            '--input',
            str(src_dir),
            '--template',
            str(tmp_path),
        ],
    )
    docma.main()
    assert (tmp_path / 'config.yaml').exists()
