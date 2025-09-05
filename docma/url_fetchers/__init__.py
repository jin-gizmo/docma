"""
WeasyPrint URL fetchers for various URL schemes.

If a fetcher is not found here, the default URL fetcher is used.
"""

import pkgutil
from importlib import import_module

from .__common__ import (
    get_url_fetcher_for_scheme as get_url_fetcher_for_scheme,
)

# Auto import our URL fetcher functions
for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name.startswith('_'):
        continue
    import_module(f'.{module_name}', package=__name__)
