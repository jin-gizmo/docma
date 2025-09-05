"""Tests for Markdown to HTML compiler."""

from __future__ import annotations

from utils import squish_html

from docma.compilers import compiler_for_file


# ------------------------------------------------------------------------------
def test_compile_markdown(dirs) -> None:

    md_path = dirs.templates / 'test1.src/content/compile-me.md'
    html_path = dirs.templates / 'test1.src/content/compile-me.html'
    compiler = compiler_for_file(md_path)

    assert squish_html(html_path.read_text()) == squish_html(compiler(md_path.read_bytes()))
