"""Docma exceptions."""

from __future__ import annotations


class DocmaError(Exception):
    """Base class for docma errors."""

    pass


class DocmaInternalError(DocmaError):
    """Internal error."""

    pass


class DocmaPackageError(DocmaError):
    """Packaging and content related errors."""

    pass


class DocmaCompileError(DocmaError):
    """Content compiler error."""

    pass


class DocmaDataProviderError(DocmaError):
    """Data provider error."""

    pass


class DocmaGeneratorError(DocmaError):
    """Content generator error."""

    pass


class DocmaImportError(DocmaError):
    """Content importer error."""

    pass


class DocmaUrlFetchError(DocmaError):
    """URL fetcher error."""

    pass
