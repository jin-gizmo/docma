#### Jinja Filter: sql_safe

Ensure that a string value is safe to use in SQL and generate an error if not.

This is primarily for use in query specifications to avoid SQL injection. It has
a puritanical view on safety but will cover most normal requirements.

!!! note "Filter Signature"

    ```python
    sql_safe(value: str) -> str
    ```

!!! example

    ```jinja
    SELECT * from {{ table | sql_safe }} ...
    ```
