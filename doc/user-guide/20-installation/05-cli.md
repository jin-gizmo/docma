
## The Docma CLI

The **docma** CLI provides everything required to compile and render document
templates.

```bash
# Get help
docma --help
```

It supports the following sub-commands.

| Command    | Description                                                       |
|------------|-------------------------------------------------------------------|
| compile    | Compile a source directory into a document template.              |
| html       | Render a document template to PDF.                                |
| html-batch | Render a batch of HTML documents from a single document template. |
| info       | Print information about a document template.                      |
| new        | Create a new docma template source directory.                     |
| pdf        | Render a document template to PDF.                                |
| pdf-batch  | Render a batch of PDF documents from a single document template.  |

Each sub-command has its own help:

```bash
docma compile --help
```

A typical usage sequence might be:

```bash
# First create the source for the document template in its own directory
docma new my-template

# Add content, configuration etc. Then ...

# Compile
docma compile -i my-template -t my-template.zip

# Render to PDF
docma pdf -t my-template.zip -o my-doc.pdf --file parameters.yaml

# Render to HTML
docma html -t my-template.zip -o my-doc.pdf --file parameters.yaml
```
