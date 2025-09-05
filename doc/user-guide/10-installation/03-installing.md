
## Installing Docma

### Installing from the Repo

Clone the docma repo.

The rest of the setup is handled by the Makefile.

```bash
# Create venv and install the required Python packages
make init
```

To run the **docma** CLI directly from the repo clone, `PYTHONPATH` will need to
include the directory repo. e.g.

```bash
python3 -m docma.cli.docma --help
```

To build docma, use the Makefile.

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

### Installing with Pip

**Docma** is not yet available in PyPI, sorry. Coming soon.

In the meantime, grab a distribution bundle created from the repo using `make
pkg` and then ...

```bash
pip install docma-<VERSION>.tar.gz
```

This will
install the base **docma** Python package and the docma CLI. This will not
install support for [duckdb](#data-provider-type-duckdb) or
[lava](#data-provider-type-lava) data providers.

To install support for the [duckdb](#data-provider-type-duckdb) data provider:

```bash
pip3 install 'docma-<VERSION>.tar.gz[duckdb]'
```

To install support for the [lava](#data-provider-type-lava) data provider:

```bash
pip3 install 'docma-<VERSION>.tar.gz[lava]'
```
