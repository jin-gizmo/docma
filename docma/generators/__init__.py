"""
Docma content generators produce dynamic content (e.g. charts) as part of template rendering.

They are activated in a HTML file in a docma template by invoking a URL in the
form:

```
docma:<content-type>?option1=value1&option2=value2
```

.. warning::
    Do not use `docma://` as that implies a netloc which is not used here.

Content generators receive the following arguments:

-   pkg: The template package. This allows the content generator to access
    files in the template, if required.

-   params: The run-time rendering parameters provided during the render phase
    of document production.

-   options: The query parameters as a Pydantic BaseModel.

Content generators return the value required of a Weasyprint URL fetcher. i.e.
a dictionary containing (at least):

- string:   The bytes of the content (yes ... it says string but it's bytes).

- mimetype: The MIME type of the content.

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
