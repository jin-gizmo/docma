
## Extending Docma

Docma has a number of plugable interfaces to allow extension. The process works
by placing a Python file in the appropriate directory in the code base, unless
otherwise indicated. These are automatically discovered as required.

### Content Importers

Content importers operate during the docma [compile](#docma-template-compilation)
phase. They collect components from external sources and inject them into the
compilation process.

Imported components are referenced via a URL `scheme://....`. The `scheme` is
used to select the importer to be used.

To create a new importer, add a new Python file into `docma/importers`. It will
contain a decorated function that has a signature like so:

```python
@content_importer('http', 'https')
def _(uri: str, max_size: int = 0) -> bytes:
    """Get an object from the web."""
    ...
```

### Content Compilers

Content compilers operate during the docma [compile](#docma-template-compilation)
phase. They transform a source format into HTML. The source format is determined
by the filename suffix.

To create a new compiler, add a new Python file into `docma/compilers`. It will
contain a decorated function that has a signature like so:

```python
@content_compiler('xyz')
def _(src_data: bytes) -> str:
    """Compile xyz source files into HTML."""

    return ...
```

### URL Fetchers

[URL fetchers](#dynamic-content-generation) operate during the docma
[render](#docma-template-rendering) phase.  They provide WeasyPrint with the
means to resolve URLs within the HTML being converted to PDF.

URL fetchers are selected based on the scheme of the URL.

To create a new URL fetcher, add a new Python file into `docma/fetchers`.
For example, to handle URLs of the form `xyz://....`, the new file will have a
function with a signature like so:

```python
@fetcher('xyz')
def _(purl: ParseResult, context: DocmaRenderContext) -> dict[str, Any]:
    """
    Fetch xyz:... URLs for WeasyPrint.

    :param purl:    A parsed URL. See urllib.parse.urlparse().
    :param context: Document rendering context.
    

    :return:        A dict containing the URL content and mime type.
    """

    ...

    return {
        'string': ...,  # This is named `string` but must be a bytestring.
        'mime_type': ...

    }
```

### Content Generators

[Content generators](#dynamic-content-generation) operate during the docma
[render](#docma-template-rendering) phase. They dynamically generate content for
WeasyPrint when a URL in the following form is accessed.

```bare
docma:<generator-name>?<generator-params>
```

They are typically used for generating image content
(charts, QR codes etc.) but they can be used wherever URLs return content to
WeasyPrint.

To create a new content generator, add a new Python file into
`docma/generators`. Start by copying the sample `swatch.py` generator and
modifying as required.

### Data Providers

[Data providers](#data-sources-in-docma) operate during the docma
[render](#docma-template-rendering) phase.

The data provider handler is selected by the `type` component of a
[data source specification](#data-source-specifications).

To create a new data provider, add a new Python file into `docma/data_providers`.
Start by copying one of the existing providers and modify as needed.

### JSON Schema Format Checkers

Docma has a number of custom
[JSON Schema format checkers](#custom-json-schema-formats-provided-by-docma).
These are all contained in the file `docma/lib/jsonschema.py`. New ones can be
added to this file.

### Custom Jinja Filters and Extensions

Docma has a number of custom Jinja
[filters](#custom-jinja-filters-provided-by-docma) and
[extensions](#custom-jinja-extensions-provided-by-docma).
These are all contained in the file `docma/lib/jinja.py`. New ones can be
added to this file.

