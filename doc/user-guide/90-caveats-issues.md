
# Caveats and Known Issues [nav: Caveats and Issues]

*   Docma does not try particularly hard to be parsimonious with memory usage.

*   Docma does pool database connections, but the approach to doing this is
    fairly naive and may need to be revisited for higher volumes.

*   Watch out for HTML authoring systems that leave Jinja-like fragments behind.
    These *will* clash with docma's use of Jinja and will generally need to be
    removed.

*   WeasyPrint suppresses some errors when rendering HTML and tries hard to
    produce something. This is unfortunate. In docma, it would have been
    preferable to fail if rendering fails to avoid an incomplete document.

*   Internal document links within the rendered PDF don't work.
