"""Tests for docma.generators.__common__."""

import pytest

from docma.generators import content_generator_for_type
from docma.exceptions import DocmaGeneratorError


# ------------------------------------------------------------------------------
def test_content_generator_for_type_fail():
    with pytest.raises(DocmaGeneratorError, match='Unknown content type'):
        content_generator_for_type('no-such-content-type')
