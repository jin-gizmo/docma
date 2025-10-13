
# Installation and Usage

## TL;DR

First install the [prerequisites](#prerequisites) then ...

```bash
pip install docma

# Optionally, add duckdb and lava support
pip install 'docma[duckdb]'
pip install 'docma[lava]'

# Check docma installed ok
docma --help

# Create our first docma template. This is a working basic template.
docma new my-template

# Compile it
docma compile -i my-template -t my-template.zip

# Render it to PDF.
docma pdf -t my-template.zip -o my-doc.pdf
```
