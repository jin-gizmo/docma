#### Jinja Filter: timedelta

Format timedelta values.

This is a [locale-aware](#locale-in-docma-templates) filter that provides an
interface to the Babel
[format_timedelta()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.format_timedelta)
API. All of its parameters can be used in the filter to obtain fine-grained control over formatting.

The locale is determined as described in [Locale in Docma
Templates](#locale-in-docma-templates).  It can also be specified explicitly by
adding a `locale` argument to the filter.

The filter signature is:

```python
timedelta(value: datetime.timedelta | datetime.datetime | datetime.time, *args, **kwargs)
```

| Parameter | Description                                                  |
| --------- | ------------------------------------------------------------ |
| value     | Filter input value. This must be a `datetime.timedelta` instance. |
| *args     | Passed to Babel's [format_timedelta()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.format_timedelta). |
| **kwargs  | Passed to Babel's [format_timedelta()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.format_timedelta). This includes the option of using the `locale` parameter to specify locale. |

Examples (assuming locale is set to `en_AU`):

```jinja
{% set d1 = docma.datetime.datetime(2025, 9, 17, 14, 15, 16) %}
{% set d2 = docma.datetime.datetime(2025, 9, 19, 14, 15, 16) %}

{{ (d2 - d1) | timedelta }} --> 2 days (default format is 'long')
{{ (d2 - d1) | timedelta(format='narrow') }} --> 2d
{{ (d2 - d1) | timedelta(add_direction=True) }} --> in 2 days
```

Locale can be specified explicitly, if required:

```jinja
{{ (d2 - d1) | timedelta(locale='uk_UA') }} --> '2 дні'
```

> The Babel [format_timedelta()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.format_timedelta) rounding process is not particularly intuitive on first appearance but makes sense once you get the hang of it. You may need to experiment with `threshold` and `granularity` arguments to get the desired effect.
