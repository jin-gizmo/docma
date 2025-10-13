
## Creating a New Document Template

To create a new docma template directory:

```bash
docma new <DIRECTORY>
```

This will prompt the user to enter a small number of configuration parameters.
They are *all* mandatory. Do not leave anything blank.

The specified directory will now contain a very simple, but complete, document
template source directory that can be compiled and rendered:

```bash
docma compile -i <DIRECTORY> -t my-template.zip
docma pdf -t my-template.zip -o my-doc.pdf
```
