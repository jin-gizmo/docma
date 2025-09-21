"""
Test docma.lib.query.

Mostly this is edge cases as the main paths are covered elsewhere.
"""

import pytest
import yaml

from docma.lib.packager import PackageReader
from docma.lib.query import *
from utils import squish_space


# ------------------------------------------------------------------------------
class TestDocmaQuerySpecification:
    """Tests for DocmaQuerySpecification."""

    # --------------------------------------------------------------------------
    def test_bad_row_schema_fail(self, dirs):
        dqs_src = yaml.safe_load(
            (dirs.templates / 'test1.src' / 'bad-queries' / 'custard-bad-schema.yaml').read_text()
        )

        with pytest.raises(ValueError, match='not valid under any of the given schemas'):
            DocmaQuerySpecification(name='custard-bad-schema', **dqs_src)

    # --------------------------------------------------------------------------
    @pytest.mark.parametrize(
        'paramstyle,reference_query, reference_params',
        [
            (
                'named',
                (
                    'SELECT count(*) FROM "docma".custard WHERE favouritecustard=:favouritecustard'
                    '  AND custardbidprice > :custardbidprice'
                    '  AND custardjedi=:custardjedi'
                ),
                {
                    'favouritecustard': 'lumpy',
                    'custardbidprice': 9.99,
                    'custardjedi': False,
                },
            ),
            (
                'pyformat',
                (
                    'SELECT count(*) FROM "docma".custard WHERE favouritecustard=%(favouritecustard)'
                    '  AND custardbidprice > %(custardbidprice)'
                    '  AND custardjedi=%(custardjedi)'
                ),
                {
                    'favouritecustard': 'lumpy',
                    'custardbidprice': 9.99,
                    'custardjedi': False,
                },
            ),
        ],
    )
    def test_named_paramstyles_ok(self, paramstyle, reference_query, reference_params, dirs):
        """Test named and pyformat paramstyles."""
        dqs_src = yaml.safe_load(
            (dirs.templates / 'test1.src' / 'queries' / f'custard-{paramstyle}.yaml').read_text()
        )
        dqs = DocmaQuerySpecification(name=f'custard-{paramstyle}', **dqs_src)
        context = DocmaRenderContext(
            tpkg=PackageReader.new(dirs.templates / 'test1.src'),
            params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
        )
        query_txt, query_params = dqs.prepare_query(
            context, params={'db': reference_params}, paramstyle=paramstyle
        )
        assert squish_space(query_txt) == squish_space(reference_query)
        # We can't just compare the params directly because they may have been
        # type cast.
        assert set(query_params) == set(reference_params)

    # --------------------------------------------------------------------------
    def test_bad_paramstyle_fail(self, dirs):
        dqs_src = yaml.safe_load(
            (dirs.templates / 'test1.src' / 'queries' / 'custard-qmark.yaml').read_text()
        )
        dqs = DocmaQuerySpecification(name='custard-qmark', **dqs_src)
        context = DocmaRenderContext(
            tpkg=PackageReader.new(dirs.templates / 'test1.src'),
            params=yaml.safe_load((dirs.templates / 'test1-params.yaml').read_text()),
        )

        with pytest.raises(ValueError, match='Unknown paramstyle'):
            dqs.prepare_query(context, params={'k': 'v'}, paramstyle='bad-paramstyle')
