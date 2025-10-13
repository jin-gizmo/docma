#### Jinja Filter: time

Format time values.

This is a [locale-aware](#locale-in-docma-templates) filter that provides an
interface to the Babel
[format_time()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.format_time)
API. All of its parameters can be used in the filter to obtain fine-grained
control over formatting.

The locale is determined as described in [Locale in Docma
Templates](#locale-in-docma-templates).  It can also be specified explicitly by
adding a `locale` argument to the filter.

!!! info "Filter Signature"

    ```python
    time(value: datetime.time | datetime.datetime, *args, **kwargs) -> str
    ```

| Parameter | Description                                                  |
| --------- | ------------------------------------------------------------ |
| value     | Filter input value. This must be a `datetime.time` or `datetime.datetime` instance. |
| *args     | Passed to Babel's [format_time()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.format_time). |
| **kwargs  | Passed to Babel's [format_time()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.format_time). This includes the option of using the `locale` parameter to specify locale. |

!!! example "Examples"

    Assuming locale is set to `en_AU`:

    ```jinja
    {% set value = docma.datetime.time(14, 15) %}

    {{ value | time }} --> 2:15:00 pm
    ```

    Locale can be specified explicitly, if required:

    ```jinja
    {{ value | datetime(locale='de_DE') }} --> 14:15:00
    ```

    If time strings need to be handled, they will need to be converted to a Python
    [datetime.time](https://docs.python.org/3/library/datetime.html#datetime.time)
    instance first. The safest way to do this is to use the
    [parse_time](#jinja-filter-parse_time) filter as this is **docma** locale aware.

    ```jinja
    {{ '14:15' | parse_time | time }} --> 2:15:00 pm
    {{ '2:15 pm' | parse_time | time }} --> 2:15:00 pm
    ```
