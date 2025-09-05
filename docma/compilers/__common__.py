"""Common components for content compilers."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

_CONTENT_COMPILERS = {}


# ------------------------------------------------------------------------------
def content_compiler(*suffixes: str) -> Callable:
    """
    Register a document compiler for the specfied filename suffixes.

    This is a decorator used like so:

    .. code-block:: python

        @content_compiler('md')
        def compile_markdown(src_data: bytes) -> str:
            ...

    :param suffixes:    File suffixes (without the dot) handled by the decorated
                        function.
    """

    def decorate(func):
        """Register the handler function."""
        for s in suffixes:
            _CONTENT_COMPILERS[s] = func
        return func

    return decorate


# ------------------------------------------------------------------------------
def compiler_for_suffix(suffix: str) -> Callable:
    """Get the handler for the specfied format."""

    return _CONTENT_COMPILERS[suffix.lower()]


# ------------------------------------------------------------------------------
def compiler_for_file(file: Path) -> Callable:
    """Get the handler for the specfied file based on suffix."""
    return compiler_for_suffix(file.suffix[1:])
