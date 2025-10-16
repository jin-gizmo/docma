

## Document Template Content

The `documents` and `overlays` keys in the document template
[configuration file](#template-configuration-file) list the files that will be
processed and assembled to produce the final PDF document.

Two types of file are permitted in these lists:

1.  HTML files (`*.html` / `*.htm`)

2.  PDF files (`*.pdf`) (PDF output only).

The HTML files may be either files directly constructed by the template author,
files that have been imported via the `imports` key, or HTML that has been
compiled from other formats (e.g. Markdown) during the template compilation
phase.

For compiled files, the original file suffix indicates the content type and
hence the process used to compile it to HTML format.

The [content compiler](#content-compilers) interface is extensible. New file
types can be added easily.

### HTML Files (\*.html, \*.htm)

When producing standalone HTML outputs, normal HTML conventions should be
followed, keeping in mind the limitations of the target rendering environment
(e.g. a variety of email clients).

When producing PDF outputs, the source HTML used in a **docma** template should be
written explicitly for print, rather than web layout. There are a set of special
HTML constructs available when the target media is print. Effective use of
these is essential to producing nice output. For an excellent short tutorial on
the subject, see [Designing For Print With
CSS](https://www.smashingmagazine.com/2015/01/designing-for-print-with-css/)

HTML source files are copied unchanged to the compiled **docma** template during the
compilation phase.

HTML files can reference other resources in the compiled template (e.g. images,
style sheets etc.) using URLs in the format `file:filename`. For example

```html
<IMG src="file:resources/logo.png" alt="logo">
```

!!! warning
    The `file:` scheme indicator is essential. The filename is relative to the
    template base directory. Do not use `file://` as that implies a network
    location will follow, which makes no sense for local files.

HTML files may contain [Jinja](https://jinja.palletsprojects.com/en/) markup to
manipulate content during the [rendering phase](#docma-template-rendering).

!!! tip
    Take care when re-purposing HTML content from other systems that may leave
    Jinja detritus behind. This may need to be manually deleted first.

HTML files can also reference dynamic content generators that will be invoked
during the [rendering phase](#docma-template-rendering). This can be used to
include content for charts, QR codes etc. Dynamic content generators are
accessed by referencing a URL with the `docma` scheme.

For example, the following will generate and insert a QR code:

```html+jinja
<IMG
  src="docma:qrcode?{{
    {
      'text': 'Hello world!',
      'fg': 'white',
      'bg': '#338888'
    } | urlencode
  }}"
>
```

This is the same thing, more cryptically:

```html
<IMG src="docma:qrcode?text=Hello+world%21&fg=white&bg=%23338888">
```

See [Dynamic Content Generation](#dynamic-content-generation) for more
information.

Important points to note:

*   The [WeasyPrint](https://weasyprint.org) package is designed to convert HTML
    for print to PDF. It does an excellent job, but some constructs take a bit
    of fiddling to get right. It seems to be more aligned to Safari behaviour
    than, say, Chrome, if that helps when previewing template components.

*   HTML produced by some WYSIWYG editors can be a tortured, gnarly mess.
    WeasyPrint may struggle with it. In many cases, it's better to hand-write
    lean, clean HTML using an IDE or an AI crutch of some kind.

### PDF Files (\*.pdf)

!!! info
    PDF output only.

PDF files in the template are copied to the compiled template unchanged. They
are simply added into the final document composition process as-is. This is
useful for boilerplate content, such as contract terms and conditions.

PDF files are not Jinja rendered during compilation. Once again, they are used
as-is.

### Markdown Files (\*.md)

All Markdown files are converted to HTML during the compilation phase. i.e.
`myfile.md` in the template source becomes `myfile.html` in the compiled
template.

!!! warning
    The HTML variant of the name **must** be used everywhere in the template when
    referencing the file.

Markdown files may contain [Jinja](https://jinja.palletsprojects.com/en/) markup
to manipulate content during the [rendering phase](#docma-template-rendering).

Conversion from Markdown to HTML is done using the Python
[markdown](https://python-markdown.github.io) package with the following
[extensions](https://python-markdown.github.io/extensions/) enabled:

*   extras
*   admonition.

Important points to note:

*   The conversion from Markdown to HTML will *not* add
    `<HTML>...<BODY></BODY></HTML>`
    framing around the result. This is an advantage, as it means the content can
    be included in other documents using Jinja `{% include 'myfile.html' %}`
    directives. If a Markdown originated source file is to be used stand-alone,
    a small HTML wrapper that references the content file may be needed to
    provide the HTML framing, style sheet etc.

*   The Markdown format is particularly suited to longer, textual content.
    It is a lot easier to edit and maintain than HTML, but complex styling is
    more difficult. The Python [markdown](https://python-markdown.github.io)
    package has some non-standard extensions that do help with this.

