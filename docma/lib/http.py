"""HTTP utilities."""

from __future__ import annotations

import requests
from cachetools import LRUCache, cached
from cachetools.keys import hashkey

HTTP_CACHE_SIZE = 128
HTTP_TIMEOUT = 20  # seconds


# ------------------------------------------------------------------------------
@cached(cache=LRUCache(maxsize=HTTP_CACHE_SIZE), key=lambda url, *args, **kwargs: hashkey(url))
def get_url(url: str, max_size: int = 0, timeout: int = HTTP_TIMEOUT) -> bytes:
    """
    Fetch a URL and return its contents.

    Results are cached, based only on the URL.

    :param url:         The URL to fetch.
    :param max_size:    The maximum allowed size of the object being fetched.
                        If 0, no limit is applied.
    :param timeout:     Timeout in seconds on HTTP operations
    :return:            The object being fetched as bytes.
    """

    if max_size:
        response = requests.head(url, timeout=timeout)
        if not response.ok:
            raise Exception(f'{url}: {response.reason}')

        try:
            size = int(response.headers['Content-Length'])
        except KeyError:
            raise Exception(f'{url}: Cannot get content length')
        if size > max_size:
            raise Exception(f'{url}: Too large ({max_size} bytes)')

    response = requests.get(url, timeout=timeout)
    if not response.ok:
        raise Exception(f'{url}: {response.reason}')
    return response.content
