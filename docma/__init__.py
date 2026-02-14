# ruff: noqa D404
"""
This is the primary docma API for compiling and rendering document templates.

Typical usage would be:

```python
from docma import compile_template, render_template

template_src_dir = 'a/b/c'
template_location = 'my-template.zip'  # ... or a directory when experimenting
pdf_location = 'my-doc.pdf'
params = { ... }  # A Dict of parameters.

compile_template(template_src_dir, template_location)

pdf = render_template_to_pdf(template_location, params)

# We now have a pypdf PdfWriter object. Do with it what you will. e.g.
pdf.write(pdf_location)
```

"""

# mkdocstrings needs this in order to discover the API.
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .docma_core import (
        compile_template,
        get_template_info,
        read_template_version_info,
        render_template_to_html,
        render_template_to_pdf,
        safe_render_path,
    )
    from .version import __version__

# ------------------------------------------------------------------------------
# These imports are pretty heavy duty. We don't want to pre-emptively import
# everything. Among other things, doing so makes CLI command completion run like
# a camel in a bog.
_LAZY_IMPORTS = {
    'compile_template': ('docma_core', 'compile_template'),
    'get_template_info': ('docma_core', 'get_template_info'),
    'read_template_version_info': ('docma_core', 'read_template_version_info'),
    'render_template_to_html': ('docma_core', 'render_template_to_html'),
    'render_template_to_pdf': ('docma_core', 'render_template_to_pdf'),
    'safe_render_path': ('docma_core', 'safe_render_path'),
    '__version__': ('version', '__version__'),
}


def __getattr__(name):
    """Lazy import heavy modules only when accessed."""
    try:
        module_name, attr_name = _LAZY_IMPORTS[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from importlib import import_module

    module = import_module(f'.{module_name}', package='docma')
    value = getattr(module, attr_name)
    globals()[name] = value  # Cache it
    return value


__all__ = [
    'compile_template',
    'get_template_info',
    'read_template_version_info',
    'render_template_to_html',
    'render_template_to_pdf',
    'safe_render_path',
    '__version__',
]


# ------------------------------------------------------------------------------
def __dir__():
    """Ensure dir() shows all public attributes."""
    return __all__
