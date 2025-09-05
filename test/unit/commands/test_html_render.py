"""Test `docma html` command."""

from __future__ import annotations

import json
import sys

import pytest
from bs4 import BeautifulSoup

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
def test_cmd_html_render_ok(location, hello, dirs, monkeypatch, tmp_path):
    # Prep a compiled template to play with
    src_dir = dirs.templates / 'test2.src'
    template_dir = tmp_path / 'test2.template'
    compile_template(src_dir, str(template_dir))
    html_output = tmp_path / 'test2.html'
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
            'html',
            '--template',
            str(template_dir),
            '--output',
            str(html_output),
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
    assert html_output.is_file() and html_output.stat().st_size > 0
    html = BeautifulSoup(html_output.read_text(), 'html.parser')
    assert html.head.title.text.strip() == 'Welcome to docma!'
    assert f'Hello {hello}' in html.body.text


# ------------------------------------------------------------------------------
def test_cmd_bad_compression_fail(dirs, monkeypatch, tmp_path, capsys):
    # Prep a compiled template to play with
    src_dir = dirs.templates / 'test2.src'
    template_dir = tmp_path / 'test2.template'
    compile_template(src_dir, str(template_dir))
    pdf_output = tmp_path / 'test2.pdf'

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
            '--compress',
            '11',
        ],
    )
    with pytest.raises(SystemExit):
        docma.main()

    assert 'compression must be between 0 and 9' in capsys.readouterr().err
