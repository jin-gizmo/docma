"""Tests for docma.data_providers.params."""

from __future__ import annotations

import pytest

from docma.data_providers.params import *
from docma.exceptions import DocmaDataProviderError
from docma.lib.core import DocmaRenderContext
from docma.lib.packager import PackageReader


# ------------------------------------------------------------------------------
def test_params_loader_ok(td) -> None:
    params = {
        'x': {
            'y': [
                {'a': 'A1', 'b': 'B1'},
                {'a': 'A2', 'b': 'B2'},
            ]
        }
    }
    data = params_loader(
        DataSourceSpec(src_type='params', location='x.y'),
        DocmaRenderContext(PackageReader.new(td), params),
    )

    assert len(data) == len(params['x']['y'])
    assert all(d == p for d, p in zip(data, params['x']['y']))


# ------------------------------------------------------------------------------
def test_params_loader_query_not_allowed_fail(td) -> None:
    with pytest.raises(DocmaDataProviderError, match='Query not allowed'):
        params_loader(
            DataSourceSpec(src_type='params', location='irrelevant', query='some-query.yaml'),
            DocmaRenderContext(PackageReader.new(td)),
        )


# ------------------------------------------------------------------------------
def test_params_loader_not_a_list_fail(td) -> None:
    params = {
        'x': {
            'y': {'a': 'A1', 'b': 'B1'},
        }
    }

    with pytest.raises(DocmaDataProviderError, match='not a list'):
        params_loader(
            DataSourceSpec(src_type='params', location='x.y'),
            DocmaRenderContext(PackageReader.new(td), params),
        )
