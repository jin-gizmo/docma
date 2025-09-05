"""
Load data from the run-time rendering parameters.

The location component of the data source is a dot separated key sequence
to select part of the params dict.

In the HTML for a Vega graph, this would look like this:

```html
<IMG src="docma:vega?spec=graph.yaml&data=params;a.param.with.values">
```

Note there is no data_query for this sourc type.
"""

from __future__ import annotations

from typing import Any

from docma.exceptions import DocmaDataProviderError
from docma.lib.core import DocmaRenderContext
from docma.lib.misc import dot_dict_get
from .__common__ import DataSourceSpec, data_provider


# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
@data_provider('params')
def params_loader(
    data_src: DataSourceSpec, context: DocmaRenderContext, **kwargs
) -> list[dict[str, Any]]:
    """Load data from the run-time rendering parameters."""

    if data_src.query:
        raise DocmaDataProviderError('Query not allowed for "params" data source type')

    data = dot_dict_get(context.params, data_src.location)

    if not isinstance(data, list):
        raise DocmaDataProviderError(f'Parameter {data_src.location} is not a list')

    return data
