#### Jinja Filter: date

Format date values.

This is a [locale-aware](#locale-in-docma-templates) filter that provides an
interface to the Babel
[format_date()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.format_date)
API. All of its parameters can be used in the filter to obtain fine-grained
control over formatting.

The locale is determined as described in [Locale in Docma
Templates](#locale-in-docma-templates).  It can also be specified explicitly by
adding a `locale` argument to the filter.

The filter signature is:

```python
date(value: datetime.date | datetime.datetime, *args, **kwargs)
```

| Parameter | Description                                                  |
| --------- | ------------------------------------------------------------ |
| value     | Filter input value. This must be a `datetime.date` or `datetime.datetime` instance. |
| *args     | Passed to Babel's [format_date()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.format_date). |
| **kwargs  | Passed to Babel's [format_date()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.format_date). This includes the option of using the `locale` parameter to specify locale. |

Examples (assuming locale is set to `en_AU`):

```jinja
{% set value = docma.datetime.date(2025, 9, 17) %}

{{ value | date }} --> 17 Sept 2025 (medium format is the default)
{{ value | date(format='short') }} --> 17/9/25
{{ value | date(format='long') }} --> 17 September 2025
{{ value | date(format='full') }} --> Wednesday, 17 September 2025
{{ value | date(format='dd/MM/yyyy')}} --> 17/09/2025
```

Locale can be specified explicitly, if required:

```jinja
{{ value | datetime(locale='en_US') }} --> Sep 17, 2025
```

If date strings need to be handled, they will need to be converted to a Python
[datetime.date](https://docs.python.org/3/library/datetime.html#datetime.date) instance
first. For date strings guaranteed to be in ISO 8601 format, Python's standard
`datetime.date.fromisoformat()` is fine. Otherwise, the safest way to do this
for dates containing only numbers (no month names) is to use the
[parse_date](#jinja-filter-parse_date) filter as this is (docma) locale aware,
unlike the Python standard datetime.datetime.strptime().

```jinja
{{ docma.datetime.date.fromisoformat('2025-09-1') | date }} --> 1 Sept 2025
{{ '1/9/2025' | parse_date | date }} --> 1 Sept 2025
{{ '1/9/2025' | parse_date(locale='en_US') | date }} --> 9 Jan 2025
```

> **Here be dragons:** There is no fully reliable way to parse dates containing
> month names in a generic, locale-aware away. Don't be tempted to attempt this
> in a docma template. If you think you need to, you are either solving the problem the wrong way or solving the wrong
> problem.
