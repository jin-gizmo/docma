"""Common components for content generators."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from pydantic import BaseModel

from docma.exceptions import DocmaGeneratorError
from docma.jinja import DocmaRenderContext

_CONTENT_GENERATORS = {}


# ------------------------------------------------------------------------------
def content_generator_for_type(content_type: str) -> Callable:
    """Get the generator function for the specified content type."""

    try:
        return _CONTENT_GENERATORS[content_type]
    except KeyError:
        raise DocmaGeneratorError(f'{content_type}: Unknown content type')


# ------------------------------------------------------------------------------
def content_generator(content_type: str, validator: type[BaseModel]) -> Callable:
    """
    Register the generator function for the specified content type.

    This is a decorator used like so:

    ```python
    class WhateverOptions(BaseModel):
        param_a: str
        param_b: int

    @content_generator('whatever', WhateverOptions)
    def _(pkg: PackageReader, options: WhateverOptions, params: dict[str]) -> dict[str, Any]:
        ...
    ```

    :param content_type: The content type. This is the first component of the
                        URL after the `docma` scheme.
    :param validator:   A class derived from a Pydantic `BaseModel` that will
                        hold the query parameters from the URL.
    """

    def decorate(func: Callable) -> Callable:
        """Register the generator function for the specified content type."""

        @wraps(func)
        def wrapper(options: dict[str, Any], context: DocmaRenderContext) -> dict[str, Any]:
            """Add option validation to the generator function."""
            options = validator(**options)
            return func(options=options, context=context)

        _CONTENT_GENERATORS[content_type] = wrapper
        return wrapper

    return decorate
