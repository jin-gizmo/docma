"""Test content validators."""

import pytest  # noqa

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


# ------------------------------------------------------------------------------
def test_load_config_validation_schema_fail(dirs, monkeypatch):
    """Test when we cannot read the validation schema for config.yaml."""

    def bad_read_text(*_, **__):
        """Patch for pathlib.Path.read_text to force an exception."""
        raise OSError('Kaboom')

    monkeypatch.setattr('pathlib.Path.read_text', bad_read_text)
    with pytest.raises(DocmaInternalError, match='Kaboom'):
        validate(dirs.templates / 'test1.src' / 'config.yaml')
