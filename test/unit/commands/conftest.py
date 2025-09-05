"""Common test componets for commands."""

import runpy

import pytest
from docma.cli import docma


@pytest.fixture(scope='session')
def docma_cli_name() -> str:
    """Return name of docma_cli."""
    return 'bin/docma'


@pytest.fixture(scope='session')
def docma_cli_module(docma_cli_name: str):
    """Return the Python module for the main docma CLI."""
    return docma.main
    # return runpy.run_path(docma_cli_name)
