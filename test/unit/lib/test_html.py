"""Tests for docma.lib.html."""

from __future__ import annotations
from bs4 import BeautifulSoup

import pytest

from docma.lib.html import *


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'h1, h2, expected',
    [
        (
            '<html><head><title>title1</title></head><body><h1>One</h1></body></html>',
            '<html><head><title>title2</title></head><body><h1>Two</h1></body></html>',
            (
                '<html><head><title>title1</title><title>title2</title></head>'
                '<body><h1>One</h1><h1>Two</h1></body></html>'
            ),
        ),
        # No head in part 1
        (
                '<html><body><h1>One</h1></body></html>',
                '<html><head><title>title2</title></head><body><h1>Two</h1></body></html>',
                (
                        '<html><head><title>title2</title></head>'
                        '<body><h1>One</h1><h1>Two</h1></body></html>'
                ),
        ),
        # No head in either part
        (
                '<html><body><h1>One</h1></body></html>',
                '<html><body><h1>Two</h1></body></html>',
                '<html><body><h1>One</h1><h1>Two</h1></body></html>',
        ),
        # Empty html1
        (
            '',
            '<html><head><title>title2</title></head><body><h1>Two</h1></body></html>',
            '<html><head><title>title2</title></head><body><h1>Two</h1></body></html>',
        ),
        # html2 has only out of body content. Sloppy but possible.
        (
                '<html><body><h1>One</h1></body></html>',
                '<html><h1>Two</h1></html>',
                '<html><body><h1>One</h1></body></html><h1>Two</h1>',
        ),
    ],
)
def test_html_append(h1: str, h2: str, expected: str):
    html1 = BeautifulSoup(h1, 'html.parser')
    html_append(html1, BeautifulSoup(h2, 'html.parser'))
    print(html1)
    assert html1 == BeautifulSoup(expected, 'html.parser')
