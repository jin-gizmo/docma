"""Test QR code generator."""

from __future__ import annotations

from docma.generators import content_generator_for_type
from docma.jinja import DocmaRenderContext
from docma.lib.packager import PackageReader
from utils import images_are_identical


# ------------------------------------------------------------------------------
def test_qrcode(td, tmp_path) -> None:

    gen = content_generator_for_type('qrcode')

    options = {
        'text': 'hello-world',
        'fg': '#ff00ff',
    }
    qr = gen(options, DocmaRenderContext(PackageReader.new(td)))

    assert qr['mime_type'] == 'image/png'
    assert images_are_identical(qr['string'], td / 'images' / 'qr-magenta-hello-world.png')
