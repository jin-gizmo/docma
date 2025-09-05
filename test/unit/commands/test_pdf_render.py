"""Test `docma pdf` command."""

from __future__ import annotations

import json
import sys

import pytest
from pypdf import PdfReader

from docma import compile_template
from docma.cli import docma


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'location, hello',
    [
        ('local', 'world'),
        ('http', 'earth'),
    ],
)
def test_cmd_pdf_render_ok(location, hello, dirs, monkeypatch, tmp_path):
    # Prep a compiled template to play with
    src_dir = dirs.templates / 'test2.src'
    template_dir = tmp_path / 'test2.template'
    compile_template(src_dir, str(template_dir))
    pdf_output = tmp_path / 'test2.pdf'
    # Setup a file containing rendering params.
    params_file = tmp_path / 'params.json'
    params_file.write_text(json.dumps({'hello_who': hello}))

    # This is a hack to force the env to be returned to not having LAVA_REALM
    # env var set at the end of the test case as --realm mods the environment.
    monkeypatch.setenv('LAVA_REALM', 'wotcha')
    monkeypatch.setattr(
        sys,
        'argv',
        [
            '*',
            'pdf',
            '--template',
            str(template_dir),
            '--output',
            str(pdf_output),
            '--realm',
            'whatever',
            '--param',
            f'doc_location={location}',
            '--list',
            'empty=/dev/null',
            '--file',
            str(params_file),
        ],
    )
    docma.main()
    assert pdf_output.is_file() and pdf_output.stat().st_size > 0
    pdf = PdfReader(str(pdf_output))
    assert f'Hello {hello}' in pdf.pages[0].extract_text()


# ------------------------------------------------------------------------------
def test_cmd_pdf_render_bad_compression_fail(dirs, monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(
        sys, 'argv', ['*', 'pdf', '--template', '*', '--output', '*', '--compress', '11']
    )
    with pytest.raises(SystemExit):
        docma.main()

    assert 'compression must be between 0 and 9' in capsys.readouterr().err
