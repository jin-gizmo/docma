# Docma -- Document Manufacturing for Fun and Profit

**Docma** is a document generator that can assemble and compose PDF and HTML
documents from document templates with dynamic, data driven content.

[![PyPI version](https://img.shields.io/pypi/v/docma)](https://pypi.org/project/docma/)
[![Python versions](https://img.shields.io/pypi/pyversions/docma)](https://pypi.org/project/docma/)
![PyPI - Format](https://img.shields.io/pypi/format/docma)
[![GitHub License](https://img.shields.io/github/license/jin-gizmo/docma)](https://github.com/jin-gizmo/docma/blob/master/LICENCE.txt)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Genesis

**Docma** was developed at [Origin Energy](https://www.originenergy.com.au)
as part of the *Jindabyne* initiative. While not part of our core IP, it proved
valuable internally, and we're sharing it in the hope it's useful to others.

Kudos to Origin for fostering a culture that empowers its people
to build complex technology solutions in-house.

[![Jin Gizmo Home](https://img.shields.io/badge/Jin_Gizmo_Home-d30000?logo=GitHub&color=d30000)](https://jin-gizmo.github.io)

## Features

**Docma** features include:

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

## Installation and Usage

See the [user guide](https://jin-gizmo.github.io/docma/) for details.
