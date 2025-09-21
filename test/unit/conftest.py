"""Pytest conf."""

from __future__ import annotations

import os
from pathlib import Path

import dotenv
import pytest  # noqa
import yaml
from jinja2 import Environment

from docma.jinja.resolvers import *
from docma.lib.plugin import (
    MappingResolver,
    PLUGIN_JINJA_FILTER,
    PLUGIN_JINJA_TEST,
    PackageResolver,
    PluginRouter,
)
from utils import DotDict

CONFIG = 'conftest.yaml'

dotenv.load_dotenv()


# ------------------------------------------------------------------------------
@pytest.fixture(scope='session')
def td() -> Path:
    """Path for test data."""
    return Path(__file__).parent.parent / 'data'


# ------------------------------------------------------------------------------
@pytest.fixture(scope='session')
def dirs(td) -> DotDict:
    """Package to access useful directories in the source tree."""

    docma_base = Path(__file__).parent.parent.parent
    test_base = Path(__file__).parent.parent

    return DotDict(
        {
            'cwd': Path('.').resolve(),
            'src': docma_base,
            'test': test_base,
            'services': test_base / 'services',
            'data': td,
            'templates': test_base / 'templates',
        }
    )


# ------------------------------------------------------------------------------
@pytest.fixture(scope='session')
def env():
    """Make environment + dotenv variables available."""
    return DotDict(os.environ)


# ------------------------------------------------------------------------------
@pytest.fixture(scope='session')
def tc() -> DotDict:
    """
    Deliver test configuration data.

    This can be accessed as `tc.a.b.c` or using dictionary notation.

    """

    with open(Path(__file__).parent / CONFIG) as fp:
        return DotDict(yaml.safe_load(fp))


# ------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def aws_mock_creds(monkeypatch):
    """Mocked AWS Credentials for moto."""

    with suppress(KeyError):
        monkeypatch.delenv('AWS_PROFILE')

    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'testing')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'testing')
    monkeypatch.setenv('AWS_SECURITY_TOKEN', 'testing')
    monkeypatch.setenv('AWS_SESSION_TOKEN', 'testing')
    monkeypatch.setenv('AWS_DEFAULT_REGION', 'us-east-1')


# ------------------------------------------------------------------------------
@pytest.fixture(scope='session')
def s3() -> DotDict:
    """ "Package up useful S3 locations."""

    return DotDict(
        {
            # 'whatever': S3path('...'),
        }
    )


# ------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def jfilters() -> PluginRouter:
    """Load jinja filters."""
    e = Environment(autoescape=True)
    return PluginRouter(
        [
            MappingResolver(e.filters),
            CurrencyFilterResolver(),
            PackageResolver('docma.plugins.jinja_filters', PLUGIN_JINJA_FILTER),
        ],
    )


# ------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def jtests() -> PluginRouter:
    """Load jinja tests."""
    e = Environment(autoescape=True)
    return PluginRouter(
        [
            MappingResolver(e.tests),
            PackageResolver('docma.plugins.jinja_tests', PLUGIN_JINJA_FILTER),
            # Format checkers work as both JSONschema formats and Jinja teats.
            DateFormatResolver(),
            PackageResolver('docma.plugins.format_checkers', PLUGIN_JINJA_TEST),
        ]
    )
