

## Prerequisites

### General

Python3.11+ is required.

### Mac

On Mac OS, GTK is required for the HTML to PDF process.

```bash
brew install gtk+
```

If [DuckDB](https://duckdb.org) data sources are used, install the DuckDB CLI.

```bash
brew install duckdb
```

### Linux

On Linux, [Pango](https://www.gtk.org/docs/architecture/pango) is required for
the HTML to PDF process.

If [DuckDB](https://duckdb.org) data sources are used,
[install the DuckDB CLI](https://duckdb.org/docs/installation/?version=stable&environment=cli&platform=linux&download_method=package_manager).
The Python API will be installed automatically when docma is installed.

To build the user guide, [Pandoc](https://pandoc.org) is required. Follow the
[Pandoc installation instructions](https://pandoc.org/installing.html).

### DOS

**Docma** might work on DOS. How would I know? Why would I care?

I guess you could try WSL 2. If you do, please let us know. 
