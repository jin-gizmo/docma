??? "Bar Chart"

    This is a bar chart of dog woof-power.

    === "Chart"

        ![](img/samples/woof.png)

    === "Chart Specification File"

        This is the specification file (with truncated data).

        ```yaml
        $schema: 'https://vega.github.io/schema/vega-lite/v5.json'
        width: 300
        config:
          font: Avenir
          background: '#eeeeee'
          padding: 10
          view:
            stroke: transparent
          axisX:
            grid: false
            gridWidth: 0.5
            domainDash:
              - 4
              - 4
            formatType: number
          axisY:
            grid: false
        data:
          values:
            - Dog: Bolliver
              Woof: 28
        view:
          fill: '#eeeeee'
        encoding:
          'y':
            field: Dog
            title: Dog
            type: ordinal
            axis: null
        layer:
          - mark:
              type: bar
              cornerRadius: 20
            encoding:
              x:
                field: Woof
                title: null
                type: quantitative
              color:
                field: Woof
                type: quantitative
                title: '% Woof'
                scale:
                  domain: [ 0, 100 ]
                  range: [ '#fec72b', '#fa4617' ]
          - mark:
              type: text
              align: left
              x: 10
              color: white
              fontWeight: bold
            encoding:
              text:
                field: Dog
        ```
