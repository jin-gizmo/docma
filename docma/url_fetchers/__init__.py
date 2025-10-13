# ruff: noqa: E501
"""
URL fetchers are used during the compile phase to inject template content referenced by URLs.

See [Dynamic Content Generation][dynamic-content-generation] for more information.

If a fetcher for a given schema does not have a custom fetcher, the default URL
fetcher is used.

URL fetchers have the following signature:

!!! info "URL Fetcher Signature"

    ```python
    from docma.url_fetchers import url_fetcher

    @url_fetcher(*schemes)
    def url_fetcher(purl: ParseResult, context: DocmaRenderContext) -> dict[str, Any]:
        ...
    ```

|Name|Type|Description|
|-|-|-|
|`purl`|[`urllib.parse.ParseResult`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.ParseResult)|The parsed URL.|
|`context`|`DocmaRenderContext`|The template package. This allows the content generator to access files in the template, if required.|

URL fetchers return the value required of a Weasyprint URL fetcher. i.e.
a dictionary containing (at least):

- `string`:   The bytes of the content (yes ... it says string but it's bytes).

- `mimetype`: The MIME type of the content.

URL fetchers should raise a
<a href="#docma.exceptions.DocmaUrlFetchError">`DocmaUrlFetchError`</a>
on failure.

"""

import pkgutil
from importlib import import_module

from .__common__ import (
    get_url_fetcher_for_scheme as get_url_fetcher_for_scheme,
    url_fetcher as url_fetcher,
)

# Auto import our URL fetcher functions
for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name.startswith('_'):
        continue
    import_module(f'.{module_name}', package=__name__)


__all__ = ['get_url_fetcher_for_scheme', 'url_fetcher']
