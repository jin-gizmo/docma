
## Batch Rendering

Docma supports the ability to generate a batch of output documents from a single
document template using the `pdf-batch` (PDF) and `html-batch` (HTML) sub-commands
of the [docma CLI](#the-docma-cli).

The document template needs to anticipate the need for batch rendering by
including some Jinja controlled content that will be varied for each document
produced via document specific parameters. The source for the document specific
batch parameters is a [docma data loader](#data-sources-in-docma). Data returned
by the data loader is merged in with the fixed rendering parameters, a row at a
time, and docma produces an output document using that combination. The source
data for the batch parameters is specified using a [docma data source
specification](#data-source-specifications).

> The following describes the process for PDF document batches. The process is
> similar for HTML batches.


![](img/render-batch.svg)

This is how a batch rendering is invoked:

```bash
# Long form arguments
docma pdf-batch --template my-template.zip \
    --file static-params.yaml \
    --data-source-spec 'postgres;pglocal;queries/batch.yaml' \
    --output 'whatever-{{id}}-{{familyname|lower}}.pdf'

# Short form arguments
docma pdf-batch -t my-template.zip \
    -f static-params.yaml \
    -d 'postgres;pglocal;queries/batch.yaml' \
    -o 'whatever-{{id}}-{{familyname|lower}}.pdf'
```

Let's examine this bit by bit.

The docma `pdf-batch` sub-command is invoked specifying the compiled document
template:

```bash
docma pdf-batch --template my-template.zip
```

Rendering parameters are specified exactly as for the single document rendering
process. These parameters are the same for every document in the rendering batch:

```bash
    --file static-params.yaml \
```

The [docma data source specification](#data-source-specifications) tells docma
how to obtain rows of data to control the batch rendering. Each row is a set of
key/value pairs that will be merged into the static rendering parameters and
used to render one PDF document:

```bash
    --data-source-spec 'postgres;pglocal;queries/batch.yaml' \
```

> The [docma data source specification](#data-source-specifications)
> is interpreted within the context of the document template.

As docma will be producing a series of PDF documents, it needs a mechanism to
provide each document with a unique name that corresponds to the batch data
entry that was used to produce it. This is done using the `--output` option with
an argument that is Jinja rendered to construct the filename. In this example,
it is assumed that the batch data contains `id` and `familyname` elements and
that these are a unique combination to avoid filename clashes:

```bash
    --output 'whatever-{{id}}-{{familyname|lower}}.pdf'
```

> There are some strict constraints on the filename rendering process for safety
reasons.

