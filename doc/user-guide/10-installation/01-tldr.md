
# Installation and Usage

## TL;DR

> **Docma** is not yet available in PyPI, sorry. Coming soon. For now, it will
> need to be [installed from the repo](#installing-from-the-repo).

First install the [prerequisites](#prerequisites) then ...

```bash
python3 -m pip install docma

# Optionally, add duckdb and lava support
python3 -m pip install 'docma[duckdb]'
python3 -m pip install 'docma[lava]'

# Check docma installed ok
docma --help

# Create our first docma template. This is a working basic template.
docma new my-template

# Compile it
docma compile -i my-template -t my-template.zip

# Render it to PDF.
docma pdf -t my-template.zip -o my-doc.pdf
```
