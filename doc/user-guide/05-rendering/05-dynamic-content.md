
## Dynamic Content Generation

When docma converts HTML into PDF or stand-alone HTML, it needs to resolve all
URLs in the source HTML in things such as `<img src="...">` tags. It does this
via a custom *URL fetcher* that allows content requests to be intercepted and
the resulting content generated dynamically. In this way, docma can generate
dynamic content, such as charts, for inclusion in the final output document.

> There are some differences in this process depending on whether the final
> output is PDF of HTML. See
[Dynamic Content Generation Differences Between PDF and HTML Output](#dynamic-content-generation-differences-between-pdf-and-html-output).

All URLs are constituted thus:

```bare
scheme://netloc/path;parameters?query#fragment
```

Docma determines which custom URL fetcher to apply based on the URL scheme (i.e.
the first part before the colon). The URL fetchers handle a range of non-standard,
docma specific schemes, as well as the standard `http` and `https` schemes.

Docma currently handles the following non-standard schemes:

| Scheme                 | Description                                                                |
|------------------------|----------------------------------------------------------------------------|
| [docma](#scheme-docma) | Interface to docma dynamic content generators of various types.            |
| [file](#scheme-file)   | Interface to access files contained within the compiled document template. |
| [s3](#scheme-s3)       | Interface to access files from AWS S3.                                     |

> The docma URL fetcher interface is easily expandable to handle other schemes.
> See [URL Fetchers](#url-fetchers).

### Dynamic Content Generation Differences Between PDF and HTML Output

PDF generation from HTML is performed by WeasyPrint, which will invoke a custom
URL fetcher for *any* URL it needs to access during the conversion process.
This includes, *but is not limited to*, `<IMG>` tags.

For standalone HTML output, the process of invoking a custom URL fetcher is done
by docma itself. It is *only* applied to the `src` attribute of `<IMG>` tags
under specific circumstances. When it is done, the `src` attribute is replaced
in the `<IMG>` tag with the actual content returned by the URL fetcher. i.e.
the data is embedded within the standalone HTML output.

In practice, these differences work naturally, relative to the final viewing
environment for the produced document, static PDF or dynamic HTML.

By default, in HTML outputs, `<IMG>` tags have the content embedded
in place of the `src` attribute in the following circumstances:

*   The `src` URL is not `http(s)://` (i.e. any of the docma custom
    schemes described below); or

*   The `src` URL is `http(s)://`, has no query component `?...`, 
    and the content size is between 100 bytes and 1MB in size.

For the `http(s)://` URLs, it is possible to override the default behaviour by
adding the `data-docma-embed` attribute to the `<IMG>` tag.

For images that are not embedded, it is assumed that the client (e.g. an email
client or web browser) will fetch the images as required at display time.

```html
<!-- Force the image to be embedded -->
<IMG src="http://host/img.png" data-docma-embed="true">

<!-- Prevent the image from being embedded -->
<IMG src="http://host/img.png" data-docma-embed="false">

<!-- This will not be embedded due to size unless we force it -->
<IMG src="http://host/multi-mega-byte-img.png">

<!-- This will not be embedded due to size unless we force it -->
<IMG src="http://host/one-pixel-img.png">

<!-- This will not be embedded due to query component unless we force it -->
<IMG src="http://host/do/something?x=20">

<!-- This will always be embedded and cannot be prevented -->
<IMG src="s3://my-bucket/corporate-logo.png">
```

### Scheme: docma

URLs of the following form are intercepted by docma and used to invoke a dynamic
content generator.

```bare
docma:<generator-name>?<generator-params>
```

Note that for these docma URLs, there is no *netloc* component and hence no `//`
in the URL.

For example, this will generate a QR code:

```html
<IMG style="height: 40px"
    src="docma:qrcode?text=Hello%s20world&fg=white&bg=red">
```

The URL should be properly URL encoded. This can be fiddly, but Jinja can help
here. The example above could also have been written in dictionary format thus:

```html
<IMG style="height: 40px" src=docma:qrcode?{{
  {
    'text': 'Hello world',
    'fg': 'white',
    'bg': 'red'
  } | urlencode
}}">
```

It could also have been written as a sequence of tuples:

```html
<IMG style="height: 40px" src=docma:qrcode?{{
  (
    ('text', 'Hello world'),
    ('fg', 'white'),
    ('bg', 'red')
  ) | urlencode
}}">
```
> The sequence format is **required** if any of the parameters needs to be used
> more than once.

Available content generators are:

| Name | Description |
|--|-----------------|
| [qrcode](#generating-qr-codes) | Generate a QR code. |
| [swatch](#generating-graphic-placeholders-swatches) | Generate a colour swatch as graphic placeholder. |
| [vega](#generating-charts-and-graphs) | Generate a chart based on the [Vega-Lite](https://vega.github.io/vega-lite/) declarative syntax for specifying charts / graphs. |

> The dynamic content generator interface is readily extensible to add new types
> of content. See [Content Generators](#content-generators).

#### Generating QR Codes

The QR code dynamic generator accepts the following parameters:

| Parameter | Type | Required | Description |
|-|-|-|------------------------|
| bg | String | No | Background colour of the QR code (e.g. `blue` or `#0000ff`). Default is white. |
| border | Integer | No | Number of boxes thick for the border. Default is the minimum allowed value of 4. |
| box | Integer | No | Number of pixels for each box in the QR code. Default is 10. |
| fg | String | No | Foreground colour of the QR code. Default is black. |
| text | String | Yes | Content to be encoded in the QR code. |

Examples:

```html
<IMG style="height: 40px"
    src="docma:qrcode?text=Hello%s20world&fg=white&bg=red">
```

```html
<IMG style="height: 40px" src=docma:qrcode?{{
  {
    'text': 'Hello world',
    'fg': 'white',
    'bg': 'red'
  } | urlencode
}}">
```

#### Generating Charts and Graphs

Docma supports the [Vega-Lite](https://vega.github.io/vega-lite/) declarative
syntax for specifying charts / graphs. Vega-Lite specifies a mapping between
source data and visual representations of the data. Docma provides mechanisms
for specifying and accessing various data sources and feeding this data through
a Vega-Lite specification to generate charts and graphs.

This is a large topic and more information is provided in
[Charts and Graphs in Docma](#charts-and-graphs-in-docma). To whet your appetite,
check out the [Vega-Lite sample gallery](https://vega.github.io/vega-lite/examples/).

This section just summarises the parameters for the `vega` content generator for
reference:

| Parameter | Type | Required | Description |
|-|-|-|------------------------|
| data | String | No | A [docma data source specification](#data-sources-in-docma). This argument can be repeated if multiple data sources are required.  If not specified, the file referenced by the `spec` parameter must contain all of the required data. |
| format | String | No | Either `svg` (the default) or `png`. Stick to `svg` if at all possible.|
| spec | String | Yes | The name of the file in the compiled document template that contains the Vega-Lite specification for the chart. The contents can be either YAML or JSON. |
| ppi | Integer | No | (`png` format only) Pixels-per-inch resolution of the generated image. Default 72. |
| scale | Float | No | (`png` format only) Scale the chart by the specified factor. Default is 1.0. Generally, it's better to control display size in the HTML but increasing the scale here can improve resolution. |
| params | JSON string | No | A string containing a JSON encoded object containing additional rendering parameters used when rendering the [chart specification](#chart-specification-files) and any associated [query specifications](#query-specifications). |

Examples:

```html
<IMG style="width: 5cm;"
    src="docma:vega?spec=charts/my-chart.yaml&data=...">
```

```html
<IMG style="width: 10cm;" src=docma:vega?{{
  (
    ( 'spec', 'charts/my-chart.yaml' ),
    ( 'data', 'file;data/my-data.csv' ),
    ( 'params', { 'extra_rendering_param': 1234 } | tojson)
  ) | urlencode
}}">
```

#### Generating Graphic Placeholders (Swatches)

The swatch generator produces a simple coloured rectangle with an optional text
message. It's not intended to be useful in final documents, Mondrian
notwithstanding. It has two purposes:

1.  As a simple code sample for dynamic content generators that can be copied
    and modified for new requirements.

2.  As a temporary placeholder when developing the structure of a docma template
    that will be replaced subsequently by a real piece of content (e.g. a chart).


| Parameter | Type | Required | Description |
|-|-|-|------------------------|
| color | String | No | Fill colour of the swatch. Default is a light grey. |
| font | String | No | Font file name for the text. Default is `Arial`. If the specified font is not available, a platform specific default is used.|
| font_size | Integer | No | Font size. Default is 18. |
| height | Integer | Yes | Swatch height in pixels. |
| text | String | No | Text to centre in the swatch. No effort is made to manipulate it to fit. |
| text_color | String | No | Colour for text. Default is black. |
| width | Integer | Yes | Swatch width in pixels. |

> **Colour** or **color**? The code and docma templates stick with `color`,
> because, well, that battle is lost. The user guide uses `colour` in descriptive
> text. Blame Webster for messing it up, not me.

Examples:

```html
<IMG src="docma:swatch?width=150&height=150&color=seagreen">
```

```html
<IMG src="docma:swatch?{{ {
    'width': 150,
    'height': 150,
    'color': '#0080ff',
    'text': 'Hello world',
    'text_color': 'yellow',
    'font_size': 24
    } | urlencode }}"
>
```

### Scheme: file

URLs in HTML files of the form `file:...` are intercepted by docma and the
content is extracted from a file within the compiled document template. As the
file is local to the template, there is no network location so the URL will be
like so:

```html
<IMG src="file:resources/logo.png" alt="logo">
```

> Do not include `//` after `file:`. It will not work.

### Scheme: s3

URLs in HTML files of the form `s3://...` are intercepted by docma and the
content is extracted from AWS S3. A typical usage would be something like:

```html
<IMG src="s3://my-bucket/some/path/logo.png" alt="logo">
```
> Files are limited to 10MB in size.
