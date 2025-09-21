
## Docma Parameter Validation

Docma supports the use of [JSON Schema](https://json-schema.org) to validate
rendering parameters at run-time. Parameters are validated against a schema
provided in the `parameters->schema` key in the 
[template configuration file](#template-configuration-file) prior to generating
the output document. Failing validation will halt the production process.

> Provision, and hence use, of a parameter validation schema is optional, but
> highly recommended to reduce the risk of generating an important
> document incorrectly or with nonsensical values.

All of the normal facilities of  [JSON Schema](https://json-schema.org) are
available, except for external schema referencing with `$ref` directives. Like
the [JSON Schema built-in string
formats](https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-validation-00#rfc.section.7.3),
docma provided [format checkers](#format-checkers-provided-by-docma) can be used
in a schema specification with the `format` attribute of string objects

The following sample schema fragment shows how these are used:

```yaml
type: object
properties:
  customer_abn:
    type: string
    format: au.ABN
  target_consumption:
    type: number
    minimum: 0
  consumption_unit:
    type: string
    format: energy_unit
  start_date:
    type: string
    format: date.dmy
```

See also [Format Checkers Provided by Docma](#format-checkers-provided-by-docma).
