
## Building the Documentation

Docma comes with this user guide and auto-generated API documentation.

To build the user guide, [Pandoc](https://pandoc.org) is required. For mac OS:

```bash
brew install pandoc
```

To build the documentation:

```bash
make doc
```

The generated documentation is placed in the `dist/doc` directory. On mac OS:

```bash
# Open the user guide
open -a Safari dist/doc/docma-user-guide.site/index.html

# Open the API doc
open -a Safari dist/doc/api/_build/html/index.html
```

By default, the user guide is generated in multi-page HTML, markdown and EPUB
formats. To also generate Microsoft Word (docx) and single page HTML, edit this
line in `doc/Makefile` to add `docx` and `html`:

```make
# FORMATS=md docx epub html site
FORMATS=md site epub
```

To edit the documentation, ensure that a spell check is done as part of the
process using:

```bash
make spell
```

This requires the `aspell` tool. For mac OS:

```bash
brew install aspell
```
