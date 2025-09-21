"""
Load data from a file in the document template package.

The location component of the data source is the path to the file.

If the file is a CSV file, it must have a header and use the excel dialect.

In the HTML for a Vega graph, this would look like this:

```html
<IMG src="docma:vega?spec=graph.yaml&data=file;data/x.csv">
```
Note there is no data_query for this source type.
"""

from __future__ import annotations

import json
from csv import DictReader
from io import StringIO
from pathlib import Path
from typing import Any

from docma.exceptions import DocmaDataProviderError
from docma.jinja import DocmaRenderContext
from .__common__ import DataSourceSpec, data_provider

READERS = {
    '.csv': lambda f: list(DictReader(f)),
    '.jsonl': lambda f: [json.loads(line) for line in f],
}


# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
@data_provider('file')
def file_loader(
    data_src: DataSourceSpec, context: DocmaRenderContext, **kwargs
) -> list[dict[str, Any]]:
    """Load data from the a file in the document template package."""

    if data_src.query:
        raise DocmaDataProviderError('Query not allowed for "file" data source type')

    path = Path(data_src.location)
    if (suffix := path.suffix) not in READERS:
        raise DocmaDataProviderError(f'Unknown file type "{suffix} for "file" data source')

    buf = StringIO(context.tpkg.read_text(path))
    return READERS[suffix](buf)
