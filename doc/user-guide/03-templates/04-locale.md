## Locale in Docma Templates

Prior to version 2.2.0, docma had no particular notion of the region or locale
with which a particular template, or the documents it produces, is associated.
If special formatting was required, it was up to the template designer to handle
that manually.

This applied for elements such as:

* phone numbers
* currencies
* numbers and percentages
* dates and times.

Version 2.2.0 introduces the concept of *locale*. A new suite of [docma provided
Jinja filters](#docma-jinja-filters) use locale information
to handle the elements listed above in accordance with locale specific
conventions instead of requiring the template designer to handle everything
manually. For example:

```jinja
{{ 123456 | decimal }} -- Format using locale specific separators etc.
{{ 123456 | AUD }} -- Format however Australian $ are shown in the current locale
```

See [Docma Jinja Rendering](#docma-jinja-rendering) for more information.

The locale for a template manifests as an additional Jinja rendering parameter,
`locale`, which is expressed in the normal way as a combination of a language
indicator and a 2 character ISO country code. e.g. `en_AU`, `en_CA`, `fr_CA`.
It can be set in the same way as any other rendering parameter, including any,
or all, of the following (from lowest precedence to highest):

*   Including it in the `parameters -> defaults` in the
    [template configuration file](#template-configuration-file).

*   Specifying it on the command line when rendering a template to PDF or HTML
    output.

*   Setting it within a template using `{% set locale="...." %}`.

*   In some [jinja filters](#docma-jinja-filters), specifying
    locale as an explicit argument to override the current effective value.

From version 2.2.0, new templates created using [docma
new](#creating-a-new-document-template) will include a default value in the
[template configuration file](#template-configuration-file). It's a good idea to
add it to earlier templates, thus:

```yaml
# config.yaml

parameters:
  defaults:
    locale: "en_AU"
```

!!! info
    If `locale` is not specified using one of the mechanisms described above, it
    will default to whatever random value the underlying platform assumes.
    Good luck with that.
