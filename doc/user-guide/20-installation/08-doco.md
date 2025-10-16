
## Building the Documentation

**Docma** comes with this user guide and auto-generated API documentation.

To build the documentation:

```bash
make doc
```

The generated documentation is placed in the `dist/doc` directory.

To see the documentation locally:

```bash
make serve
```

This uses mkdocs to run a local server on `http://127.0.0.1:8000/`.

If editing the documentation, ensure that a spell check is done as part of the
process using:

```bash
make spell
```

This requires the `aspell` tool. For macOS:

```bash
brew install aspell
```
