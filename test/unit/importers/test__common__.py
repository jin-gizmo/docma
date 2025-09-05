"""Tests for docma.importers.__common__."""

import pytest

from docma.exceptions import DocmaImportError
from docma.importers import content_importer, import_content


# ------------------------------------------------------------------------------
def test_import_content_fail_unknown_scheme():
    with pytest.raises(DocmaImportError, match='No importer available'):
        import_content('bad-scheme://blah.blah')


# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
@content_importer('dummy')
def dummy_importer(url: str, max_size: int = 0):
    """Just return the URL as if it was the content (ignoring size)."""

    return url


def test_import_content_fail_too_big():
    with pytest.raises(DocmaImportError, match='Too large'):
        import_content('dummy://blah.blah', 1)
