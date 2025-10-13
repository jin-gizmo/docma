"""
Content compilers turn non-HTML content into HTML content as part of template compilation.

They accept a single bytes argument containing source content and return a
string object containing HTML.
"""

import pkgutil
from importlib import import_module

from .__common__ import (
    compiler_for_file as compiler_for_file,
    compiler_for_suffix as compiler_for_suffix,
    content_compiler as content_compiler,
)

# Auto import our generator functions
for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name.startswith('_'):
        continue
    import_module(f'.{module_name}', package=__name__)

__all__ = ['compiler_for_file', 'compiler_for_suffix', 'content_compiler']
