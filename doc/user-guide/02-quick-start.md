# Quick Start

Before launching into the details of **docma**, let's get started with a simple
document template.

## Setup

The easiest method is to use the **docma** docker image, but getting started on
macOS is straightforward enough provided you have Python3.11+ and
[Homebrew](https://brew.sh) installed.

=== "macOS"
    Assuming we have Python3.11+ and [Homebrew](https://brew.sh) installed:

    ```bash
    brew install gtk+

    # Create a sandbox
    mkdir docma-quick-start
    cd docma-quick-start

    # Create a virtual environment for cleanliness
    python3 -m venv venv
    source venv/bin/activate

    # Install docma
    pip install docma
    ```

=== "Docker"
    ```bash
    # Create a sandbox
    mkdir docma-quick-start
    cd docma-quick-start

    # Get the docma docker image (ARM64 and AMD64/X86_64 versions are available)
    docker pull jingizmo/docma
    
    # Save ourselves some typing later on ...
    alias docma='docker run -it --rm -v $(pwd):/docma jingizmo/docma'
    ```

    !!! warning
        Make sure you get the image name correct ... `jingizmo/docma` *not* `docma`.

=== "Linux"
    Installation of the prerequisites on Linux can vary depending on the distro
    being used. See [Installation and Usage](#installation-and-usage) for more
    information.

    ```bash
    # Create a sandbox
    mkdir docma-quick-start
    cd docma-quick-start

    # Create a virtual environment for cleanliness
    python3 -m venv venv
    source venv/bin/activate

    # Install docma
    pip install docma
    ```

## Step 1 -- Create a Template

```bash
docma new demo
```

This will ask a few configuration questions and then create a new
[docma document template](#document-templates). The only questions that will
require an answer are `description` and `owner`. The defaults are fine for the
other questions.

You should now have a directory (`demo`) containing a fully functioning **docma**
template that we can compile and render. Explore it.

## Step 2 -- Compile the Template

```bash
docma compile --input demo --template docma.d
# ... or ...
docma compile -i demo -t docma.d
```

In this example, the template has been compiled into another directory, `docma.d`.
In production use, it would be compiled into a zip file instead:

```bash
docma compile --input demo --template docma.zip
```

The template is ready for rendering into either PDF or HTML output.

## Step 3 -- Render the Template

```bash
# Render to PDF
docma pdf --template demo.d --output demo.pdf

# Render to HTML
docma html --template demo.d --output demo.html
```

## Now What?

Feel free to explore and play with the contents of the template. Start with
these files:

*   `content/sample.html`: This is the main content. Vanilla HTML.
*   `config.yaml`: The [template configuration file](#template-configuration-file).
