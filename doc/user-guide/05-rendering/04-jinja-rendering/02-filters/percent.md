#### Jinja Filter: percent

Format percentage values.

This is a [locale-aware](#locale-in-docma-templates) filter that provides an
interface to the Babel
[format_percent()](https://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_percent)
API. All of its parameters can be used in the filter to obtain fine-grained
control over formatting.

The locale is determined as described in [Locale in Docma
Templates](#locale-in-docma-templates).  It can also be specified explicitly by
adding a `locale` argument to the filter.

The filter signature is:

```python
percent(
    value: str | int | float,
    *args,
    rounding: str = 'half-up',
    default: int | float | str | None = None,
    **kwargs
)
```

| Parameter | Description                                                  |
| --------- | ------------------------------------------------------------ |
| value     | Filter input value. Numbers and strings containing numbers are accepted. |
| *args     | Passed to Babel's [format_percent()](https://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_percent). |
| rounding  | How to round the value. This must be one of the rounding modes in Babel's `decimal.ROUND_*`, with the `ROUND_` prefix removed. Case is ignored and hyphens become underscores. Defaults to `half-up` (Excel style rounding), instead of `half-even` (Bankers rounding) which is Python's normal default. |
| default   | The default value to use for the filter if the input value is empty (i.e. None or an empty string). If the input value is empty and `default` is a string, it is used as-is as the return value of the filter. If the input value is empty, and `default` is not specified, an error is raised. Otherwise, the default is assumed to be numeric and is used as the input to the filter. **Note:** The `default` parameter described does something different to the Jinja standard `default` filter. They are both useful but not interchangeable. |
| **kwargs  | Passed to Babel's [format_percent()](https://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_percent). This includes the option of using the `locale` parameter to specify locale. |

Examples (assuming locale is set to `en_AU`):

```jinja
{{ 0.1234 | percent }} --> 12%
{{ '0.1234' | percent }} --> 12%
{{ None | percent }} --> ERROR!
{{ None | percent(default=0) }} --> %0
{{ None | percent(default='--')}} --> --
```

Locale can be specified explicitly, if required:

```jinja
{{ '0.123' | percent(locale='fr_FR') }} --> 12 %
```
