
## Docma Jinja Rendering

The rendering phase uses Jinja to render HTML content with the parameters
provided at run-time. Other components (e.g.
[query specifications](#query-specifications)) also use Jinja rendering on some
of their content.

All of the facilities provided by Jinja are available, including parameter
injection, loops, conditional content and use of the `include` directive to
incorporate other content from the document template. Include directives should
use the name of the file relative to the template root. e.g.

```jinja2
{% include 'my-file.html' %}
```

See also [Jinja Rendering Parameters Provided by
Docma](#jinja-rendering-parameters-provided-by-docma).

In addition to standard Jinja facilities, docma also provides a number of extra
[filters](#custom-jinja-filters-provided-by-docma) and
[extensions](#custom-jinja-extensions-provided-by-docma).

### Custom Jinja Filters Provided by Docma

In addition to the standard filters provided by Jinja, docma provides the
following additions.

| Filter Name  | Description                                                                                                                 |
| ------------ | -------------------------------------------------- |
| abn (or ABN) | Format an ABN. e.g. `{{ customer_abn | ABN }}`    |
| acn (or ACN) | Format an ACN. e.g. `{{ customer_acn | ACN }}`    |
| css\_id       | Sanitise a string to be a valid CSS identifier.    |
| dollars      | Format a number as dollars with specified precision (default 2). e.g. `{{ price | dollars }}` or `{{ price | dollars(0) }}`. An optional second argument can specify the currency indicator (default `$`). Note that this uses *half round up* rounding (like Excel) not *bankers rounding* like the Python / Jinja2 `round` function. |
| require       | Abort with an error message if the value is not a truthy value (i.e. a non-empty string, non-zero integer etc) otherwise return the value. This is useful for things such as ensuring an expression has a value. e.g. `{{ my_var | require('my_var must be a non-empty string') }}`|
| sql\_safe     | Ensure that a string value is safe to use in SQL and generate an error if not. This is primarily for use in query specifications to avoid SQL injection. It has a puritanical view on safety but will cover most normal requirements. e.g. `SELECT * from {{ table | sql_safe }} ...` |

### Custom Jinja Extensions Provided by Docma

Docma provides some custom Jinja extensions.
In Jinja, extensions are invoked using the following syntax:

```jinja
{% tag [parameters] %}
```

In addition to the custom extensions described below, docma also provides the
following standard Jinja extensions:

*   [debug](https://jinja.palletsprojects.com/en/stable/extensions/#debug-extension)
*   [loopcontrols](https://jinja.palletsprojects.com/en/stable/extensions/#loop-controls).


#### Jinja Extension: abort

The **abort** extension forces the rendering process to abort with an exception
message. It would typically be used in response to some failed correctness check
where it's preferable to fail document production rather than to proceed in
error.

For example:

```jinja
{% if bad_data %}
    {% abort 'Fatal error - bad data' %}
{% endif %}
```

#### Jinja Extension: dump\_params

The **dump\_params** extension simply dumps the rendering parameters for
debugging purposes. The standard Jinja
[debug](https://jinja.palletsprojects.com/en/stable/extensions/#debug-extension)
extension does something similar (and a bit more) but much less readably.

Typical usage would be:

```html
<PRE>{% dump_params %}</PRE>
```

#### Jinja Extension: global

The **global** extension allows values defined within the Jinja content of a
HTML document to be made available when rendering other components in a
document template.

For example, the following declares the *globals* `a` and `b`.

```jinja
{% global a=1, b='Plugh' %}
```

These can then be accessed, either in the file in which they were declared or in
a different HTML document, or a [query specification](#query-specifications)
like so:


```jinja
You are at Y{{ globals.a + 1 }}. A hollow voice says "{{ globals.b }}."
```

The result will be:

```bare
Your are at Y2. A hollow voice says "Plugh".
```

Compare this with the standard Jinja `set` operation:

```jinja
{% set a=1 %}
```

The variable `a` can only be accessed in the file in which it is defined, or a
file that includes that file. It cannot be accessed in a different HTML
document, or a [query specification](#query-specifications)

> **Warning**: It is important to understand that within the docma rendering
> phase, the Jinja rendering of the component HTML documents is *completed* before
> the [generation and injection of dynamic content](#dynamic-content-generation).
> This means that only the *final* value of any global parameter is available
> during the dynamic content generation phase. i.e. It is not possible to use
> globals to pass a loop variable from the Jinja rendering of the HTML into
> the dynamic content generation phase.

