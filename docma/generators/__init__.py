# ruff: noqa: E501
"""
Docma content generators produce dynamic content (e.g. charts) as part of template rendering.

They are activated in a HTML file in a docma template by invoking a URL in the
form:

```uri
docma:<content-type>?option1=value1&option2=value2
```

!!! info
    Do not use `docma://` as that implies a netloc which is not used here.

Content generators have the following signature:

!!! info "Content Generator Signature"

    ```python
    @content_generator(content_type: str, validator=type[BaseModel])))
    def content_generator(options: type[BaseModel], context: DocmaRenderContext) -> dict[str, Any]:
    ```

The `content_generator` registration decorator has the following parameters:

|Name|Type|Description|
|-|-|-|
|`content_type`|`str`| The content type. This is the first component of the URL after the `docma` scheme.|
|`validator`|`type[BaseModel]`|A class derived from a Pydantic `BaseModel` that will validate and hold the query parameters from the URL.|

The content generator itself has the following parameters:

|Name|Type|Description|
|-|-|-|
|`options`|`type[BaseModel]`|An instance of the Pydantic validator class for the generator.|
|`context`|`DocmaRenderContext`|The template package. This allows the content generator to access files in the template, if required.|

Content generators return the value required of a Weasyprint URL fetcher. i.e.
a dictionary containing (at least):

- `string`:   The bytes of the content (yes ... it says string but it's bytes).

- `mimetype`: The MIME type of the content.

Content generators should raise a
<a href="#docma.exceptions.DocmaGeneratorError">`DocmaGeneratorError`</a>
on failure.

Look at the `swatch` content generator as an example.
"""

import pkgutil
from importlib import import_module

from .__common__ import (
    content_generator as content_generator,
    content_generator_for_type as content_generator_for_type,
)

# Auto import our generator functions
for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name.startswith('_'):
        continue
    import_module(f'.{module_name}', package=__name__)

__all__ = ['content_generator', 'content_generator_for_type']
