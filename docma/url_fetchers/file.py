"""Fetch file:... URLs for WeasyPrint from the document template package."""

from __future__ import annotations

from mimetypes import guess_type
from typing import Any
from urllib.parse import ParseResult

from docma.exceptions import DocmaUrlFetchError
from docma.jinja import DocmaRenderContext
from .__common__ import fetcher


# ------------------------------------------------------------------------------
@fetcher('file')
def file_url_fetcher(purl: ParseResult, context: DocmaRenderContext) -> dict[str, Any]:
    """
    Fetch file:... URLs for WeasyPrint from the document template package.

    :param purl:    A parsed URL. See urllib.parse.urlparse().
    :param context: Document rendering context.

    :return:        A dict containing the URL content and mime type.
    """

    if purl.netloc:
        # We log here as well as raise because Weasyprint suppresses errors
        raise DocmaUrlFetchError(
            f'{purl.geturl()}: Local files must be referenced as file:path, not file://path'
        )

    try:
        return {
            'string': context.tpkg.read_bytes(purl.path),
            'mime_type': guess_type(purl.path)[0],
        }
    except Exception as e:
        raise DocmaUrlFetchError(f'{purl.geturl()}: {e}') from e
