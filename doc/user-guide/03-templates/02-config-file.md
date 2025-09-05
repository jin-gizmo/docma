

## Template Configuration File

The document template configuration file, `config.yaml`, is critical to the
setup and operation of a **docma** template. The structure of the configuration
file is validated during template compilation. It contains the following
elements.

| Key            | Type           | Required | Description                                                  |
| -------------- | -------------- | -------- | ------------------------------------------------------------ |
| id             | string         | Yes      | Template identifier. This must be at least 3 chars long, start with an alpha, end with an alphanumeric and contain only alpha-numerics and `+-_=` characters. |
| description    | string         | Yes      | Template description.                                        |
| owner          | string         | Yes      | Template owner.                                              |
| version        | string         | Yes      | Template version. Must be in the form major.minor.patch (e.g. `1.0.0`). |
| documents      | list           | Yes      | A list of [document references](#document-references) to be included in the specified order in the output document. |
| overlays       | object         | No       | Document overlay specifications to enable watermarking / stamping of the output document (PDF only). See [Watermarking](#watermarking) below. |
| imports        | list           | No       | A list of specifications for external files to include during compilation. See [Document Imports](#document-imports) below. |
| parameters     | object         | No       | Contains optional keys `defaults` and `schema`.              |
| -> defaults    | object         | No       | Default values for rendering parameters.                     |
| -> schema      | object         | No       | A JSON Schema for the rendering parameters. See [Docma Parameter Validation](#docma-parameter-validation). |
| options        | object         | No       | Options passed to the WeasyPrint PDF generator. See [WeasyPrint Options](#weasyprint-options). |
| -> stylesheets | list           | No       | A list of CSS style sheet files that will be fed to the PDF generator. See [CSS Style Sheets](#css-style-sheets) below. |
| metadata       | object         | No       | Values to be added to the output document metadata. See [Document Metadata](#document-metadata) below. |
| -> author      | string         | No       | Document author.                                             |
| -> title       | string         | No       | Document title.                                              |
| -> subject     | string         | No       | Document subject.                                            |
| -> keywords    | string \| list | No       | A string of semi-colon separated keywords or a list of keywords for the PDF. |

> Prior to docma v2.0, metadata fields were specified in the PDF convention of
> `/Author` instead of `author`. This is still supported for backward
> compatibility but the naming shown above should now be used. Docma will use
> the appropriate conventions for PDF and HTML when producing output.

### Document References

The `documents` key in the configuration file is a list of component documents
that will be rendered and assembled into the final output document.

Each element in the document list can be either a string containing the name of
a content file or an object containing the following keys:

| Key | Type   | Required | Description                                                                   |
| --- | ------ | -------- | ----------------------------------------------------------------------------- |
| src | string | Yes      | Name of a content file.
| if  | string | No       | A string that will be Jinja rendered with the run-time parameters and evaluated as a truthy value. If the value is true (the default), the document is included. Truthy *true* values are  `true` / `t` / `y` / `yes` and non-zero integers. Truthy *false* values are `false` / `f` / `no` / `n` and zero and empty strings.|

Content files must be of one of the following types:

*   HTML (`*.html` / `*.htm`)
*   PDF (`*.pdf`) (for PDF output documents only)

Content files can (and generally should) be contained within the template source
directory hierarchy. The file is referenced by its path relative to the template
source base directory.

Content files can also be remote and will be loaded dynamically during the
rendering process. This differs from [document imports](#document-imports) which
incorporate the document into the template during template compilation.
For remote content files, any of the forms supported by the importer subsystem
can be used. e.g.

*   `http(s)://host/some/path/...`
*   `s3://bucket/some/path/...`

Unlike imports, dynamically referenced content documents must be in HTML or PDF
format. There is no compilation of other formats to HTML.

> It is *strongly* recommended to include all content files in the template
> itself (e.g using [document imports](#document-imports) for remote files).
> This will be faster and more predictable at run-time as well as
> improving traceability of documents.

For example:

```yaml
documents:
  - content/cover.html
  # Our main contract document template
  - content/contract.html
  # Boilerplate PDF to include
  - content/standard-terms.pdf
  # Reference to a file in S3
  - s3://my-content-bucket/extra-terms.pdf
  # Now a conditional document using evaluated parameters.
  # The "if" condition will evaluate to the string "True" or "False".
  - src: content/even-more-terms.pdf
    if: '{{ contract.term_in_years >= 3 }}'
```

Some of the HTML files may have been compiled from other formats (e.g.
Markdown) during the compilation phase. All references to the file during
rendering must use the HTML file name. So, for example, a file `content/text.md`
in the template source, will be present as `content/text.html` in the compiled
template.

> The original, uncompiled files are also replicated into the template to allow
> later recompilation and for traceability. The uncompiled files are not used in the rendering process.

See [Document Template Content](#document-template-content) for more
information.

### Overlay Documents

> PDF outputs only.

The `overlays` key in the configuration file is a list of documents that are
prepared in the same way as the primary documents. These are used when the final document requires
an overlaid stamp or underlaid watermark. See [Watermarking](#watermarking) for
more information.


### Document Imports

The [configuration file](#template-configuration-file) may contain an `imports`
key to specify a list of external files that will be included within the
compiled template package. The imported file is processed just like a local
file, including compilation of supported non-HTML formats (e.g. Markdown) into
HTML.

Imports are specified as a URL, with the URL scheme determining the means of
access. Imports are currently supported for:

*   AWS S3: `s3://....`

*   Web content: `http(s)://...`

The [content importers interface](#content-importers) is extensible. New sources
can be added easily.

Each import specification is either a string or an object, like so:

```yaml
imports:

  # Simple string format. This S3 file will be placed in the template based on
  # the last component of the filename (i.e `myfile.pdf`).
  - s3://my-bucket/some/path/myfile.pdf

  # Object format to allow a file to be imported and renamed in the process.
  # This will copy the file into the template as `content/afile.pdf`.
  - src: s3://my-bucket/some/path/myfile.pdf
    as: content/afile.pdf

  # This Markdown file will be compiled and can be referenced elsewhere in the
  # template as "content/mydoc.html"
  - src: s3://my-bucket/some/path/somedoc.md
    as: content/mydoc.md

  # Import an image
  - src: http://a.url.com/some/image.png
    as: resources/image.png

  # Import a font:
  - src: http://host/my-corporate-font.ttf
    as: fonts/my-corporate-font.ttf
```

> Imported docs are limited to 10MB in size.

### WeasyPrint Options

> PDF outputs only.

WeasyPrint is used for converting HTML to PDF for PDF document production.  It
provides a number of
[options](https://doc.courtbouillon.org/weasyprint/stable/api_reference.html#weasyprint.DEFAULT_OPTIONS)
to control aspects of the PDF production process. These can be specified under
the `options` key of the [template configuration
file](#template-configuration-file).

The following options are set by docma itself. They can be overridden in the
template but it's best not to.

|Option|Value set by docma| Notes |
|-|-|------|
|media|print| |
|optimize\_images|True|This is required to avoid an image loading bug in WeasyPrint.|

### CSS Style Sheets

> PDF outputs only.

The [configuration file](#template-configuration-file) may contain an `options
--> styesheets` key that lists files containing style sheets that will be
applied to _all_ HTML document files when converting them to PDF. Hence, these
files should only contain styles that should be applied everywhere.

In some cases, including for HTML outputs, it will be more appropriate to have
styles defined within the HTML source document to which they relate, or included
from CSS files using the Jinja `include` directive.

### Sample Configuration File

A sample file might look like this:

```yaml
description: Contract of Sale
owner: Cest Moi
version: 1.0.0

# List the primary files containing document content. File names are relative to
# the root of the template.
documents:
  - content/cover.html
  # Our main contract document template
  - content/contract.html
  # Boilerplate PDF to include
  - content/standard-terms.pdf
  # Now a conditional document using evaluated parameters.
  # The "if" condition will evaluate to the string "True" or "False".
  - src: content/extra-terms.pdf
    if: '{{ contract.term_in_years >= 3 }}'

# Bring these files into the package when building the template.
imports:
  - src: s3://my-bucket/common-files/standard-terms.pdf
    as: content/standard-terms.pdf

# Used in the HTML to PDF conversion
options:
  stylesheets:
    - styles.css

parameters:
  # These defaults are deep-merged into any parameters specified at run-time
  # during rendering.
  defaults:
    our_abn: 54321123456
    contract:
      term_in_years: 3
  # JSON Schema used to validate parameters supplied at run-time.
  schema:
    $schema: https://json-schema.org/draft/2020-12/schema
    title: Parameters validation schema
    type: object
    required:
      - customer_name
      - customer_abn
      - contract
      - price
    properties:
      customer_name:
        type: string
        minLength: 1
      customer_abn:
        type: string
        format: ABN
      contract:
        type: object
      price:
        type: number
        minimum: 1.00

# This gets Jinja rendered and added as metadata to the output PDF.
metadata:
  /Title: Contract of Sale
  /Subject: '{{ customer_name }}'

```
