"""Test utility functions."""

from __future__ import annotations

from itertools import product
from pathlib import Path
from io import BytesIO

from PIL import Image


# ------------------------------------------------------------------------------
def squish_html(html: str) -> str:
    """Remove unnecessary whitespace from HTML."""

    return ''.join(s.strip() for s in html.splitlines())


# ------------------------------------------------------------------------------
def images_are_identical(img1_src: str | Path | bytes, img2_src: str | Path | bytes) -> bool:
    """Check if two images are identical."""

    img1 = Image.open(BytesIO(img1_src) if isinstance(img1_src, bytes) else img1_src)
    img2 = Image.open(BytesIO(img2_src) if isinstance(img2_src, bytes) else img2_src)

    if img1.size != img2.size:
        return False

    if img1.mode != img2.mode:
        img2 = img2.convert(img1.mode)

    # Compare pixel by pixel
    width, height = img1.size
    for x, y in product(range(width), range(height)):
        if img1.getpixel((x, y)) != img2.getpixel((x, y)):
            return False

    return True
