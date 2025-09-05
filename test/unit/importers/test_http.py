"""Test HTTP importer."""

from __future__ import annotations

import pytest

from docma.importers import import_content
from docma.exceptions import DocmaImportError


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('filename', ['README.md', 'images/qr-magenta-hello-world.png'])
def test_import_http_ok(filename, td, tc):

    assert (
        import_content(f'http://{tc.web_server.netloc}/data/{filename}')
        == (td / filename).read_bytes()
    )


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('filename', ['bad-file', 'bad-dir/qr-magenta-hello-world.png'])
def test_import_http_fail(filename, td, tc):

    with pytest.raises(DocmaImportError, match='File not found'):
        import_content(f'http://{tc.web_server.netloc}/data/{filename}')


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('filename', ['README.md', 'images/qr-magenta-hello-world.png'])
def test_import_http_too_big(filename, td, tc):

    with pytest.raises(DocmaImportError, match='Too large'):
        import_content(f'http://{tc.web_server.netloc}/data/{filename}', max_size=1)
