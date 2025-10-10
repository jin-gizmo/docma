
??? "Heat Map"

    This heat map shows electricity interval meter data.

    === "Chart"

        ![](img/samples/heatmap.png)

    === "Chart specification file"

        ```yaml
        $schema: 'https://vega.github.io/schema/vega-lite/v5.json'
        title: 'Daily Usage'
        config:
          font: Avenir
          view:
            continuousWidth: 300
            continuousHeight: 300
            step: 13
            strokeWidth: 0
          axis:
            domain: false
        data:
          name: usage_by_day

        mark:
          type: rect
        encoding:
          color:
            aggregate: max
            field: kwh
            legend:
              title: kWh
            type: quantitative
            scale:
              range: [ '#fec72b', '#fa4617' ]
          x:
            axis:
              format: '%e'
              labelAngle: 0
            field: date
            timeUnit: date
            title: Day
            type: ordinal
          y:
            field: date
            timeUnit: month
            title: Month
            type: ordinal
        datasets:
          # Sample data -- this gets replaced
          usage_by_day:
            - date: 2023-07-01
              kwh: 1234
        ```



