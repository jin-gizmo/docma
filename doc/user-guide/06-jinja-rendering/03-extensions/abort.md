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
