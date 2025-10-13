
### Data Provider Type: postgres

Docma can read data from a Postgres database.

The `type` component of the [data source specification](#data-sources-in-docma)
is `postgres`.

The `location` component is an alpha-numeric label for the database. This is
used to determine connection details from environment variables or the contents
of a `.env` file.

If the `location` component is `xyz`, then docma will read the following values
from a `.env` file to connect to the database.

| Name | Description |
|-|--------------|
|XYZ\_USER|Database user name|
|XYZ\_PASSWORD|Password. Exactly one of `XYZ_PASSWORD` and `XYZ_PASSWORD_PARAM` must be specified.|
|XYZ\_PASSWORD\_PARAM|AWS SSM parameter containing the password.|
|XYZ\_HOST|Host name|
|XYZ\_PORT|Port number|
|XYZ\_DATABASE|Database name|
|XYZ\_SSL|A truthy value specifying if SSL should be enforced (default `no`)|

Values can also be overridden by environment variables with the same names as
above, prefixed with `DOCMA_`. e.g. `DOCMA_XYZ_USER`.

!!! danger
    Take care to ensure the `.env` file is excluded from any GIT repo. A
    redacted sample is provided in the `test` directory.

The `query` component is the name of a
[query specification](#query-specifications) file.

!!! example "Examples"

    === "Chart"

        This example shows a Postgres database being used to supply data to a
        chart (using Jinja tuple notation):

        ```html+jinja
        <IMG
            style="width: 10cm;"
            src="docma:vega?{{ (
                ( 'spec', 'charts/dog-woof-power-chart.yaml' ),
                ( 'data', 'postgres;prod01;queries/woof-power.yaml' ),
            ) | urlencode }}"
        >
        ```

    === "HTML Table"

        This example shows a Postgres database being used to populate an HTML
        table:

        ```html+jinja
        <TABLE>
          <THEAD>
          <TR>
            <TH>Dog</TH>
            <TH class="Woof">Woof</TH>
          </TR>
          </THEAD>
          <TBODY>
          {% for row in docma.data('postgres', 'prod01', 'queries/woof-power.yaml') %}
          <TR>
            <TD class="Dog">{{ row.Dog }}</TD>
            <TD class="Woof">{{ row.Woof }}</TD>
          </TR>
          {% endfor %}
          </TBODY>
        </TABLE>
        ```
