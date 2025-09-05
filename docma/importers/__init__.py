"""
Content mporters bring in external content when compiling a document template package.

They accept a single URL style argument and return bytes with the content. The
scheme from the URL is used to select the appropriate import handler.
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
