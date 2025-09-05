
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
available, except for external schema referencing with `$ref` directives.

### Custom JSON Schema Formats Provided by Docma

In addition to the standard format specifiers supported by JSON Schema, docma
also provides the following.

| Format            | Description                                               |
|-------------------|-----------------------------------------------------------|
| ABN               | Australian Business Number.                               |
| ACN               | Australian Company Number.                                |
| DD/MM/YYYY        | Date formatted as day/month/year (e.g. `31/12/2024`).     |
| MIRN              | Gas Meter Installation Registration Number.               |
| NMI               | National Metering Identifier.                             |
| energy\_unit      | An energy unit (e.g. kWh, MVArh).                         |
| power\_unit       | A power unit (e.g. kW, MVA).                              |
| semantic\_version | A version in the form `major.minor.patch` (e.g. `1.3.0`). |

> These are format / syntax checks only. For example, the `ABN` format
> check will confirm the value is correctly constructed (including valid checksum)
> but will not do a look-up to confirm it applies to any particular entity.

The following sample schema fragment shows how these are used:

```yaml
properties:
  customer_abn:
    type: string
    format: ABN
  target_consumption:
    type: number
    minimum: 0
  consumption_unit:
    type: string
    format: energy_unit
  start_date:
    type: string
    format: DD/MM/YYYY
```

> It is straightforward to add new format checkers.
> See [JSON Schema Format Checkers](#json-schema-format-checkers).
