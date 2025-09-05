"""Test `docma pdf-batch` command."""

from __future__ import annotations

import json
import sys

import pytest
from bs4 import BeautifulSoup

from docma import compile_template
from docma.cli import docma


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'batch_data_spec',
    ['params;data.custard', 'postgres;pglocal;queries/batch.yaml'],
)
def test_cmd_html_render_batch_ok(
    batch_data_spec, dirs, td, monkeypatch, tmp_path
):
    doc_count = 10  # Max # docs to generate. Could be less if not enough batch data.
    # Prep a compiled template to play with
    src_dir = dirs.templates / 'test3.src'
    template_dir = tmp_path / 'test3.template'
    compile_template(src_dir, str(template_dir))
    output_dir = tmp_path / 'output'
    output_dir.mkdir()

    # This is a hack to force the env to be returned to not having LAVA_REALM
    # env var set at the end of the test case as --realm mods the environment.
    monkeypatch.setenv('LAVA_REALM', 'wotcha')
    monkeypatch.setattr(
        sys,
        'argv',
        [
            '*',
            'html-batch',
            '--template',
            str(template_dir),
            '--output',
            str(output_dir),
            '--realm',
            'whatever',
            '--output',
            f'{output_dir}' '/{{ id }}-{{ givenname }}.html',
            '--data-source-spec',
            batch_data_spec,
            '--no-progress',
            '--param',
            f'doc_count={doc_count}',
        ],
    )
    docma.main()
    # Load our comparison data - need some rows keyed on output filename stem
    base_data = {}
    with open(td / 'custard100.jsonl') as fp:
        for _ in range(doc_count):
            batch_row = json.loads(next(fp))
            base_data['{ID}-{GivenName}'.format(**batch_row)] = batch_row

    for html_path in output_dir.glob('*.html'):
        html = BeautifulSoup(html_path.read_text(), 'html.parser')
        assert (
            '{GivenName} {FamilyName} likes {FavouriteCustard}'.format(**base_data[html_path.stem])
            in html.body.text
        )
