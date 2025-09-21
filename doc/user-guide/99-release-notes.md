
# Release Notes

## Version 2

#### Version 2.2.0

*   The Jinja subsystem has been refactored substantially (backward compatible).
    Changes include:

    *   Region specific filters are now named with the 2 character ISO country
        code as a prefix. e.g. [au.ABN](#jinja-filter-auabn) replaces `abn` and
        [au.ACN](#jinja-filter-auacn) replaces `acn`.  Using the old forms will
        still work but produces a deprecation warning.

    *   Adding new generic and region specific filters has been simplified.

    *   Docma templates now support [locales](#locale-in-docma-templates). A
        locale is a string such as `en_AU`, `fr_CA`, etc and can
        influence the behaviour of things such as
        [Jinja filters](#custom-jinja-filters-provided-by-docma).

    *   The names of docma custom Jinja filters, Jinja tests and
        [format checkers](#format-checkers-provided-by-docma) are case insensitive.

*   The following Jinja filters have been added for use in document templates.
    These are all locale / region aware. Credit to the
    [Babel](https://babel.pocoo.org) and
    [phonenumbers](https://pypi.org/project/phonenumbers/) packages for making
    this possible. All of the filters come with sensible defaults. The Babel based
    filters in particular provide a high degree of control over formatting using
    the [Locale Data Markup Language
    specification](https://unicode.org/reports/tr35/tr35-numbers.html#Number_Format_Patterns)
    (LDML) if the defaults don't suit.

    *   [phone](#jinja-filter-phone)  formats international phone numbers.
        
    *   [currency](#jinja-filter-currency) formats international currencies.
        This also provides support for currency specific filters such as `AUD` ,
        `EUR`, `GBP` for a wide range of currencies. The older `dollars` filter
        is still supported but discouraged (not deprecated, as such).

    *   [decimal](#jinja-filter-decimal) and
        [compact_decimal](#jinja-filter-compact_decimal) format numbers using
        locale specific conventions.

    *   [percent](#jinja-filter-decimal) formats percentages using locale
        specific conventions.

    *   [date](#jinja-filter-date), [datetime](#jinja-filter-datetime),
        [time](#jinja-filter-time) and [timedelta](#jinja-filter-timedelta)
        format datetime elements using locale specific conventions.

    *   [parse_date](#jinja-filter-parse_date) and
        [parse_time](#jinja-filter-parse_time) parse dates and times into the
        appropriate Python objects using locale specific conventions.

*   A new suite of [format checkers](#format-checkers-provided-by-docma) has
    been introduced. These serve the dual purpose of being available as `format`
    entries for string objects in JSON Schema specifications as well as custom
    Jinja tests.

*   The following changes have been made to the `docma new` command used to
    create a new document template:

    *   Some basic validation has been added to user input values.

    *   The default `locale` for the template must now be specified.

*   The [docma.format](#jinja-rendering-parameters-provided-by-docma) rendering
    parameter has been added to indicate the type of output document being
    produced, `HTML` or `PDF`.

*   Some minor improvements in error messages for database related errors have
    been made. (Credit MN.)

*   Added the `make count` target to count lines of code, doc, stuff. Why not?

#### Version 2.1.0

This is the open source base release.

Changes from v2.0.0 are:

*   Updated CLI install approach.

*   Incremental increase in test coverage.

*   Editorial changes in the user guide.

*   Docker build switched to buildkit.

*   The size limit on imported documents has been increased from 5MB to 10MB.
