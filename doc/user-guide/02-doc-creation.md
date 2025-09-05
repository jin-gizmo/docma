
# Document Creation

The docma document creation process consists of these steps:

1.  [Document template creation](#document-templates): The template content is
    contained in a directory dedicated to a single template. It contains the
    static content (e.g. HTML, PDF, Markdown and image files) as well as YAML
    formatted metadata files that control the rendering process, database access
    etc.

2.  [Template compilation](#docma-template-compilation): The compilation process
    validates the template content, converts supported non-HTML content (e.g.
    Markdown files) into HTML and generates a compiled template package
    in either a directory or ZIP file.

3.  [Template rendering](#docma-template-rendering): The rendering process
    uses Jinja to inject run-time parameters into the HTML template content,
    converts the component documents to PDF, if required, and composes all of
    the components into a single output PDF or standalone HTML document.

![](img/docma-high-level.svg)
