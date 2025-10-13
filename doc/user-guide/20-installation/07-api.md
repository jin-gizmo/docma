
## Docma Python API

The API is quite basic:

```python
from docma import compile_template, render_template_to_pdf

template_src_dir = 'a/b/c'
template_location = 'my-template.zip'  # ... or a directory when experimenting
pdf_location = 'my-doc.pdf'
params = {...}  # A Dict of parameters.

compile_template(template_src_dir, template_location)

pdf = render_template_to_pdf(template_location, params)

# We now have a pypdf PdfWriter object. Do with it what you will. e.g.
pdf.write(pdf_location)
```

Refer to the [API documentation](#docma-api-reference) for more information.
