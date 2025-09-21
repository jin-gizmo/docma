#### Jinja Filter: dollars

Round and format a currency value as dollars.

Banker's half-up, rounding is used (like Excel) instead of the half-even rounding that is Python's normal default.

> This filter is a legacy that is not actually deprecated (yet), but its use is discouraged. Use the [currency](#jinja-filter-currency) filter in preference.

The filter signature is:

```python
dollars(value: str | int | float, precision: int = 2, symbol: str = '$')
```


| Parameter | Description                                      |
| --------- | ------------------------------------------------ |
| value     | A number or numeric string.                      |
| precision | Number of decimal places to show. Defaults to 2. |
| symbol    | The currency symbol to show. Defaults to `$`.    |

Examples:

```jinja
{{ 1234.50 | dollars }} --> $1,234.50
{{ 1234.50 | dollars(0) }} --> $1,235
```
