# ruff: noqa: E501
"""
Data providers access external data sources (e.g. databases) as part of template rendering.

They are referenced in HTML content via a
[data source specification][data-source-specifications] containing
these elements:

-   type
-   location
-   query
-   target.

See <a href="#docma.data_providers.DataSourceSpec">`DataSourceSpec`</a> for
details on what the components mean.

Data providers must have the following signature:

!!! info "Data Provider Signature"

    ```python
    @data_provider(*src_type: str)
    def whatever(
        data_src: DataSourceSpec,
        context: DocmaRenderContext,
        params: dict[str, Any],
        **kwargs,
    ) -> list[dict[str, Any]]:
    ```

|Name|Type|Description|
|-|-|-|
|`data_src`|<a href="#docma.data_providers.DataSourceSpec">`DataSourceSpec`</a>|The data source specification.|
|`context`|`DocmaRenderContext`|The template package. This allows the content generator to access files in the template, if required.|
`params`|`dict[str, Any]`|The run-time rendering parameters provided during the render phase of document production.|
|`kwargs`|`Any`|This is a sponge for spare arguments. Some handlers don't require the `params` argument.|

Data providers must return a list of dictionaries, where each dictionary
contains one row of data. This is the format required by Altair-Vega and is also
suitable for consumption in Jinja templates.

Data providers should generally raise a
<a href="#docma.exceptions.DocmaDataProviderError">`DocmaDataProviderError`</a>
on failure.
"""

import pkgutil
from importlib import import_module

from .__common__ import (
    DataSourceSpec as DataSourceSpec,
    data_provider as data_provider,
    load_data as load_data,
)

# Auto import our data provider functions
for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name.startswith('_'):
        continue
    import_module(f'.{module_name}', package=__name__)

__all__ = ['DataSourceSpec', 'data_provider', 'load_data']
