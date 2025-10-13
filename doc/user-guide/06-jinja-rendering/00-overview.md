
# Docma Jinja Rendering [nav: Jinja Rendering]

The rendering phase uses Jinja to render HTML content with the parameters
provided at run-time. Other components (e.g.
[query specifications](#query-specifications)) also use Jinja rendering on some
of their content.

!!! note
    The docma Jinja subsystem has been refactored somewhat in v2.2.0.

All of the facilities provided by Jinja are available, including parameter
injection, loops, conditional content and use of the `include` directive to
incorporate other content from the document template. Include directives should
use the name of the file relative to the template root. e.g.

```jinja
{% include 'my-file.html' %}
```

See also [Jinja Rendering Parameters Provided by
Docma](#rendering-parameters-provided-by-docma).

In addition to standard Jinja facilities, docma also provides a number of extra
[filters](#docma-jinja-filters) and
[extensions](#docma-jinja-extensions).

