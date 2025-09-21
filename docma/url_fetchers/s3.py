"""Fetch s3://... URLs for WeasyPrint."""

from __future__ import annotations

from functools import lru_cache
from mimetypes import guess_type
from typing import Any
from urllib.parse import ParseResult

import boto3

from docma.config import IMPORT_MAX_SIZE
from docma.exceptions import DocmaUrlFetchError
from docma.jinja import DocmaRenderContext
from .__common__ import fetcher


# ------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def s3resource():
    """Get a singleton boto3 S3 resource."""
    return boto3.Session().resource('s3')


# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
@fetcher('s3')
def s3_url_fetcher(purl: ParseResult, context: DocmaRenderContext) -> dict[str, Any]:
    """
    Fetch s3://... URLs for WeasyPrint.

    :param purl:    A parsed URL. See urllib.parse.urlparse().
    :param context: Document rendering context. Not used in this handler.

    :return:        A dict containing the URL content and mime type.
    """

    s3obj = s3resource().Bucket(purl.netloc).Object(purl.path.lstrip('/'))

    try:
        content_len = s3obj.content_length
    except Exception as e:
        raise DocmaUrlFetchError(f'{purl.geturl()}: {e}') from e
    if content_len > IMPORT_MAX_SIZE:
        raise DocmaUrlFetchError(f'{purl.geturl()}: Too large')

    try:
        return {
            'string': s3obj.get()['Body'].read(),
            'mime_type': guess_type(purl.path)[0],
        }
    except Exception as e:
        raise DocmaUrlFetchError(f'{purl.geturl()}: {e}') from e
