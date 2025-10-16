## Docma Format Checkers

**Docma** includes an extensible set of format checkers. These can be used in two ways:

1.  In [JSON schema specifications](#format-checkers-in-json-schema)
    as `format` specifiers for `string` data elements; and

2.  As [Jinja tests](#format-checkers-in-jinja) in content that will be
    Jinja rendered.

The **docma** provided format checkers are divided into:

* [Generic checkers](#generic-format-checkers)
* [Region / country specific checkers](#regional-format-checkers).

All **docma** provided format checker names are case insensitive.

It is easy to [add new format checkers](#format-checkers), as required.

### Generic Format Checkers

| Test Name        | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| date.dmy         | Date formatted as day/month/year. The separators can be any of `/-_.` or missing (e.g. `31/12/2024`, `31.12.2024`, `31-12-2024`, `31_12_2024`, `31122024`). |
| date.mdy         | Date formatted as month/day/year. The separators can be any of `/-_.` or missing  (e.g. `12/31/2024`, ...). |
| date.ymd         | Date formatted as year/month/day. The separators can be any of `/-_.` or missing (e.g. `2024/12/31`, ...). |
| DD/MM/YYYY       | *JSON Schema use only*. Deprecated. Use `date.dmy` instead.  |
| energy_unit      | An energy unit (e.g. kWh, MVArh).                            |
| locale           | A locale specifier (e.g. `en_AU`, `fr_FR`)                   |
| power_unit       | A power unit (e.g. kW, MVA).                                 |
| semantic_version | A version in the form `major.minor.patch` (e.g. `1.3.0`).    |

### Regional Format Checkers

| Checker Name | Description         |
| ---------------- | -------------------------- |
| ACN           | Deprecated. Use `au.abn` instead.  |
| ABN           | Deprecated. Use `au.abn` instead.   |
| au.ABN           | Australian Business Number.                                  |
| au.ACN           | Australian Company Number.                                   |
| au.MIRN          | Australian energy industry Gas Meter Installation Registration Number. |
| au.NMI           | Australian energy industry National Metering Identifier. |
| MIRN             | Deprecated. Use `au.MIRN` instead. |
| NMI              | Deprecated. Use au.NMI instead. |

### Format Checkers in JSON Schema

JSON Schema specifications are supported, and strongly recommended, in a number
of **docma** components, such as as the [template configuration
file](#template-configuration-file), and [query
specifications](#query-specifications). They provide run-time type checking of
important data elements and are an important safety mechanism.

Like the [JSON Schema built-in
string formats](https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-validation-00#rfc.section.7.3),
**docma** provided format checkers can be used in a schema specification with the
`format` attribute of string objects, like so:

```yaml
type: object
properies:
  prop1:
    type: string
    # Use a built in format like "email" or one of **docma**'s format checkers
    format: ... 
```

!!! note
    Examples are given in YAML rather than JSON for readability, and because they
    are specified in YAML in **docma**.

For example, consider a document template for a contract that requires
parameters for customer email, contract start date, and customer Australian
Business Number (ABN) to be specified: The relevant portion of the [template
configuration file](#template-configuration-file) might look like this:

```yaml
parameters:
  schema:
    # Schema for the schema!
    $schema: https://json-schema.org/draft/2020-12/schema
    title: Parameters validation schema
    type: object
    required:
      - locale
      - customer_email
      - customer_abn
      - contract_start_date
    properties:
      locale:
        type: string
        format: locale  # This is a docma provided format checker
      customer_email:
        type: string
        format: email  # This is a standard JSON schema format checker
      customer_abn:
        type: string
        format: au.ABN   # This is a docma provided format checker.
      contract_start_date:
        type: string
        format: date.dmy  # This is a docma provided format checker
```

**Docma** will validate values provided at run-time against this schema.

### Format Checkers in Jinja

In addition to the [standard tests provided by
Jinja](https://jinja.palletsprojects.com/en/stable/templates/#list-of-builtin-tests),
the **docma** format checkers can also be used as Jinja tests, like so:

```jinja
{% if contract_date is not date.dmy %}
{% abort 'Bad date' %}
{% endif %}
```

When used as Jinja tests, none of the **docma** format checkers accept an arguments
additional to the value being checked. 

!!! note
    **Docma** can also be extended with Jinja tests that can accept additional
    arguments, but these would not also be used in JSON Schema specifications
    and hence would not be considered to be format checkers.
