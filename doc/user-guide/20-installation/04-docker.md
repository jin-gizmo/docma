
## Docker

The [repo](https://jin-gizmo.github.io) includes support for building a docker
container on an Amazon Linux 2023 base with **docma** installed. To build the
image:

```bash
make docker
```

This will include support for the [duckdb](#data-provider-type-duckdb) data
provider, but not the [lava](#data-provider-type-lava) data provider.

!!! info
    The basic image doesn't add any fonts to the minimal set already available
    in the Amazon Linux 2023 image. To add fonts, build your own image on the
    **docma** base image.
