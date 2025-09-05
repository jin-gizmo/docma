"""Tests for docma.url_fetchers.__common__."""

import pytest

from docma.url_fetchers import get_url_fetcher_for_scheme


# ------------------------------------------------------------------------------
def test_import_content_fail():
    with pytest.raises(KeyError):
        get_url_fetcher_for_scheme('bad-scheme')
