"""Tests for the vega generator."""

from __future__ import annotations
import pytest
from pydantic import ValidationError

from docma.generators.vega import *
from docma.generators import content_generator_for_type
from docma.lib.core import DocmaRenderContext
from docma.lib.packager import PackageReader

from utils import images_are_identical


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'pre_data, post_data',
    [
        ('data', ['data']),
        (['a', 'data', 'list'], ['a', 'data', 'list']),
    ],
)
def test_vega_options_ok(pre_data, post_data):
    params = {'p1': 'v1', 'p2': 22}
    options_data = {
        'spec': 'spec',
        'data': pre_data,
        'params': json.dumps(params),
    }

    options_model = VegaOptions(**options_data)
    # Data attribute is always coerced to list
    assert options_model.data == post_data
    assert options_model.params == params


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'params_json, match',
    [
        ('{ "bad": }', 'Bad JSON'),
        (['a', 'b'], 'Unexpected type'),
    ],
)
def test_vega_options_bad_params_fail(params_json, match):
    options_data = {
        'spec': 'spec',
        'data': 'data',
        'params': params_json,
    }

    with pytest.raises(ValidationError, match=match):
        VegaOptions(**options_data)


# ------------------------------------------------------------------------------
def test_vega_chart_svg(td, tmp_path):
    """Generate a Vega chart in SVG format."""

    gen = content_generator_for_type('vega')

    options = {
        'spec': 'charts/woof.yaml',
        'data': f'file;dogs.csv',
    }
    chart = gen(options, DocmaRenderContext(PackageReader.new(td)))
    # To update the baseline image .. uncomment this and run the test once.
    # - (td / 'images' / 'woof.svg').write_bytes(chart['string'])

    assert chart['mime_type'] == 'image/svg+xml'
    assert chart['string'] == (td / 'images' / 'woof.svg').read_bytes()


# ------------------------------------------------------------------------------
def test_vega_chart_png(td, tmp_path):
    """Generate a Vega chart in PNG format."""

    gen = content_generator_for_type('vega')

    options = {
        'spec': 'charts/woof.yaml',
        'data': f'file;dogs.csv',
        'format': 'png',
    }
    chart = gen(options, DocmaRenderContext(PackageReader.new(td)))
    # To update the baseline image .. uncomment this and run the test once.
    # - (td / 'images' / 'woof.png').write_bytes(chart['string'])

    assert chart['mime_type'] == 'image/png'
    assert images_are_identical(chart['string'], td / 'images' / 'woof.png')
