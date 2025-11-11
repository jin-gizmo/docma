
### Data Provider Type: lava { data-toc-label="Lava" }

If the **lava** package is [installed](#installing-docma), **docma** can use the
**lava** connection subsystem to read data from a database. Lava provides support
for connecting to a range of database types, including Postgres, Redshift, SQL
Server, MySQL and Oracle. It also manages all of the connection details,
credentials etc.

The `type` component of the data source specification is `lava`.

The `location` component is a **lava** connection ID for a database.

The `query` component is the name of a
[query specification](#query-specifications) file.

The **lava** realm must be specified during rendering, either by setting the
`LAVA_REALM` environment variable, or via the `--realm` argument to the CLI.

!!! info
    The [query text](#query-text) must use a
    [paramstyle](https://peps.python.org/pep-0249/#paramstyle) that matches the
    underlying driver being used by **lava**. Refer to the **lava** user guide for more
    information.

!!! example "Examples"

    === "Chart"

        This example shows a **lava** database connector (ID=`redshift/prod`) being
        used to supply data to a chart (using Jinja tuple notation):

        ```html+jinja
        <IMG
            style="width: 10cm;"
            src="docma:vega?{{ (
                ( 'spec', 'charts/dog-woof-power-chart.yaml' ),
                ( 'data', 'lava;redshift/prod;queries/woof-power.yaml' ),
            ) | urlencode }}"
        >
        ```

    === "HTML Table"

        This example shows a **lava** database connector (ID=`redshift/prod`) being
        used to populate an HTML table:

        ```html+jinja
        <TABLE>
          <THEAD>
          <TR>
            <TH>Dog</TH>
            <TH class="Woof">Woof</TH>
          </TR>
          </THEAD>
          <TBODY>
          {% for row in docma.data('lava', 'redshift/prod', 'queries/woof-power.yaml') %}
          <TR>
            <TD class="Dog">{{ row.Dog }}</TD>
            <TD class="Woof">{{ row.Woof }}</TD>
          </TR>
          {% endfor %}
          </TBODY>
        </TABLE>
        ```

