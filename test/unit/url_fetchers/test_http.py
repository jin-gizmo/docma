"""Test HTTP URL fetcher."""

from __future__ import annotations

from urllib.parse import ParseResult

import pytest  # noqa

from docma.config import IMPORT_MAX_SIZE
from docma.exceptions import DocmaUrlFetchError
from docma.jinja import DocmaRenderContext
from docma.lib.packager import PackageReader
from docma.url_fetchers import get_url_fetcher_for_scheme


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename,mime_type',
    [
        ('dogs.csv', 'text/csv'),
        ('images/swatch-cyan-100x50.png', 'image/png'),
    ],
)
def test_http_url_fetcher_ok(filename: str, mime_type: str, tc, td):
    # noinspection PyArgumentList
    purl = ParseResult('http', tc.web_server.netloc, f'/data/{filename}', None, None, None)
    fetcher = get_url_fetcher_for_scheme(purl.scheme)
    url_info = fetcher(purl, DocmaRenderContext(PackageReader.new(td)))
    assert url_info['string'] == (td / filename).read_bytes()
    assert url_info['mime_type'] == mime_type


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename,mime_type',
    [
        ('dogs.csv', 'text/csv'),
    ],
)
def test_http_url_fetcher_too_big(filename: str, mime_type: str, tc, td):

    # noinspection PyArgumentList
    purl = ParseResult(
        scheme='http',
        netloc=tc.web_server.netloc,
        path=f'/data/{filename}',
        params=None,
        # Our test server allows us to manipulate response headers
        query=f'header=Content-Length/{IMPORT_MAX_SIZE+1}',
        fragment=None,
    )
    fetcher = get_url_fetcher_for_scheme(purl.scheme)
    with pytest.raises(DocmaUrlFetchError, match='Too large'):
        fetcher(purl, DocmaRenderContext(PackageReader.new(td)))


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename,mime_type',
    [
        ('dogs.csv', 'text/csv'),
        ('images/swatch-cyan-100x50.png', 'image/png'),
    ],
)
def test_http_url_fetcher_guess_content_type(filename, mime_type, tc, td):
    # noinspection PyArgumentList
    purl = ParseResult(
        scheme='http',
        netloc=tc.web_server.netloc,
        path=f'/data/{filename}',
        params=None,
        # Our test server allows us to delete response headers. This forces
        # us to guess content type at the client end.
        query='header=Content-Type/',
        fragment=None,
    )
    fetcher = get_url_fetcher_for_scheme(purl.scheme)
    url_info = fetcher(purl, DocmaRenderContext(PackageReader.new(td)))
    assert url_info['mime_type'] == mime_type


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename',
    ['no-mime-type'],
)
def test_http_url_fetcher_no_content_type(filename, tc, td):
    # noinspection PyArgumentList
    purl = ParseResult(
        scheme='http',
        netloc=tc.web_server.netloc,
        path=f'/data/{filename}',
        params=None,
        # Our test server allows us to delete response headers. This forces
        # us to guess content type at the client end which we can't do in this test.
        query='header=Content-Type/',
        fragment=None,
    )
    fetcher = get_url_fetcher_for_scheme(purl.scheme)
    with pytest.raises(DocmaUrlFetchError, match='Cannot get content type'):
        fetcher(purl, DocmaRenderContext(PackageReader.new(td)))


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename',
    ['dogs.csv'],
)
def test_http_url_fetcher_head_ok_get_fail(filename, tc, td):
    # noinspection PyArgumentList
    purl = ParseResult(
        scheme='http',
        netloc=tc.web_server.netloc,
        path=f'/data/{filename}',
        params=None,
        # Our test server allows us to delete response headers. This forces
        # us to guess content type at the client end which we can't do in this test.
        query='allow=HEAD',
        fragment=None,
    )
    fetcher = get_url_fetcher_for_scheme(purl.scheme)
    with pytest.raises(DocmaUrlFetchError, match='403'):
        fetcher(purl, DocmaRenderContext(PackageReader.new(td)))


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename',
    ['dogs.csv'],
)
def test_http_url_fetcher_server_lies_about_size(filename, tc, td, monkeypatch):
    """Test when the server says object size is ok but its really to big."""

    import docma.url_fetchers.http

    monkeypatch.setattr(docma.url_fetchers.http, 'IMPORT_MAX_SIZE', 1)

    purl = ParseResult(
        scheme='http',
        netloc=tc.web_server.netloc,
        path=f'/data/{filename}',
        params=None,
        # Our test server allows us to manipulate response headers
        # We're forcing it to not provide content length so the initial length
        # check will pass but the subsequent GET will get an oversized object.
        query=f'header=Content-Length/',
        fragment=None,
    )
    fetcher = get_url_fetcher_for_scheme(purl.scheme)
    with pytest.raises(DocmaUrlFetchError, match='Too large'):
        fetcher(purl, DocmaRenderContext(PackageReader.new(td)))
