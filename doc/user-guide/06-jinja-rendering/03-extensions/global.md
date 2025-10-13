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

!!! warning
    It is important to understand that within the **docma** rendering phase, the
    Jinja rendering of the component HTML documents is *completed* before the
    [generation and injection of dynamic content](#dynamic-content-generation).
    This means that only the *final* value of any global parameter is available
    during the dynamic content generation phase.

    It is not possible to use globals to pass a loop variable from the Jinja
    rendering of the HTML into the dynamic content generation phase.

