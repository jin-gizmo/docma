"""Compile Markdown documents into HTML."""

from __future__ import annotations

import markdown

from .__common__ import content_compiler


# ------------------------------------------------------------------------------
@content_compiler('md')
def compile_markdown(src_data: bytes) -> str:
    """Compile Markdown source documents into HTML."""
    return markdown.markdown(src_data.decode('utf-8'), extensions=['extra', 'admonition'])
