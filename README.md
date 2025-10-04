# Docma -- Document Manufacturing for Fun and Profit

> [!NOTE]
> **About this project**
> 
> **Docma** was developed at [Origin Energy](https://www.originenergy.com.au) as part of the
> *Jindabyne* initiative. While not part of our core IP, it proved valuable
> internally, and we're sharing it in the hope it's useful to others.
> 
> Kudos to Origin for fostering a culture that empowers its people
> to build complex technology solutions in-house.

![](doc/img/docma-logo/svg/docma-logo-horizontal-light.svg)

## Overview

**Docma** is a document generator that can assemble and compose PDF and HTML
documents from document templates with dynamic, data driven content.

Features include:

*   Document content can be defined in any combination of HTML and PDF.

*   Content can also be defined in other formats that are compiled to HTML
    (e.g. Markdown, CSV).

*   Dynamic content preparation (conditionals, loops, transformation etc.) based
    on structured data parameters fed to the rendering process at run-time.

*   Composition of multiple source documents into a single output document.

*   Conditional inclusion of component documents based on parameter based 
    conditions evaluated at run-time.

*   Deep schema validation of structured data parameters at run-time.

*   Watermarking / stamping of PDF output.

*   Support for charts via the Vega-lite specification with multiple data
    sources, including live database connections.

*   Readily extensible to add new data sources and content types.

See the user guide for details.

## Credits

Thanks to MenaG for inspiring this idea in the first place.

Thanks to Alex Boul, and Art Dorokhov for contributing to **docma**.

**Docma** is possible because of these amazing Python packages:

*   [WeasyPrint](https://weasyprint.org)

*   [Jinja2](https://jinja.palletsprojects.com/en/)

*   [Vega-Altair](https://altair-viz.github.io/index.html)

*   [PyPDF](https://pypdf.readthedocs.io/en/stable/)

Honourable mentions:

*   [Babel](https://babel.pocoo.org/en/latest/)

*   [Phonenumbers](https://pypi.org/project/phonenumbers/)
