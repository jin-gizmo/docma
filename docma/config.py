"""Docma static config."""

from __future__ import annotations

LOGNAME = 'docma'

# PDF bounding box rectangles within this amount of size variation are considered
# to be identical. Each unit is 1/72 of an inch. So, for example an A4 portrait
# page is about 595 (w) x 842 (h). But PDFs tools wobble a bit around this value
# so we need a fuzzy size match.
RECTANGLE_FUZZ_PDF_UNITS = 10.0

IMPORT_MAX_SIZE = 10_000_000  # bytes -- not sure this is needed at all tbh.
IMPORT_CACHE_SIZE = 10  # LRU cache
IMPORT_URL_TIMEOUT = 20  # seconds

# These values control image inlining in HTML rendering mode.
# The reason you might not want to inline small images is because a 1x1 png
# image is < 100 bytes and is sometimes used for tracking purposes.
EMBED_IMG_MAX_SIZE = 1_000_000  # bytes
EMBED_IMG_MIN_SIZE = 100  # bytes

VEGA_PPI = 72

# Set these default weasyprint options. Template can override.
WEASYPRINT_OPTIONS = {
    'optimize_images': True,  # Essential to avoid Weasyprint bug where it bypasses url fetcher
    'media': 'print',
}
