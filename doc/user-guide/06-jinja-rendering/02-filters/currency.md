#### Jinja Filter: currency

Format a currency value.

This is a [locale-aware](#locale-in-docma-templates) filter that provides an
interface to the Babel
[format_currency()](https://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_currency)
API.

It is important to understand that there are two orthogonal aspects to formatting
currency values:

1.  The currency involved, such as Australian dollars (AUD), Euros (EUR) etc.

2.  The locale in which the currency is to be presented.

For example:

*   One Australian dollar would appear in Australia as `$1.00`.
*   One Australian dollar would appear in the US as `A$1.00`
*   One Australian dollar would appear in France as `1,00 AU$`

For the **docma** filter, the currency (AUD in the example above) can be
specified in one of two ways:

1.  By providing an argument to the currency filter `{{ 1 | currency('AUD') }}`;
    or
2.  Using the currency name itself as an alias for the filter name
    `{{ 1 | AUD }}`. **Docma** dynamically generates a filter alias for known
    currencies. Case is not significant.

The locale is determined as described in [Locale in Docma
Templates](#locale-in-docma-templates).  It can also be specified explicitly by
adding a `locale` argument to the filter.

!!! info "Filter Signature"

    ```python
    currency(
        value: str | int | float,
        currency: str,
        *args,
        rounding: str = 'half-up',
        default: int | float | str | None = None,
        **kwargs
    ) -> str
    ```

    ... or .... 

    ```python

    <CURRENCY_CODE>(
        value: str | int | float,
        *args,
        rounding: str = 'half-up',
        default: int | float | str | None = None,
        **kwargs
    ) -> str
    ```

    Here `<CURRENCY_CODE>` can be `AUD`, `GBP`, `EUR` etc.

| Parameter | Description                                                  |
| --------- | ------------------------------------------------------------ |
| value     | Filter input value. Numbers and strings containing numbers are accepted. Jinja will inject this automatically. |
| currency  | The currency code (e.g `AUD`, `EUR` etc.)                    |
| *args     | Passed to Babel's [format_currency()](https://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_currency). |
| rounding  | How to round the value. This must be one of the rounding modes in Babel's `decimal.ROUND_*`, with the `ROUND_` prefix removed. Case is ignored and hyphens become underscores. Defaults to `half-up` (Excel style rounding), instead of `half-even` (Bankers rounding) which is Python's normal default. |
| default   | The default value to use for the filter if the input value is empty (i.e. None or an empty string but not zero). If the input value is empty and `default` is a string, it is used as-is as the return value of the filter. If the input value is empty, and `default` is not specified, an error is raised. Otherwise, the default is assumed to be numeric and is used as the input to the filter. **Note:** The `default` parameter does something different to the Jinja standard [default](https://jinja.palletsprojects.com/en/stable/templates/#jinja-filters.default) filter. They are both useful but not interchangeable. |
| **kwargs  | Passed to Babel's [format_decimal()](https://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_decimal). This includes the option of using the `locale` parameter to specify locale. |

!!! example "Examples"

    Assuming locale is set to `en_AU`:

    ```jinja
    {{ 123 | AUD }} --> $123.00
    {{ 123 | currency('AUD') }} --> $123.00
    {{ '123' | NZD }} --> NZD123.00 (numeric strings are fine as input)
    {{ None | AUD }} --> ERROR!
    {{ None | AUD(default=0) }} --> $0.00
    {{ None | AUD(default='FREE!')}} --> FREE!
    {{ -123 | AUD(format="¤#,###;(¤#)", currency_digits=False)}} --> ($123)
    ```

    Locale can be specified explicitly, if required:

    ```jinja
    {{ 123 | EUR(locale='en_GB') }} --> €123.00
    {{ 123 | EUR(locale='fr_FR' }} --> 123,00 €
    ```

    The legacy [dollars](#jinja-filter-dollars) filter can be replicated like so
    (use whatever dollar currency is appropriate):

    ```jinja
    {{ 1234.5 | dollars }} --> {{ 1234.5 | AUD }} --> $1,234.50
    {{ 1234.5 | dollars(0) }} --> {{ AUD(format="¤#,###", currency_digits=False) }} --> $1,235
    ```

