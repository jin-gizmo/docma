"""Tests for docma.data_providers.__common__."""

from __future__ import annotations

import json

import pytest  # noqa

from docma.data_providers import load_data
from docma.data_providers.__common__ import data_provider_for_src_type
from docma.data_providers.db import *
from docma.exceptions import DocmaDataProviderError
from docma.jinja import DocmaRenderContext
from docma.lib.packager import PackageReader


# ------------------------------------------------------------------------------
def test_datasourcespec(tc):
    dsp1 = DataSourceSpec(
        src_type='postgres',
        location=tc.postgres.id,
        query='queries/custard.yaml',
        target='whatever',
    )
    dsp2_s = f'postgres;{tc.postgres.id};queries/custard.yaml;whatever'
    dsp2 = DataSourceSpec.from_string(dsp2_s)
    assert dsp1 == dsp2
    assert str(dsp2) == dsp2_s == str(dsp1)

    with pytest.raises(ValueError, match='type and location required'):
        DataSourceSpec(
            src_type='postgres',
            location=None,  # noqa
            query='queries/custard.yaml',
            target='whatever',
        )

    with pytest.raises(ValueError, match='type and location required'):
        DataSourceSpec.from_string(';a;b;c')


# ------------------------------------------------------------------------------
def test_data_provider_for_src_type():
    with pytest.raises(DocmaDataProviderError, match='Unknown data provider type'):
        data_provider_for_src_type('no-such-type')


# ------------------------------------------------------------------------------
def test_load_data_ok(tc, td, dirs):

    dsp = DataSourceSpec(
        src_type='postgres',
        location=tc.postgres.id,
        query='queries/custard.yaml',
        target='whatever',
    )

    context = DocmaRenderContext(
        tpkg=PackageReader.new(dirs.templates / 'test1.src'),
        params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
    )
    data = load_data(dsp, context)
    assert data


# ------------------------------------------------------------------------------
def test_data_loader_bad_content_fail(td, tmp_path) -> None:

    data_file = tmp_path / 'bad-data.jsonl'
    with data_file.open('w') as fp:
        json.dump('Bad data - expecting a dict', fp)
        print(file=fp)

    with pytest.raises(DocmaDataProviderError, match='Bad data - must be a list of dicts'):
        load_data(
            DataSourceSpec(src_type='file', location='bad-data.jsonl'),
            DocmaRenderContext(PackageReader.new(tmp_path)),
        )
