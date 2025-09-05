"""Tests for docma.lib.core."""

from __future__ import annotations

import pytest

from docma.lib.core import *
from docma.lib.packager import PackageReader


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'v, extra_params, expected',
    [
        ('{{ x.y[0].a }}', {}, 'A1'),
        ('{{ x.y[0].a }}', {'x': {'y': [{'a': 'Not A1'}]}}, 'Not A1'),
    ],
)
def test_docma_render_context_scalar_ok(v, expected, extra_params, td):
    params = {
        'x': {
            'y': [
                {'a': 'A1', 'b': 'B1'},
                {'a': 'A2', 'b': 'B2'},
            ]
        }
    }

    context = DocmaRenderContext(PackageReader.new(td), params)
    assert context.render(v, **extra_params) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'v, expected',
    [
        (['{{ x.y[0].a }}', '{{ x.y[1].b }}', 'c'], ['A1', 'B2', 'c']),
    ],
)
def test_docma_render_context_iter_ok(v, expected, td):
    params = {
        'x': {
            'y': [
                {'a': 'A1', 'b': 'B1'},
                {'a': 'A2', 'b': 'B2'},
            ]
        }
    }

    context = DocmaRenderContext(PackageReader.new(td), params)
    assert context.render(v) == expected


# ------------------------------------------------------------------------------
def test_docma_render_context_bad_type_to_render_fail(td):
    context = DocmaRenderContext(PackageReader.new(td))
    with pytest.raises(TypeError, match="Cannot render type"):
        # Can't render an int
        context.render(34)


# ------------------------------------------------------------------------------
def test_metadata_ok():
    m = Metadata(
        **{
            'author': 'A',
            '/Title': 'T',
            '/CreationDate': 'CD',
        }
    )
    m['/Keywords'] = ['A', ['B', ['C', 'D']], 'E']

    assert m['author'] == 'A'
    assert m['title'] == 'T'
    assert m['creation_date'] == 'CD'
    assert m['keywords'] == ['A', 'B', 'C', 'D', 'E']

    assert 'title' in m
    del m['title']
    assert 'title' not in m
    assert len(m) == 3
    assert str(m) == "{'author': 'A', 'creation_date': 'CD', 'keywords': ['A', 'B', 'C', 'D', 'E']}"
    assert (
        repr(m) == "{'author': 'A', 'creation_date': 'CD', 'keywords': ['A', 'B', 'C', 'D', 'E']}"
    )
    assert m.as_dict() == {
        'author': 'A',
        'creation_date': 'CD',
        'keywords': ['A', 'B', 'C', 'D', 'E'],
    }
    assert m.as_dict('html') == {
        'author': 'A',
        'creation_date': 'CD',
        'keywords': 'A, B, C, D, E',
    }
    assert m.as_dict('pdf') == {
        '/Author': 'A',
        '/CreationDate': 'CD',
        '/Keywords': 'A; B; C; D; E',
    }
    with pytest.raises(ValueError, match='Unknown format'):
        m.as_dict('bad-format')

    assert len(m.keys()) == 3
    assert m.get('author') == 'A'

    n = 0
    for n, _ in enumerate(m):
        pass
    assert n == 2

    m['int'] = 10
    assert m['int'] == '10'

    m.clear()
    assert len(m) == 0

