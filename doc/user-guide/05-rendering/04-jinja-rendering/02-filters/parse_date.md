#### Jinja Filter: parse_date

Parse a date string into a [datetime.date](https://docs.python.org/3/library/datetime.html#datetime.date) instance.

This is a [locale-aware](#locale-in-docma-templates) filter that provides an
interface to the Babel
[parse_date()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.parse_date)
API.

The filter signature is:

```python
parse_date(value: str, *args, **kwargs) -> datetime.date
```

| Parameter | Description                                                  |
| --------- | ------------------------------------------------------------ |
| value     | Filter input value. The parser understands component ordering variations by locale but cannot handle month names. Numbers only. |
| *args     | Passed to Babel's [parse_date()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.parse_date). |
| **kwargs  | Passed to Babel's [parse_date()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.parse_date). This includes the option of using the `locale` parameter to specify locale. |

Examples (assuming locale is set to `en_AU`):

```jinja
{{ '1/9/2025' | parse_date) }} --> datetime.date(2025, 9, 1)
```

Locale can be specified explicitly, if required:

```jinja
{{ '1/9/2025' | parse_date(locale='en_US') }} --> datetime.date(2025, 1, 9)
```
