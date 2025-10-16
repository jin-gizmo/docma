
## Docma Parameter Validation

**Docma** supports the use of [JSON Schema](https://json-schema.org) to validate
rendering parameters at run-time. Parameters are validated against a schema
provided in the `parameters->schema` key in the 
[template configuration file](#template-configuration-file) prior to generating
the output document. Failing validation will halt the production process.

!!! tip
    Provision, and hence use, of a parameter validation schema is optional, but
    highly recommended to reduce the risk of generating an important
    document incorrectly or with nonsensical values.

All of the normal facilities of  [JSON Schema](https://json-schema.org) are
available, except for external schema referencing with `$ref` directives. Like
the [JSON Schema built-in string
formats](https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-validation-00#rfc.section.7.3),
**docma** provided [format checkers](#docma-format-checkers) can be used
in a schema specification with the `format` attribute of string objects

The following sample schema fragment shows how these are used:

```yaml
type: object
properties:
  customer_email:
    type: string
    format: email  # This is a JSON schema built-in format checker
  customer_abn:
    type: string
    format: au.ABN  # This is a docma provided format checker
  target_consumption:
    type: number
    minimum: 0
  consumption_unit:
    type: string
    format: energy_unit  # This is a docma provided format checker
  start_date:
    type: string
    format: date.dmy  # This is a docma provided format checker
```

See also [Docma Format Checkers](#docma-format-checkers).
