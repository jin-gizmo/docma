"""Tests for docma.lib.http."""

from __future__ import annotations

from urllib.parse import urlunparse

import pytest

from docma.lib.http import *


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename, max_size',
    # Watch out for get_url() cacheing here!
    [
        ('README.md', 0),
        ('custard100.csv', 100000),
    ],
)
def test_get_url_ok(filename: str, max_size: int, tc, td):
    url = str(urlunparse(('http', tc.web_server.netloc, f'/data/{filename}', None, None, None)))
    assert get_url(url, max_size=max_size) == (td / filename).read_bytes()


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename, max_size, error',
    # Watch out for get_url() cacheing here!
    [
        ('total-usage-by-day.csv', 1, 'Too large'),
        ('No-such-file', 0, 'File not found'),
        ('Does-not-exist', 1, 'File not found'),
    ],
)
def test_get_url_fail(filename: str, max_size: int, error: str, tc, td):
    url = str(urlunparse(('http', tc.web_server.netloc, f'/data/{filename}', None, None, None)))
    with pytest.raises(Exception, match=error):
        get_url(url, max_size=max_size)


# ------------------------------------------------------------------------------

def test_get_url_no_size():

    with pytest.raises(Exception, match='Cannot get content length'):
        get_url('https://httpbin.org/stream-bytes/100', max_size=1000, timeout=5)
