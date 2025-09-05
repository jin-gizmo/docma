"""Test swatch generator."""

from __future__ import annotations

import pytest

from docma.generators import content_generator_for_type
from docma.lib.core import DocmaRenderContext
from docma.lib.packager import PackageReader

from utils import images_are_identical


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'options, result_file',
    [
        (
            {
                'width': 100,
                'height': 50,
                'color': '#00ffff',
            },
            'swatch-cyan-100x50.png',
        ),
        (
            {
                'width': 100,
                'height': 50,
                'color': '#0000ff',
                'text': 'Hello world!',
                'text_color': 'yellow',
                'font': 'Arial',
                'font_size': 16,
            },
            'swatch-blue-100x50-hello-world.png',
        ),
    ],
)
def test_swatch(options: dict, result_file: str, td) -> None:

    gen = content_generator_for_type('swatch')

    swatch = gen(options, DocmaRenderContext(PackageReader.new(td)))

    assert swatch['mime_type'] == 'image/png'
    assert images_are_identical(swatch['string'], td / 'images' / result_file)
