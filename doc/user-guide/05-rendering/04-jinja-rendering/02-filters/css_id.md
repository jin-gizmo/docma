#### Jinja Filter: css_id

Sanitise a string to be a valid CSS identifier.

```jinja
{{ 'a/()=*&bcd'' | css_id }} --> abcd
```
