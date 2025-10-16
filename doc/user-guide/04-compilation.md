
# Docma Template Compilation [nav: Template Compilation]

The compilation process is a build-time activity consisting of the following steps:

1.  Validate the template [configuration file](#template-configuration-file).

2.  Copy files from the template source to the template staging area,
    compiling any compilable files (e.g Markdown) to HTML in the process.

3.  Import any files specified in the `imports` key of the
    [configuration file](#template-configuration-file), compile as required and
    copy them to the template staging area.

4.  Zip up the contents of the template staging area to produce the compiled
    document template.

!!! note
    The **docma** CLI also supports the option of saving the compiled template,
    uncompressed, into a local directory. This is primarily for development and
    testing.

![](img/compile-phase.svg)

There is (approximately) a one-to-one correspondence between files
in the source directory and the compiled template. Directory structure is
preserved.
