#### Jinja Extension: dump\_params

The **dump\_params** extension simply dumps the rendering parameters for
debugging purposes. The standard Jinja
[debug](https://jinja.palletsprojects.com/en/stable/extensions/#debug-extension)
extension does something similar (and a bit more) but much less readably.

Typical usage would be:

```html
<PRE>{% dump_params %}</PRE>
```
