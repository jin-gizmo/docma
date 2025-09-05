
# Document Templates

The source directory for a document template should be created using the docma
CLI:

```bash
docma new <DIRECTORY>
```

The resulting directory is structured thus:

```bare
<DIRECTORY>/
├── config.yaml    ... Mandatory
├── charts/        ... Specification files for charts
├── content/       ... Document content (HTML, PDF, Markdown etc.)
├── data/          ... Data files (e.g CSV / JSONL files)
├── fonts/         ... Font files (e.g. .ttf files)
├── overlays/      ... Overlay content files (Typically HTML or PDF)
├── queries/       ... Query specifications used for charts
└── resources/     ... HTML resources (image files etc.)
```

Only the `config.yaml` file is mandated. While the other components can be
present, or not, as required, and directory structure is arbitrary, it is
**strongly** recommended to adhere to the layout shown above.

> Files and directories in the template source directory matching `.*` are not
> copied into the compiled template.
