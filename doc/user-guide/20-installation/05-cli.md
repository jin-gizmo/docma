
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
| completion | Generate the command line completion script. See [Command Line Completion](#command-line-completion).|
| html       | Render a document template to PDF.                                |
| html-batch | Render a batch of HTML documents from a single document template. |
| info       | Print information about a document template.                      |
| new        | Create a new **docma** template source directory.                 |
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

### Command Line Completion

!!! note
    New in v8.3.0.

The **docma** CLI can produce command completion scripts for the most common
shells (typically **zsh** or **bash**).

```bash
# Produce the command completion script for zsh
docma completion --shell zsh

# ... and for bash ...
docma completion --shell bash
```

Place the resulting script wherever it needs to go in your environment.
For **zsh** with **oh-my-zsh**, this would typically be something
like `~/.oh-my-zsh/completions/_docma`.

!!! info
    You will probably need to restart your shell after creating the completion
    script.

!!! tip
    The bash completion shell will not work on the 20 year old version of
    **bash** that ships on macOS. Honestly, just switch to **zsh** which is now
    the default shell on macOS anyway.
