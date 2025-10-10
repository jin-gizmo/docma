"""
Primary docma API for compiling and rendering document templates.

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

from pathlib import Path

from .docma_core import (
    compile_template as compile_template,
    get_template_info as get_template_info,
    read_template_version_info as read_template_version_info,
    render_template_to_html as render_template_to_html,
    render_template_to_pdf as render_template_to_pdf,
    safe_render_path as safe_render_path,
)

__version__ = (Path(__file__).parent / 'VERSION').read_text().strip()
__author__ = 'Murray Andrews'

__all__ = [
    'compile_template',
    'get_template_info',
    'read_template_version_info',
    'render_template_to_html',
    'render_template_to_pdf',
    'safe_render_path',
]
