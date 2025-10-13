
# Extending Docma

**Docma** has a number of plugable interfaces to allow extension. The process
works by placing a Python file in the appropriate directory in the code base,
unless otherwise indicated. These are automatically discovered as required.

## Content Importers

Content importers operate during the docma [compile](#docma-template-compilation)
phase. They collect components from external sources and inject them into the
compilation process.

Imported components are referenced via a URL `scheme://....`. The `scheme` is
used to select the importer to be used.

To create a new importer, add a new Python file into `docma/importers`. It will
be auto-discovered.

See the [API reference][docma.importers] for details.

## Content Compilers

Content compilers operate during the docma [compile](#docma-template-compilation)
phase. They transform a source format into HTML. The source format is determined
by the filename suffix.

To create a new compiler, add a new Python file into `docma/compilers`. It will
be auto-discovered.

See the [API reference][docma.compilers] for details.

## URL Fetchers

[URL fetchers](#dynamic-content-generation) operate during the docma
[render](#docma-template-rendering) phase. They provide WeasyPrint with the
means to resolve URLs within the HTML being converted to PDF. They are also used
when producing HTML output documents to populate the data for `IMG` tags.

URL fetchers are selected based on the scheme of the URL.

To create a new URL fetcher, add a new Python file into `docma/url_fetchers`.
It will be auto-discovered.

See the [API reference][docma.url_fetchers] for details.

## Content Generators

[Content generators](#dynamic-content-generation) operate during the docma
[render](#docma-template-rendering) phase. They dynamically generate content for
WeasyPrint when a URL in the following form is accessed.

```bare
docma:<generator-name>?<generator-params>
```

They are typically used for generating image content
(charts, QR codes etc.) but they can be used wherever URLs return content to
WeasyPrint.

To create a new content generator, add a new Python file into
`docma/generators`.  It will be auto-discovered. Start by copying the sample
`swatch.py` generator and modifying as required.

See the [API reference][docma.generators] for details.

## Data Providers

[Data providers](#data-sources-in-docma) operate during the docma
[render](#docma-template-rendering) phase.

The data provider handler is selected by the `type` component of a
[data source specification](#data-source-specifications).

To create a new data provider, add a new Python file into
`docma/data_providers`. It will be auto-discovered.  Start by copying one of
the existing providers and modify as needed.

See the [API reference][docma.data_providers] for details.

## Format Checkers

Docma has a number of custom [format
checkers](#docma-format-checkers) that serve a dual role as JSON
Schema string formats and custom Jinja tests. These are implemented using a
simple plugin mechanism. Read the docstring at the top of `docma/lib/plugin.py`
before launching into it.

To create a new format checker, add a new Python file into
`docma/plugins/format_checkers`.  Start by copying one of the existing checkers.

Checkers can be grouped together in families (e.g. the `au.*` suite) using
nested Python packages (directories containing `__init__.py`). The discovery and
loading process is automatic.

Each checker is basically a decorated function with a single parameter,
being the string value to be checked, and must return a boolean indicating
whether it conforms to the required format, or not.

It is also possible to have checkers with names generated dynamically at
run-time. Tricky. Don't start here on day one but check out the
`DateFormatResolver` class in `docma/jinja/resolvers.py` if the fever is upon
you.

!!! info
    Resolvers are *not* automatically discovered.

## Custom Jinja Filters

Docma has a number of custom Jinja
[filters](#docma-jinja-filters). These are implemented using
a simple plugin mechanism. Read the docstring at the top of
`docma/lib/plugin.py`  before launching into it.

To create a new format checker, add a new Python file into
`docma/plugins/jinja_filters`.  Start by copying one of the existing filters.

Checkers can be grouped together in families (e.g. the `au.*` suite) using
nested Python packages (directories containing `__init__.py`). The discovery and
loading process is automatic.

It is also possible to have filters with names generated dynamically at
run-time. For example, the [currency filters](#jinja-filter-currency) work this
way. Tricky. Don't start here on day one but check out the
`CurrencyFilterResolver` class in `docma/jinja/resolvers.py` if inspiration
strikes.

!!! info
    Resolvers are *not* automatically discovered.

## Custom Jinja Tests

Docma does not currently provide any custom Jinja tests, other than custom
[format checkers](#docma-format-checkers) which are kept separate
because they server both Jinja and JSON Schema.

Unlike custom [format checkers](#docma-format-checkers), custom
tests can be written to accept arguments additional to the value being tested.

All of the scaffolding required to add custom Jinja tests is present. The
mechanism is the same as used for adding [custom jinja
filters](#custom-jinja-filters) except that the required decorator is
`@jtest` instead of `@jfilter` and they should be placed in
`docma/plugins/jinja_tests` instead of `docma/plugins/jinja_filters`. The
discovery and loading process is automatic.

## Custom Jinja Extensions

Docma has a number of custom Jinja
[extensions](#docma-jinja-extensions). These are all
contained in the file `docma/jinja/extensions.py`. New ones can be added to this
file but if you think you need to, think again.

