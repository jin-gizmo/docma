## Rendering Parameters

The parameters used by **docma** during the template rendering process is the union
of the following (from highest to lowest precedence):

1.  [Parameters provided by **docma**](#rendering-parameters-provided-by-docma).

2.  Parameters supplied by the user at run-time.

3.  Parameters specified under `parameters->defaults` in the
    [template configuration file](#template-configuration-file)

Parameters are any object that can be represented in JSON / standard YAML, which
can include arbitrary combinations of objects, lists and scalar values.

The marshalling process *deep-merges* the parameter trees from each source. Lists
are not merged. One list will replace another if they occur at the same location.

### Rendering Parameters Provided by Docma { data-toc-label="Parameters Provided by Docma" }

In addition to user supplied parameters, **docma** includes the following items
under the `docma` key.

| Key      | Notes | Description                   |
| ---------------------- |--| ----------------------------- |
| calendar | | The Python `calendar` module. |
| data     | | Function to invoke a [**docma** data provider](#data-sources-in-docma) and return the data as a list of dictionaries. See [Data Source Specifications for HTML Rendering](#data-source-specifications-for-html-rendering).|
| datetime | | The Python `datetime` module. |
| format | | The format of the output document to be produced, `PDF` or `HTML`. This can be used, among other things, for format specific content or formatting (e.g. CSS variations). |
| paramstyle | (1) |Corresponds to the DBAPI 2.0 `paramstyle` attribute of the underlying database driver when processing a  [query specification](#query-specifications). |
| template | | An object containing information about the document template.|
| --> description | | The `description` field from the [template configuration file](#template-configuration-file).|
| --> doc\_no |(2)| The document number in the list being included in the final document, starting at 1. |
| --> document |(2)| The path for the source document being processed. This is a pathlib `Path()` instance.|
| --> id   | | The `id` field from the [template configuration file](#template-configuration-file).|
| --> overlay\_id |(3) | The ID of the current overlay set being rendered. |
| --> overlay\_path |(3) | The path for the current overlay file being rendered. This is a pathlib `Path()` instance.|
| --> page |(2) | The starting page number for the current document with respect to the final output document. This may be useful for manipulating page numbering in multipart documents. Or not.|
| --> version | | The `version` field from the [template configuration file](#template-configuration-file).|
| version  | | The **docma** version. |

!!! note "Notes"
    1.  The `paramstyle` parameter is only available for use in
        [query specifications](#query-specifications).
    2.  The `template.doc_no`, `template.document` and `template.page` parameters
        are only available when a document file is being rendered (i.e. not when an
        overlay is being rendered). The `template.page` parameter is only available
        for PDF outputs.

    3.  The `template.overlay_id` and `template.overlay_path` parameters are only
        available when an overlay file is being rendered.

For example, to insert today's date:

```jinja
{{ docma.datetime.date.today() | date }} -- "date" filter formats for locale
```

To check whether we are producing HTML or PDF:

```jinja
This is {{ docma.format }} output using **docma** version {{ docma.version }}.
```

