"""
Data providers access external data sources (e.g. databases) as part of template rendering.

They are referenced in HTML content via a data source spec containing these
elements:

-   type
-   location
-   query
-   target.

See DataSourceSpec for details on what the components mean.

Data providers receive the following arguments:

-   data_src:   The data source (DataSourceSpec).
-   pkg:        The template package. This allows the content generator to
                access files in the template, if required.
-   params:     The run-time rendering parameters provided during the render
                phase of document production.

Data providers must return a list of dictionaries, where each dictionary
contains one row. This is the format required by Altair-Vega and is also
suitable for consumption in Jinja templates.

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
