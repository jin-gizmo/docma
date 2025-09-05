"""Test content validators."""

import pytest

from docma.validators import *


# ------------------------------------------------------------------------------
def test_chart_validator_fail_no_schema():

    content = b"""
problem: "no $schema"
"""

    with pytest.raises(DocmaPackageError, match=r'No \$schema defined'):
        validate_content(Path('charts/whatever.yaml'), content)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename',
    [
        'config.yaml',
        'charts/woof.yaml',
        'content/hello-world.html',
        'data/dogs.csv',
        'queries/custard.yaml',
    ],
)
def test_validate_content_ok(filename, dirs):
    validate(dirs.templates / 'test1.src' / filename)
