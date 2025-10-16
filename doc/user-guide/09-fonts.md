
# Fonts

!!! note
    This section primarily applies to PDF output documents. For HTML output
    documents, font handling is exactly as it is for HTML in general. **Docma**
    does not embed fonts in HTML output documents.

**Docma** inherits the [font handling capabilities of
WeasyPrint](https://doc.courtbouillon.org/weasyprint/v0.42.3/features.html#fonts),
which are essentially those of native HTML / CSS. TrueType (TTF), OpenType (OTF)
and Web Open Font Format (WOFF), and, more recently, WOFF2, fonts should work fine.

!!! warning
    Fonts are Intellectual Property and may be subject to licence conditions,
    just like software. Take care to comply with licence terms and be aware that
    the font is likely to be embedded in the PDF produced by **docma**.
    [Google fonts](https://fonts.google.com) is quite a good source for royalty
    free fonts.

Fonts installed on the base platform generally can be used directly in CSS
styles. However, it is risky to rely on this beyond the most basic common font
types (e.g. Sans Serif). A template that is developed and compiled on one
platform may be rendered on a different platform with different fonts. It will
still render, in most cases, but may not look as expected.

Fonts that are not installed on the base platform can be used via `@font-face`
CSS directives in either stand-alone style sheets or within CSS in the HTML.
These specify where to find the font files and how to reference them from HTML /
CSS.  These fonts can be either:

1.  Placed in the **docma** template source directory for inclusion into the
    compiled template; or

2.  Imported into the document template during compilation via an
    [import directive](#document-imports); or

3.  Loaded at run-time during template rendering using standard HTML / CSS
    features for remote font access.

!!! tip
    Option 3 is strongly deprecated for performance reasons.

## Fonts Included in the Template Source

A font file can be placed directly into the document template source directory.
It is recommended to place fonts in the `fonts` sub-directory. e.g.

```bare
<template-base-dir>
│
├── css
│   └── pdf.css
├── ...
├── fonts
│   └── my-corporate-font.ttf
└── ...
```

The font then needs to be declared in CSS. This can be in a standalone
style sheet invoked via the `options->stylesheets` key in the template
configuration file (PDF output only) or directly within a `<STYLE>...</STYLE>` 
block in a HTML document.

```css
@font-face {
    font-family: 'CorpFont';
    src: url(file:fonts/my-corporate-font.ttf) format('truetype');
}
```

!!! info
    In **docma** versions <= 1.9, the font-face declaration must be in the HTML
    document using it. In versions >= 1.10, the declaration can also be in a
    separate style sheet (preferred).

This makes the font available for use in CSS styling in the normal way. e.g.

```html
<HTML lang="en-us">
<HEAD>
  <STYLE type="text/css">
      .corpfont {
          font-family: CorpFont, sans-serif;
      }
  </STYLE>
</HEAD>
<BODY>
  <P style="corpfont">
    Hello world!
  </P>
</BODY>
</HTML>
```

## Importing Fonts during Template Compilation

Remote fonts can be incorporated into a document template during the compilation
phase using the [imports directive](#document-imports) in the [template
configuration file](#template-configuration-file) .

For example, to include the *Kablammo* font from Google fonts, `config.yaml`
would contain something like this:

```yaml
# config.yaml

imports:
  - src: https://fonts.gstatic.com/s/kablammo/v1/bWtm7fHPcgrhC-J3lcXhcQTY5Ixs6Au9YgCjjw.ttf
    as: fonts/kablammo.ttf

options:
  stylesheets:
    - css/pdf.css
```

For PDF output, the font declaration can then go into `css/pdf.css` (or any
other style sheet being referenced in the document content HTML) like so:

```css
@font-face {
    font-family: 'Kablammo';
    font-style: normal;
    font-weight: 400;
    src: url(file:fonts/kablammo.ttf) format('truetype');
}
```

!!! info
    In **docma** versions <= 1.9, the font-face declaration must be in the HTML
    document using it. In versions >= 1.10, the declaration can also be in a
    separate style sheet (preferred).

This makes the font available for use in CSS styling, thus:

```html
<HTML lang="en-us">
<HEAD>
  <STYLE type="text/css">
      .kablammo {
          font-family: Kablammo, sans-serif;
      }
  </STYLE>
</HEAD>
<BODY>
  <P style="kablammo">
    Hello world!
  </P>
</BODY>
</HTML>
```

## Loading Fonts during Template Rendering

Fonts can also be dynamically loaded at run-time during template rendering using
standard HTML / CSS mechanisms. 

!!! tip
    Best to avoid doing this in a production environment when producing PDF output.

For example, the following shows two different mechanisms for incorporating the
*Barrio* and *Dokdo* fonts from Google Fonts using HTML `<link>` and CSS
`@import` mechanisms, respectively.

```html
<HTML lang="en-us">
<HEAD>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

  <link href="https://fonts.googleapis.com/css2?family=Barrio" rel="stylesheet">

  <STYLE type="text/css">
      @import url('https://fonts.googleapis.com/css2?family=Dokdo');

      .barrio {
          font-family: "Barrio", system-ui;
          font-weight: 400;
          font-style: normal;
      }

      .dokdo {
          font-family: "Dokdo", system-ui;
          font-weight: 400;
          font-style: normal;
      }

  </STYLE>
</HEAD>
<BODY>
  <P class="barrio">
    Hello world!
  </P>

  <P class="dokdo">
    Hello world!
  </P>
</BODY>
</HTML>
```
