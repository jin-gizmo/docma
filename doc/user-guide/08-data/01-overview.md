
# Data Sources in Docma [nav: Data Sources]

**Docma** can access data files and live data sources during the rendering phase.
This is done by the *data provider* subsystem.
The returned data can be used in the following ways:

*   Source data for [charts and graphs](#data-source-specifications-for-charts).

*   Injection into the Jinja rendering process for
    [HTML content](#data-source-specifications-for-html-rendering) (e.g. for
    tables or other variable content).

Data providers return their data as a list of objects, one row of data per
object.

!!! tip
    Be careful with dataset sizes. This interface is not designed for very large
    amounts of data. Do as much data preparation / reduction outside of
    **docma** as possible (e.g. via database queries to generate just the
    essential data).

## Data Source Specifications

**Docma** uses the concept of **data source specifications** to control the
process of obtaining the data and what to do with it. They contain the following
components.

| Component | Description |
|-|-----------------------|
| type | The [data provider type](#data-provider-types) (e.g. `file` if the data comes from a file). This controls the connection / access mechanism.|
| location | Where to find the data. For a file based source it would be the path to the file. For a database provider, it would point to the connection information for the database.|
| query | The file name in the document template containing a [query specification](#query-specifications) that defines a query to execute on the data provider. This is required for database-like sources. It is not used for some data provider types. |
| target | For charts, the position in the Vega-Lite specification where the data will be attached. This is a dot separated dictionary key sequence pointing into the chart specification. If not provided, this defaults to `data.values`, which is the primary data location for a Vega-Lite specification. |

### Data Source Specifications for Charts

The HTML to include a chart is of the form:

```html
<IMG src="docma:vega?spec=charts/my-chart.yaml&data=...">
```

The value of the `data` parameter is a **docma**
[data source specification](#data-source-specifications)
expressed in string form, like so:

```bare
data=type;location[;query[;target]
```

!!! question
    Why jam all this together into a single URL parameter rather than have
    separate parameters for each component? The reason is because a Vega-Lite
    chart can have multiple data sources and hence multiple instances of the
    `data` parameter.

It can be fiddly combining all these components in a URL in a readable way. The
recommended approach is to use Jinja to assemble all the pieces and handle the
gory details of URL encoding, like so:

```html+jinja
<IMG style="width: 10cm;" src=docma:vega?{{
  (
    ( 'spec', 'charts/my-chart.yaml' ),
    ( 'data', 'file;data/my-data.csv' ),
    ( 'data', 'file;data/more-data.csv;;datasets.more_data' ),
    (
      'data', (
        'postgres', 'pgdb01', 'queries/usage-by-day.yaml', 'datasets.usage_by_day'
      ) | join(';'),
    ),
  ) | urlencode
}}">
```

In this example, three data sets are specified:

1.  The first one is extracted from a local CSV file and attached to the chart
    specification at the default location of `data.values` (i.e the `values`
    object under the `data` object is replaced with our CSV data).

2.  The second one is extracted from a local CSV file and attached to the chart
    specification as the `datasets.more_data` object in the specification. Note
    that the unused `query` component must be provided as an empty string to ensure the
    `target` component is correctly placed.

3.  The third one is extracted by running a query against a Postgres database
    and attached to the chart specification as the `datasets.usage_by_day`
    object in the specification.

### Data Source Specifications for HTML Rendering

A data source specification can be invoked directly in Jinja content within a
document that is to be rendered. 

This is done using the `docma.data()` function provided in the [run-time
rendering parameters](#rendering-parameters-provided-by-docma). It accepts
three arguments corresponding to the first three components of a [data source
specification](#data-source-specifications):

*   type 
*   location
*   query (optional).

The `docma.data()` function also accepts an optional `params` argument which is
a dictionary of additional parameter values that will be merged into the Jinja
rendering parameters when rendering the
[query specification](#query-specifications).

See also [Jinja Rendering Parameters Provided by
Docma](#rendering-parameters-provided-by-docma).

For example, the following document content invokes the
[postgres](#data-provider-type-postgres) data provider to run a query on the
Custard Appreciation Society membership records and present the data in a table.

```html+jinja
<TABLE>
  <THEAD>
  <TR>
    <TH>Custard Type</TH>
    <TH>Bid Price</TH>
  </TR>
  </THEAD>
  <TBODY>
  {% for row in docma.data('postgres', 'pgdb01', 'queries/custard-price.yaml') %}
    <TR>
      <TD>{{ row.favouritecustard }}</TD>
      <TD>{{ row.price | dollars(2) }}</TD>
    </TR>
  {% endfor %}
  </TBODY>
</TABLE>
</BODY>
</HTML>
```

If a query only returns a single row, that would be referenced like so:

```jinja
{{ docma.data(...)[0] }}
```

... or ...

```jinja
{{ docma.data(...) | first }}
```
