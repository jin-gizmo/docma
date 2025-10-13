
## Docma Jinja Filters

!!! note
    Jinja filter management has changed significantly in **docma** 2.2. Some
    filters have been renamed (with backward compatible aliases) and a new, more
    extensible filter plugin system has been implemented.

In addition to the standard filters provided by Jinja, **docma** provides a
number of additions. These are divided into:

* [Generic filters](#generic-filters)
* [Region / country specific filters](#regional-filters).

!!! info
    Custom filter names are not case sensitive.

### Generic Filters

Filters marked with * are locale aware.

| Filter Name                    | Description                                 |
|--------------------------------| -------------------------------------------------- |
| [compact_decimal](#jinja-filter-compact_decimal) * | Format a number in a compact format. |
| [css_id](#jinja-filter-css_id) | Sanitise a string to be a valid CSS identifier.    |
| [currency](#jinja-filter-currency) * | Format currency. |
| [date](#jinja-filter-date) * | Format a date. |
| [datetime](#jinja-filter-datetime) * | Format a datetime. |
| [decimal](#jinja-filter-decimal) * | Format a number. |
| [dollars](#jinja-filter-dollars) | Legacy. Format currency a value as dollars. |
| [parse_date](#jinja-filter-parse_date) * | Parse a date string into a [datetime.date](https://docs.python.org/3/library/datetime.html#datetime.date) instance. |
| [parse_time](#jinja-filter-parse_time) * | Parse a date string into a [datetime.time](https://docs.python.org/3/library/datetime.html#datetime.time) instance. |
| [percent](#jinja-filter-percent) * | Format a percentage. |
| [phone](#jinja-filter-phone) * | Format a phone number. |
| [require](#jinja-filter-require) | Abort with an error message an expression does not have a truthy value. |
| [sql\_safe](#jinja-filter-sql_safe) | Ensure that a string value is safe to use in SQL and generate an error if not. |
| [time](#jinja-filter-time) * | Format a time value. |
| [timedelta](#jinja-filter-timedelta) * | Format a timedelta value. |

### Regional Filters

| Filter Name  | Description                                      |
| ------------ | -------------------------------------------------- |
| abn | Deprecated. Use [au.abn](#jinja-filter-auabn). |
| acn | Deprecated. Use [au.abn](#jinja-filter-auacn). |
| [au.abn](#jinja-filter-auabn) | Format an Australian Business Number (ABN). |
| [au.acn](#jinja-filter-auacn) | Format an Australian Company Number (ACN). |

