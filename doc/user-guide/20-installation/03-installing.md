
## Installing Docma

### Installing with Pip

Basic install:

```bash
pip install docma
```

This will
install the base **docma** Python package and the **docma** CLI. This will not
install support for [duckdb](#data-provider-type-duckdb) or
[lava](#data-provider-type-lava) data providers.

To install support for the [duckdb](#data-provider-type-duckdb) data provider:

```bash
pip install 'docma[duckdb]'
```

To install support for the [lava](#data-provider-type-lava) data provider:

```bash
pip install 'docma[lava]'
```

### Installing from the Repo

Clone the [**docma** repo](https://github.com/jin-gizmo/docma).

The rest of the setup is handled by the Makefile.

```bash
# Create venv and install the required Python packages
make init
# Activate the virtual environment
source venv/bin/activate
```

To run the **docma** CLI directly from the repo:

```bash
python3 -m docma.cli.docma --help
```

To build **docma**, use the Makefile.

```bash
# See what we can build ...
make
# ... or ....
make help
```

To build an install bundle:

```bash
make pkg
```
