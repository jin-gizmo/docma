"""Test document metadate (mostly edge cases)."""

import pytest  # noqa

from docma.lib.metadata import DocumentMetadata


# ------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def metadata() -> DocumentMetadata:
    """Construct a simple metadata instance."""
    return DocumentMetadata(
            keywords=['a', 'b', 'c'],
            subject='Test'
        )

# ------------------------------------------------------------------------------
class TestDocumentMetadata:
    """Test the DocumentMetadata class."""

    # --------------------------------------------------------------------------
    @pytest.mark.parametrize(
        'name, expected',
        [
            ('keywords', '/Keywords'),
            ('creation_date', '/CreationDate'),
        ],
    )
    def test_to_pdf_name(self, name: str, expected: str):
        assert DocumentMetadata.to_pdf_name(name) == expected

    # --------------------------------------------------------------------------
    @pytest.mark.parametrize(
        'name, expected',
        [
            ('keywords', 'keywords'),
            ('CreationDate', 'creation_date'),
            ('/CreationDate', 'creation_date'),
        ],
    )
    def test_normalise_attr_name(self, name: str, expected: str):
        assert DocumentMetadata.normalise_attr_name(name) == expected

    # --------------------------------------------------------------------------
    def test__setitem__(self, metadata):
        metadata['/SomeThing'] = 'Test'
        assert len(metadata) == 3
        assert metadata['some_thing'] == 'Test'

    # --------------------------------------------------------------------------
    def test__getitem__(self, metadata):
        assert metadata['subject'] == 'Test'
        with pytest.raises(KeyError):
            _ = metadata['---']

    # --------------------------------------------------------------------------
    def test_get(self, metadata):
        assert metadata.get('subject') == 'Test'
        assert metadata.get('---', 'default') == 'default'

    # --------------------------------------------------------------------------
    def test__len__(self, metadata):
        assert len(metadata) == 2

    # --------------------------------------------------------------------------
    def test__iter__(self, metadata):
        assert set(metadata) == {'keywords', 'subject'}

    # --------------------------------------------------------------------------
    def test__delitem__(self, metadata):
        del metadata['keywords']
        assert len(metadata) == 1
        assert 'keywords' not in metadata

    # --------------------------------------------------------------------------
    @pytest.mark.parametrize(
        'format_, expected',
        [
            ('html', {'keywords': 'a, b, c', 'subject': 'Test'}),
            ('pdf', {'/Keywords': 'a; b; c', '/Subject': 'Test'}),
        ],
    )
    def test_as_dict_ok(self, format_, expected, metadata):
        assert metadata.as_dict(format_) == expected

    # --------------------------------------------------------------------------
    def test_as_dict_fail(self, metadata):
        with pytest.raises(ValueError, match='Unknown format'):
            metadata.as_dict('badformat')
