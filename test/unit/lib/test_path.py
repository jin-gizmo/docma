"""Tests for docma.lib.path."""

from __future__ import annotations

import pytest

from docma.lib.path import *


# ------------------------------------------------------------------------------
def test_walkpath(dirs):
    assert __file__ in (str(f) for f in walkpath(dirs.test))


# ------------------------------------------------------------------------------
def test_relative_path_ok(dirs):
    assert relative_path(dirs.test, 'whatever') == Path('whatever')
    assert relative_path(dirs.test, 'a/b/../../whatever') == Path('whatever')


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename',
    [
        '/an/absolute/path',
        'a/b/../../../whatever',  # Outside the tree
        '..',
    ],
)
def test_relative_path_fail(filename: str, dirs):
    with pytest.raises(ValueError):
        relative_path(dirs.test, filename)
