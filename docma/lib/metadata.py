"""Document metadata management for docma."""

from __future__ import annotations

__author__ = 'Murray Andrews'

from collections.abc import MutableMapping
from typing import Any

from pydantic.alias_generators import to_camel, to_snake

from docma.lib.misc import flatten_iterable


# ------------------------------------------------------------------------------
class DocumentMetadata(MutableMapping):
    """
    Document metadata manager and format converter.

    This provides an output format agnostic container for document metadata
    (title, subject, author etc.). It can provide a metadata structure in the
    format required for either PDF or HTML.
    """

    @staticmethod
    def to_pdf_name(name: str) -> str:
        """Convert a metadata attribute name to PDF metadata style."""

        s = to_camel(name)
        if s[0].islower():
            s = s[0].upper() + s[1:]
        return f'/{s}'

    @staticmethod
    def normalise_attr_name(attr_name: str) -> str:
        """Normalise attribute name to handle PDF and plain variants."""
        return to_snake(attr_name.removeprefix('/'))

    @classmethod
    def normalise_attr_value(cls, attr_value: Any) -> list | str:
        """Normalise attribute value to preserve lists but everything else is string."""
        if isinstance(attr_value, str):
            return attr_value
        if isinstance(attr_value, list):
            return [cls.normalise_attr_value(v) for v in flatten_iterable(attr_value)]
        return str(attr_value)

    def __init__(self, **kwargs: Any) -> None:
        """Initialize metadata."""
        self._attrs = {
            self.normalise_attr_name(k): self.normalise_attr_value(v) for k, v in kwargs.items()
        }

    def __setitem__(self, key, value):
        """
        Set an attribute using dict semantics.

        List values are converted to semicolon
        """
        self._attrs[self.normalise_attr_name(key)] = self.normalise_attr_value(value)

    def __getitem__(self, key):
        """Implement core dict methods."""
        return self._attrs[key]

    def __len__(self):
        """Implement core dict methods."""
        return len(self._attrs)

    def __iter__(self):
        """Implement core dict methods."""
        return iter(self._attrs)

    def __delitem__(self, key):
        """Implement core dict methods."""
        del self._attrs[key]

    def __repr__(self):
        """Implement core dict methods."""
        return repr(self._attrs)

    def __str__(self):
        """Implement core dict methods."""
        return str(self._attrs)

    def as_dict(self, format:str =None) -> dict[str, Any]:  # noqa A002
        """
        Return a dictionary with all attributes.

        :param format:  Adjust metadata for the specified format. Allowed values
                        are None, `html` and `pdf`, PDF has names like `/Author`
                        whereas HTML convention is `author`. PDF convention on
                        list items (e.g. /Keywords) is to join them with semi-colons.
                        HTML convention is commas.
        """

        if not format:
            return self._attrs
        if format == 'html':
            return {k: ', '.join(v) if isinstance(v, list) else v for k, v in self._attrs.items()}
        if format == 'pdf':
            return {
                self.to_pdf_name(k): '; '.join(v) if isinstance(v, list) else v
                for k, v in self._attrs.items()
            }
        raise ValueError(f'Unknown format: {format}')
