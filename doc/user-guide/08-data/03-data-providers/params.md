### Data Provider Type: params

**Docma** can extract data from a list of objects in the rendering parameters.

The `type` component of the [data source specification](#data-sources-in-docma)
is `params`.

The `location`  component is a dot separated key sequence
to select a data list within the parameters. Each element of the list must be
an object (not a string).

The `query` component is not used.

!!! example "Examples"

    === "Source Data"

        Consider the following rendering parameters:

        ```yaml
        param1: value1
        param2: value2

        data:
          custard:
            prices:
              - type: lumpy
                price: 1.53
              - type: baked
                price: 2.84
              - type: runny
                price: 3.50
        ```

        A data source specification of `params;data.custard.prices` would return
        the following data rows:

        ```json
        { "type": "lumpy", "price": 1.53 }
        { "type": "baked", "price": 2.84 }
        { "type": "runny", "price": 3.5 }
        ```

    === "Chart"
        This example shows rendering parameters being used to supply data to a 
        chart (using Jinja tuple notation):

        ```html+jinja
        <IMG
            style="width: 10cm;"
            src="docma:vega?{{ (
                ( 'spec', 'charts/custard-prices-chart.yaml' ),
                ( 'data', 'params;data.custard.prices' ),
            ) | urlencode }}"
        >
        ```

    === "HTML Table"

        This example shows rendering parameters being used to populate an HTML
        table:

        ```html+jinja
        <TABLE>
          <THEAD>
          <TR>
            <TH>Custard Type</TH>
            <TH class="price">Price</TH>
          </TR>
          </THEAD>
          <TBODY>
          {% for row in docma.data('params', 'data.custard.prices') %}
          <TR>
            <TD class="type">{{ row.type }}</TD>
            <TD class="price">{{ row.price }}</TD>
          </TR>
          {% endfor %}
          </TBODY>
        </TABLE>
        ```
