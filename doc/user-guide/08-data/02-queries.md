
## Query Specifications

Some data providers require a query to be specified to extract the data. In
docma, this is done using a **query specification**.

A query specification is a YAML formatted file in the document template. It is
referenced as the third element of a
[data source specification](#data-source-specifications). These should be placed
in the `queries` directory in the template.

Docma thus externalises all database queries into a single, visible collection
rather than embedding them in random places within the template document
components.

A query specification file contains the DML of the query to be executed as well
as information on how to handle query parameters. It contains the following
keys:

| Key | Type |Required | Description|
|---|---|---|--------------------------|
| description | String | Yes | A description for human consumption. Not used by docma. |
| options | Object | No | Query control options.|
|--> fold_headers | Boolean | No | Convert all headers to lowercase (prior to row validation). This is sometimes necessary as different database drivers can handle the case treatment of headers in different ways. The default is `false`.|
|--> row_limit | Integer | No | Abort if the query returns more than the specified number of rows. This is a safety mechanism. The default is 0, meaning no limit is applied. |
| parameters | List | No | A list of [query parameter specification](#query-parameters) objects. If empty, the query has no parameters (which would be unusual). The parameter values are Jinja rendered using the run-time rendering parameters. |
| query | String | Yes | The [query text](#query-text). This will be Jinja rendered using the run-time rendering parameters. |
| schema | Object | No | A JSON Schema specification for each row of data returned by the query. See [Query Schemas](#query-schemas) below. |

Here's a sample:

```yaml+jinja
description: Extract Custard Appreciation Society membership records

query: >-
  SELECT * FROM "{{ db.schema | sql_safe }}".custard
  WHERE favouritecustard=%s
    AND custardbidprice > %s
    AND custardjedi=%s;
  SORT BY surname;

parameters:
  - name: favouritecustard
    value: '{{ db.favouritecustard }}'
  - name: custardbidprice
    value: '{{ db.custardbidprice }}'
    type: decimal
  - name: custardjedi
    value: '{{ db.custardjedi }}'
    type: boolean

options:
  row_limit: 20
  fold_headers: true
```

### Query Text

The query itself is pretty vanilla (ha!) SQL with some notable exceptions.

**Firstly,** the query text will be Jinja rendered with the docma run-time rendering
parameters. This makes it easy to do things such as switching schemas without
having to alter the document template. (This is close to impossible in some
popular analytics platforms that shall remain nameless.)

!!! tip
    It is probably best not to embed data source specification references within
    a query specification (i.e. recursive calls to the data provider subsystem).
    Don't cross the streams.

Care is required to avoid SQL injection risks. In the example above, the schema
is quoted and also filtered using the docma specific
[sql_safe](#docma-jinja-filters) Jinja filter. This filter
will abort if the value contains something unsafe.

**Secondly,** the values for query parameters are replaced with placeholders. The
actual values are determined at run-time from the parameter specifications. The
placeholder is database driver specific unfortunately, based on the
[paramstyle](https://peps.python.org/pep-0249/#paramstyle)
it uses. The `pg8000` driver used for Postgres uses `%s` style, whereas DuckDB
uses `?`. It's not my fault.

!!! danger
    **DO NOT** attempt to use Jinja to format query parameters into the SQL text
    itself. This is seriously unsafe. Use
    [query parameter specifications](#query-parameters).

**Thirdly,** when the data is to be used in a [Vega-Lite
chart](#charts-and-graphs-in-docma), all of the data returned by the query needs
to be JSON serialisable. i.e.  Python types such as `datetime`, `Decimal` etc
will be a problem. The query should type cast everything to types that can be
JSON serialised. For example:

```sql
-- This will not work ...
SELECT date_of_birth as dob, height_in_cm as height
FROM people;

-- This will work (Postgres syntax) ...
SELECT date_of_birth::text as dob, height_in_cm::float as height
FROM people;
```

### Query Parameters

Query parameters are specified as a list of query parameter specification objects.
These contain the following keys:

| Key | Type |Required | Description |
|---|---|---|-------------------------------------------------------------------|
|name|String|Yes| The parameter name. This is used for database drivers that support `named` and `pyformat` [paramstyles](https://peps.python.org/pep-0249/#paramstyle). It is mandatory for all parameters for maintainability. |
|value|String|Yes| The parameter value. In many cases this will be a Jinja value injection construct.|
|type|String|No| A type indicator. Docma uses this to cast the value to the specified type. Only the following are supported: `str` / `string`, `int` / `integer`, `float`, `decimal`, `bool` / `boolean`. The default is `string`. Alternatively, cast string values within the DML. |

These are supplied to the query at run-time using the DBAPI 2.0 driver's
query parameter mechanism to avoid SQL injection risks.

### Query Schemas

In some situations, it may be important to validate that the data returned by a
query meets certain conditions and to abort document production if it does
not. This can be achieved by including a `schema` object in the [query 
specification](#query-specifications).

!!! tip
    The data preparation process should take proper care to ensure valid data.
    Query Schemas are the last line of defence against bad data appearing in
    documents.

The `schema` object is a JSON Schema specification that is used to validate each
row of data. Validation failures will abort the process. Note that all rows are
returned as objects with keys based on the column names in the query.

For example, consider the following query specification:

```yaml
description: Get company information.

query: >-
  SELECT name, age_in_years, abn
  FROM companies;

# This schema will validate each row. We don't have to
# validate every attribute in a row. Just the ones we're
# worried about.
schema:
  type: object  # It's always one object per row of data
  properties:
    age_in_years:
      type: number
      minimum: 0
      maximum: 200
    abn:
      type: string
      format: au.ABN  # This is a docma provided format checker
```

In addition to the standard format specifiers supported by JSON Schema, the
[format checkers provided by
docma](#docma-format-checkers) are available for `string` objects.
