#### Jinja Filter: datetime

Format datetime values.

This is a [locale-aware](#locale-in-docma-templates) filter that provides an
interface to the Babel
[format_datetime()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.format_datetime)
API. All of its parameters can be used in the filter to obtain fine-grained
control over formatting.

The locale is determined as described in [Locale in Docma
Templates](#locale-in-docma-templates).  It can also be specified explicitly by
adding a `locale` argument to the filter.

The filter signature is:

!!! info "Filter Signature"

    ```python
    datetime(value: datetime.date | datetime.datetime | datetime.time, *args, **kwargs) -> str
    ```

| Parameter | Description                                                  |
| --------- | ------------------------------------------------------------ |
| value     | Filter input value. Typically, this would be a `datetime.datetime` instance. While `datetime.date` and `datetime.time` instances are also accepted, they are unlikely to be particularly useful. |
| *args     | Passed to Babel's [format_datetime()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.format_datetime). |
| **kwargs  | Passed to Babel's [format_datetime()](https://babel.pocoo.org/en/latest/api/dates.html#babel.dates.format_datetime). This includes the option of using the `locale` parameter to specify locale. |

!!! example "Examples"

    Assuming locale is set to `en_AU`:

    ```jinja
    {% set value = docma.datetime.datetime(2025, 9, 17, 14, 15, 16) %}

    {{ value | datetime }} --> 17 Sept 2025, 2:15:16 pm
    ```

    Locale can be specified explicitly, if required:

    ```jinja
    {{ value | datetime(locale='en_US') }} --> Sep 17, 2025, 2:15:16 PM
    ```

If datetime strings need to be handled, they will need to be converted to a
Python
[datetime.datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime)
instance first. For datetime strings guaranteed to be in ISO 8601 format,
Python's standard `datetime.datetime.fromisoformat()` is fine.

!!! example
    ```jinja
    {{ docma.datetime.datetime.fromisoformat('2025-09-17T14:15:16') | datetime }}
    ```

!!! tip
    Avoid using the Python standard `datetime.datetime strptime()` if at all
    possible. This will use the platform locale and cannot handle the **docma**
    locale. The results can be very unpredictable.
