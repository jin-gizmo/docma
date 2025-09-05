"""Import web document content."""

from __future__ import annotations

from docma.config import IMPORT_URL_TIMEOUT
from docma.lib.http import get_url
from .__common__ import content_importer


# ------------------------------------------------------------------------------
@content_importer('http', 'https')
def http(url: str, max_size: int = 0) -> bytes:
    """Get an object from the web (cached)."""

    return get_url(url, max_size=max_size, timeout=IMPORT_URL_TIMEOUT)
