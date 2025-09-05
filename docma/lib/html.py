"""HTML utilities."""

from __future__ import annotations

from copy import deepcopy

from bs4 import BeautifulSoup


# ------------------------------------------------------------------------------
def html_append(html1: BeautifulSoup, html2: BeautifulSoup) -> None:
    """Append head and body of a HTML document into another HTML document."""

    if not html1.html:
        html1.append(html1.new_tag('html'))

    # Merge head
    head1 = html1.head
    head2 = html2.head
    if head2:
        # Obnly create head1 if needed to hold head2 content
        if not head1:
            head1 = html1.new_tag('head')
            html1.html.insert(0, head1)
        for item in head2.contents:
            head1.append(deepcopy(item))

    body1 = html1.body
    body2 = html2.body
    if not body1:
        # Always ensure a body in the final document.
        body1 = html1.new_tag('body')
        html1.html.append(body1)

    if body2:
        for item in body2.contents:
            body1.append(deepcopy(item))
    elif html2.html:
        # Maybe some orphan content outside a body structure. Stick it at the end of the html
        # Sloppy but possible
        for item in html2.html.children:
            if item.name != 'head':
                html1.append(deepcopy(item))
