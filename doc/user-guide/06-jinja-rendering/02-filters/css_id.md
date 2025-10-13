#### Jinja Filter: css_id

Sanitise a string to be a valid CSS identifier.

!!! "Filter Signature"

    ```python
    css_id(value: str) -> str
    ```

!!! example

    ```jinja
    {{ 'a/()=*&bcd'' | css_id }} --> abcd
    ```
