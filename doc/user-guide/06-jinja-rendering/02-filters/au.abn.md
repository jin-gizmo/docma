#### Jinja Filter: au.abn

Format an Australian Business Number (ABN).

This supersedes the, now deprecated, `abn` filter.

!!! info "Filter Signature"

    ```python
    au.abn(value: str) -> str
    ```

!!! example

    ```jinja
    {{ '51824753556'  | au.abn }} --> 51 824 753 556 
    ```
