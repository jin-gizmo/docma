#### Jinja Filter: parse_time

Parse a date string into a [datetime.time](https://docs.python.org/3/library/datetime.html#datetime.time) instance.

This is a [locale-aware](#locale-in-docma-templates) filter that provides an
interface to the Babel
[parse_time()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.parse_time)
API.

!!! info "Filter Signature"

    ```python
    parse_time(value: str, *args, **kwargs) -> datetime.time
    ```

| Parameter | Description                                                  |
| --------- | ------------------------------------------------------------ |
| value     | Filter input value.                                          |
| *args     | Passed to Babel's [parse_time()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.parse_time). |
| **kwargs  | Passed to Babel's [parse_time()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.parse_time). This includes the option of using the `locale` parameter to specify locale. |

!!! example "Examples"

    Assuming locale is set to `en_AU`:

    ```jinja
    {{ '2:15 pm' | parse_time) }} --> datetime.time(14, 15)
    ```

    Locale can be specified explicitly, if required:

    ```jinja
    {{ '1/9/2025' | parse_date(locale='en_US') }} --> datetime.date(2025, 1, 9)
    ```
