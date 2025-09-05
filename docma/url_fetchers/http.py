"""Fetch s3://... URLs for WeasyPrint."""

from __future__ import annotations

from functools import lru_cache
from mimetypes import guess_type
from typing import Any
from urllib.parse import ParseResult

import requests

from docma.config import IMPORT_MAX_SIZE
from docma.exceptions import DocmaUrlFetchError
from docma.lib.core import DocmaRenderContext
from .__common__ import fetcher


# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
@lru_cache(maxsize=10)
@fetcher('http', 'https')
def http_url_fetcher(purl: ParseResult, context: DocmaRenderContext) -> dict[str, Any]:
    """
    Fetch http(s)://... URLs.

    We provide our own fetcher for HTTP/HTTPS rather than rely on the WeasyPrint
    default fetcher for predictability and also for use in HTML rendering.

    :param purl:    A parsed URL. See urllib.parse.urlparse().
    :param context: Document rendering context. Not used in this handler.

    :return:        A dict containing the URL content and mime type.
    """

    response = requests.head(purl.geturl(), timeout=5)

    if not response.ok:
        raise DocmaUrlFetchError(f'{purl.geturl()}: {response.status_code} - {response.reason}')
    try:
        content_type = response.headers['Content-Type']
    except KeyError:
        content_type = guess_type(purl.path)[0]

    if not content_type:
        raise DocmaUrlFetchError(f'{purl.geturl()}: Cannot get content type')

    # Check it for size -- may or may not have a Content-Length header
    content_len = int(response.headers.get('Content-Length', -1))
    if content_len > IMPORT_MAX_SIZE:
        raise DocmaUrlFetchError(f'{purl.geturl()}: Too large')

    # Download
    response = requests.get(purl.geturl(), timeout=30)
    if not response.ok:
        raise DocmaUrlFetchError(f'{purl.geturl()}: {response.status_code} - {response.reason}')

    if len(response.content) > IMPORT_MAX_SIZE:
        raise DocmaUrlFetchError(f'{purl.geturl()}: Too large')

    return {'string': response.content, 'mime_type': content_type}
