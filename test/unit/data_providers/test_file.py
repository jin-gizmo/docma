"""Tests for docma.data_providers.file."""

from __future__ import annotations

import pytest  # noqa

from docma.data_providers.file import *
from docma.exceptions import DocmaDataProviderError
from docma.jinja import DocmaRenderContext
from docma.lib.packager import PackageReader


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename,rows',
    [
        ('custard100.csv', 100),
        ('custard100.jsonl', 100),
    ],
)
def test_file_loader_ok(filename: str, rows: int, td) -> None:
    data = file_loader(
        DataSourceSpec(src_type='file', location=filename),
        DocmaRenderContext(PackageReader.new(td)),
    )

    assert len(data) == rows


# ------------------------------------------------------------------------------
def test_file_loader_bad_suffix_fail(td) -> None:
    with pytest.raises(DocmaDataProviderError, match='Unknown file type'):
        file_loader(
            DataSourceSpec(src_type='file', location='unknown-suffix.junk'),
            DocmaRenderContext(PackageReader.new(td)),
        )


# ------------------------------------------------------------------------------
def test_file_loader_query_not_allowed_fail(td) -> None:
    with pytest.raises(DocmaDataProviderError, match='Query not allowed'):
        file_loader(
            DataSourceSpec(src_type='file', location='irrelevant', query='some-query.yaml'),
            DocmaRenderContext(PackageReader.new(td)),
        )


# ------------------------------------------------------------------------------
def test_file_loader_query_no_file_fail(td) -> None:
    with pytest.raises(FileNotFoundError, match=' No such file'):
        file_loader(
            DataSourceSpec(src_type='file', location='no-such-file.csv'),
            DocmaRenderContext(PackageReader.new(td)),
        )
