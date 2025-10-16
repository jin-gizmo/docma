
# Docma Template Rendering [nav: Template Rendering]

The document rendering phase combines a compiled **docma** template with run-time
specified parameters and dynamically generated content to produce a final output
document.

The rendering process is slightly different for PDF and HTML outputs.

## Rendering for PDF Outputs

![](img/render-phase-pdf.svg)

The main steps in the process for PDF production are:

1.  Marshal the [rendering parameters](#rendering-parameters).

2.  [Validate the rendering parameters](#docma-parameter-validation).

3.  Collect the list of documents to be incorporated into the final output PDF.

4.  [Render HTML documents](#docma-jinja-rendering) in the component list using
    Jinja to inject the [rendering parameters](#rendering-parameters).

5.  Convert the HTML documents to PDF using [WeasyPrint](https://weasyprint.org/).
    This process will also generate any [dynamic content](#dynamic-content-generation)
    from specifications embedded in the source HTML.

6.  Assemble all of the components (generated PDFs and any listed static PDFs)
    into a single PDF document.

7.  Add any requested [watermarking or stamping](#watermarking) to the document.

8.  Jinja render any required metadata specified in the
    [template configuration file](#template-configuration-file) and add it to
    the PDF.

9.  Optionally, compress the PDF using lossless compression. Depending on the
    PDF contents, compression may, or may not, help.

## Rendering for HTML Outputs

![](img/render-phase-html.svg)

The main steps in the process for HTML production are:

1.  Marshal the [rendering parameters](#rendering-parameters).

2.  [Validate the rendering parameters](#docma-parameter-validation).

3.  Collect the list of documents to be incorporated into the final output HTML.

4.  [Render HTML documents](#docma-jinja-rendering) in the component list using
    Jinja to inject the [rendering parameters](#rendering-parameters).

5.  Process `<IMG>` tags in the HTML to generate and embed any
    [dynamic content](#dynamic-content-generation) from specifications embedded
    in the source HTML. Static images may also be embedded.

6.  Assemble all of the component HTML documents into a single HTML document.

8.  Jinja render any required metadata specified in the
    [template configuration file](#template-configuration-file) and add it to
    the HTML.

