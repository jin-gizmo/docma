
### Data Provider Type: duckdb

**Docma** can read data from a local file containing a
[DuckDB](https://duckdb.org) database.

The DuckDB data provider is a useful mechanism for handling data extracts with
**docma**. **Docma**, running on a DuckDB data extract can be quite fast, even
with moderately large datasets.

!!! question "Why DuckDB?"
    Why DuckDB rather than, for example, SQLite? DuckDB has a much more complete
    SQL implementation than SQLite, and one which is much closer to Postgres. It
    also has a very powerful and flexible mechanism for accessing data from
    other sources (files in various formats, AWS S3 etc.). And it goes like the
    clappers.

The `type` component of the [data source specification](#data-sources-in-docma)
is `duckdb`.

The `location` component is the name of a local file (not a template file)
containing the database.

The `query` component is the name of a
[query specification](#query-specifications) file.

!!! example "Examples"

    === "Chart"

        This example shows a DuckDB database being used to supply data to a chart 
        (using Jinja tuple notation):

        ```html+jinja
        <IMG
            style="width: 10cm;"
            src="docma:vega?{{ (
                ( 'spec', 'charts/dog-woof-power-chart.yaml' ),
                ( 'data', 'duckdb;/tmp/demo/dogs.db;queries/woof-power.yaml' ),
            ) | urlencode }}"
        >
        ```

    === "HTML Table"

        This example shows a DuckDB database being used to populate an HTML table:

        ```html+jinja
            <TABLE>
              <THEAD>
              <TR>
                <TH>Dog</TH>
                <TH class="Woof">Woof</TH>
              </TR>
              </THEAD>
              <TBODY>
              {% for row in docma.data('duckdb', '/tmp/demo/dogs.db', 'queries/woof-power.yaml') %}
              <TR>
                <TD class="Dog">{{ row.Dog }}</TD>
                <TD class="Woof">{{ row.Woof }}</TD>
              </TR>
              {% endfor %}
              </TBODY>
            </TABLE>
        ```
