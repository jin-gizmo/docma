"""Test main docma module interface."""

import pytest  # noqa
import docma


# ------------------------------------------------------------------------------
def test_docma_dir():
    assert set(dir(docma)) == set(docma.__all__)
