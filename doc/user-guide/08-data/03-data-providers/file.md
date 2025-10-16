
### Data Provider Type: file

**Docma** can read data from static files contained within the compiled document
template.


The `type` component of the [data source specification](#data-sources-in-docma)
is `file`.

The `location` component is the name of the file, relative to the root of the
template. Handling is determined based on the file suffix. The following formats
are supported:

|File Suffix| Description |
|-|--------------|
|csv|A CSV file with a header line. The excel dialect is assumed.|
|jsonl|A file containing one JSON formatted object per line.|

The `query` component is not used.

!!! example "Examples"

    === "CSV Data"

        In these examples, the csv file (`data/dogs.csv`) might look something
        like this:

        ```bare
        Dog,Woof
        Bolliver,28
        Rin Tin Tin,55
        Fido,43
        Kipper,91
        Zoltan,81
        Pluto,53
        Scooby,24
        Cerberus,87
        Snoopy,52
        ```

    === "Chart"

        This example shows a CSV file being used to supply data to a chart
        (using Jinja tuple notation):

        ```html+jinja
        <IMG
            style="width: 10cm; justify-self: start;"
            src="docma:vega?{{ (
                  ( 'spec', 'charts/woof.yaml'),
                  ( 'data', 'file;data/dogs.csv'),
                ) | urlencode }}"
        >
        ```

    === "HTML Table"

        This example shows a CSV file being used to populate an HTML table:

        ```html+jinja
        <TABLE>
          <THEAD>
          <TR>
            <TH>Dog</TH>
            <TH class="Woof">Woof</TH>
          </TR>
          </THEAD>
          <TBODY>
          {% for row in docma.data('file', 'data/dogs.csv', 'queries/woof-power.yaml') %}
          <TR>
            <TD class="Dog">{{ row.Dog }}</TD>
            <TD class="Woof">{{ row.Woof }}</TD>
          </TR>
          {% endfor %}
          </TBODY>
        </TABLE>
        ```
