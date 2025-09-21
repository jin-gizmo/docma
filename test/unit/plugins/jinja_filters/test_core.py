"""Test core Jinja management components."""

import pytest

from docma.jinja import *


# ------------------------------------------------------------------------------
def test_noloader():
    with pytest.raises(Exception, match='loading prohibited'):
        NoLoader().get_source(DocmaJinjaEnvironment(), 'whatever')


# ------------------------------------------------------------------------------
def test_abort():
    with pytest.raises(Exception, match='aborted'):
        DOCMA_JINJA_EXTRAS['abort']('aborted')


# ------------------------------------------------------------------------------
def test_jfunc():
    @jfunc('funky')
    def _():
        """Placeholder."""
        return 42

    assert DOCMA_JINJA_EXTRAS['funky']() == 42
