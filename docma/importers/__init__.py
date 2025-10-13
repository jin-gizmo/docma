# ruff: noqa: E501
"""
Content importers bring in external content when compiling a [docma template][document-templates].

See [Document Imports][document-imports].

They accept a single URL style argument and return bytes with the content. The
scheme from the URL is used to select the appropriate import handler.

Importers have the following signature:

!!! note "Importer Signature"

    ```python
    @content_importer(*schemes: str)
    def whatever(url: str, max_size: int = 0) -> bytes:
    ```

|Name|Type|Description|
|-|-|-|
|`url`|`str`|The URL to import. The scheme has already been used to select the correct importer.|
|`max_size`|`int`|The maximum size of the imported content. If non-zero, the importer should do its best to determine the imported data size and throw a [DocmaImportError](#docma.exceptions.DocmaImportError) if the data exceeds this size.|

Importers should raise a
<a href="#docma.exceptions.DocmaImportError">`DocmaImportError`</a>
on failure.

"""

import pkgutil
from importlib import import_module

from .__common__ import (
    content_importer as content_importer,
    import_content as import_content,
)

# Auto import our generator functions
for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name.startswith('_'):
        continue
    import_module(f'.{module_name}', package=__name__)


__all__ = ['content_importer', 'import_content']
