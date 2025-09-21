"""Test docma URL fetcher."""

from __future__ import annotations

from urllib.parse import urlencode, urlparse, urlunparse

import pytest

from docma.exceptions import DocmaUrlFetchError
from docma.jinja import DocmaRenderContext
from docma.lib.packager import PackageReader
from docma.url_fetchers.docma import docma_url_fetcher
from utils import images_are_identical


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'options, result_file',
    [
        (
            {
                'width': 100,
                'height': 50,
                'color': '#00ffff',
            },
            'swatch-cyan-100x50.png',
        ),
        (
            {
                'width': 100,
                'height': 50,
                'color': '#0000ff',
                'text': 'Hello world!',
                'text_color': 'yellow',
                'font': 'Arial',
                'font_size': 16,
            },
            'swatch-blue-100x50-hello-world.png',
        ),
    ],
)
def test_docma_url_fetcher_ok(options: dict, result_file: str, td):
    purl = urlparse(urlunparse(('docma', '', 'swatch', '', urlencode(options), '')))
    result = docma_url_fetcher(purl, DocmaRenderContext(PackageReader.new(td)))

    assert result['mime_type'] == 'image/png'
    assert images_are_identical(result['string'], td / 'images' / result_file)

    # assert result == {
    #     'string': (td / 'images' / result_file).read_bytes(),
    #     'mime_type': 'image/png',
    # }


# ------------------------------------------------------------------------------
def test_docma_url_fetcher_fail(td):
    purl = urlparse('docma://should.not.have.netloc/swatch?width=100&height=50')
    with pytest.raises(DocmaUrlFetchError):
        docma_url_fetcher(purl, DocmaRenderContext(PackageReader.new(td)))
