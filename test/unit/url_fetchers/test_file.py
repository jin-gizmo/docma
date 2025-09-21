"""Test file based URL fetcher."""

from __future__ import annotations

from urllib.parse import urlparse

import pytest

from docma.exceptions import DocmaUrlFetchError
from docma.jinja import DocmaRenderContext
from docma.lib.packager import PackageReader
from docma.url_fetchers import get_url_fetcher_for_scheme


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename,mime_type',
    [
        ('custard100.csv', 'text/csv'),
        ('images/swatch-cyan-100x50.png', 'image/png'),
    ],
)
def test_file_url_fetcher_ok(filename: str, mime_type: str, td):
    purl = urlparse(f'file:{filename}')
    fetcher = get_url_fetcher_for_scheme(purl.scheme)
    url_info = fetcher(purl, DocmaRenderContext(PackageReader.new(td)))
    assert url_info['string'] == (td / filename).read_bytes()
    assert url_info['mime_type'] == mime_type


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'url,error',
    [
        ('file://whatever.txt', 'file:path, not file://path'),
        ('file:no-such-file.txt', 'No such file or directory'),
    ],
)
def test_file_url_fetcher_fail(url: str, error: str, td):
    purl = urlparse(url)
    with pytest.raises(DocmaUrlFetchError, match=error):
        fetcher = get_url_fetcher_for_scheme(purl.scheme)
        fetcher(purl, DocmaRenderContext(PackageReader.new(td)))
