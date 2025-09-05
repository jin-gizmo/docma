"""Pytest conf."""

from __future__ import annotations

import os
from collections.abc import Mapping
from contextlib import suppress
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import dotenv
import pytest
import yaml

CONFIG = 'conftest.yaml'

dotenv.load_dotenv()


# ------------------------------------------------------------------------------
class DotDict:
    """
    Access dict values with dot notation or conventional dict notation or mix and match.

    ..warning:: This does not handle all dict syntax, just what is needed here.

    """

    def __init__(self, *data: Mapping[str, Any]):
        """Create dotable dict from dict(s)."""
        self._data = {}

        for d in data:
            self._data.update(d)

    def __getattr__(self, item: str) -> Any:
        """Access config elements with dot notation support for keys."""

        if not item or not isinstance(item, str):
            raise ValueError(f'Bad config item name: {item}')

        try:
            value = self._data[item]
        except KeyError:
            raise AttributeError(item)
        return self.__class__(value) if isinstance(value, dict) else value

    def __getitem__(self, item):
        value = self._data[item]
        return self.__class__(value) if isinstance(value, dict) else value

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return repr(self._data)

    @property
    def dict(self) -> dict:
        """Return the underlying data as a dict."""
        return self._data


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
class S3path:
    """Convenience hack for handling S3 paths."""

    def __init__(self, uri: str):
        purl = urlparse(uri)
        if purl.scheme != 's3':
            raise ValueError(f'Unsupported S3 scheme: {purl.scheme}')
        self.bucket, self.key = purl.netloc, purl.path[1:]
        self.uri = uri

    def __call__(self):
        return self.uri

    def __truediv__(self, other):
        return self.__class__(f'{self.uri}/{other}')

    def __str__(self):
        return self.uri

    def __repr__(self):
        return self.uri


# ------------------------------------------------------------------------------
@pytest.fixture(scope='session')
def s3() -> DotDict:
    """ "Package up useful S3 locations."""

    return DotDict(
        {
            # 'whatever': S3path('...'),
        }
    )
