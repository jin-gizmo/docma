"""Common components for content generators."""

from __future__ import annotations

from functools import lru_cache
from typing import Callable
from urllib.parse import urlparse

from docma.config import IMPORT_CACHE_SIZE
from docma.exceptions import DocmaImportError

_CONTENT_IMPORTERS = {}


# ------------------------------------------------------------------------------
def content_importer(*schemes: str) -> Callable:
    """
    Register document importers for the specified URL schemes.

    This is a decorator used like so:

    ```python
    @content_importer('http', 'https')
    def http(url: str) -> bytes:
        ...
    ```

    """

    def decorate(func: Callable) -> Callable:
        """Register the handler function."""
        for scheme in schemes:
            _CONTENT_IMPORTERS[scheme] = func
        return func

    return decorate


# ------------------------------------------------------------------------------
@lru_cache(maxsize=IMPORT_CACHE_SIZE)
def import_content(url: str, max_size: int = 0) -> bytes:
    """
    Import the content from the specified URL style source.

    :param url:         The URL from which to import.
    :param max_size:    The maximum size in bytes of the object. Default is 0
                        (no limit).
    """

    try:
        import_handler = _CONTENT_IMPORTERS[urlparse(url).scheme]
    except KeyError:
        raise DocmaImportError(f'{url}: No importer available')

    try:
        content = import_handler(url, max_size=max_size)
    except Exception as e:
        raise DocmaImportError(str(e)) from e

    # In case the importer itself doesn't enforce
    if max_size and len(content) > max_size:
        raise DocmaImportError(f'{url}: Too large')

    return content
