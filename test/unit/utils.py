"""Test utility functions."""

from __future__ import annotations

from io import BytesIO
from itertools import product
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

# noinspection PyPackageRequirements
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
        return False  # pragma: no cover

    if img1.mode != img2.mode:
        img2 = img2.convert(img1.mode)  # pragma: no cover

    # Compare pixel by pixel
    width, height = img1.size
    for x, y in product(range(width), range(height)):
        if img1.getpixel((x, y)) != img2.getpixel((x, y)):
            return False  # pragma: no cover

    return True


# ------------------------------------------------------------------------------
def squish_space(s: str) -> str:
    """Collapse whitespace."""

    return ' '.join(s.strip().split())


# ------------------------------------------------------------------------------
class DotDict:
    """
    Access dict values with dot notation or conventional dict notation or mix and match.

    ..warning:: This does not handle all dict syntax, just what is needed here.

    """

    def __init__(self, *data: Mapping[str, Any]):
        """Create dotable dict from dict(s)."""
        self._data: dict[str, Any] = {}

        for d in data:
            self._data.update(d)

    def __getattr__(self, item: str) -> Any:
        """Access config elements with dot notation support for keys."""

        if not item or not isinstance(item, str):
            raise ValueError(f'Bad config item name: {item}')

        try:
            value = self._data[item]
        except KeyError:
            raise AttributeError(item)
        return self.__class__(value) if isinstance(value, dict) else value

    def __getitem__(self, item):
        value = self._data[item]
        return self.__class__(value) if isinstance(value, dict) else value

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return repr(self._data)

    @property
    def dict(self) -> dict[str, Any]:
        """Return the underlying data as a dict."""
        return self._data


# ------------------------------------------------------------------------------
class S3path:
    """Convenience hack for handling S3 paths."""

    def __init__(self, uri: str):
        purl = urlparse(uri)
        if purl.scheme != 's3':
            raise ValueError(f'Unsupported S3 scheme: {purl.scheme}')
        self.bucket, self.key = purl.netloc, purl.path[1:]
        self.uri = uri

    def __call__(self):
        return self.uri

    def __truediv__(self, other):
        return self.__class__(f'{self.uri}/{other}')

    def __str__(self):
        return self.uri

    def __repr__(self):
        return self.uri
