"""Common components for data providers."""

from __future__ import annotations

from typing import Any, Callable

from docma.exceptions import DocmaDataProviderError
from docma.jinja import DocmaRenderContext

_DATA_SOURCE_TYPE = {}


# ------------------------------------------------------------------------------
def data_provider(data_src_type: str) -> Callable:
    """
    Register the data provider function for the specified data source type.

    This is a decorator used like so:

    .. code-block:: python

        @data_provider('postgres')
        def postgres(
            data_src: DataSourceSpec, pkg: PackageReader, params: dict[str, Any]
        )  -> list[dict[str, Any]]:
            ...

    :param data_src_type: Data source type.

    """

    def decorate(func: Callable) -> Callable:
        """Register the handler function."""
        _DATA_SOURCE_TYPE[data_src_type] = func
        return func

    return decorate


# ------------------------------------------------------------------------------
def data_provider_for_src_type(data_src_type: str) -> Callable:
    """Get the data provider function for the specified type."""

    try:
        return _DATA_SOURCE_TYPE[data_src_type]
    except KeyError:
        raise DocmaDataProviderError(f'{data_src_type}: Unknown data provider type')


# ------------------------------------------------------------------------------
class DataSourceSpec:
    """
    Data source specifier.

    The components are:

    :param src_type: The data provider type (e.g. `csv` if the data comes from
                    a CSV file). This controls the connection / access mechanism.

    :param location: The location where to find the data. For a file based
                    source it would be the path to the file in the document
                    template package.

    :param query:   The query to execute on the data provider. This is required for
                    database-like sources. It is not used for some types (e.g.
                    data sourced from the rendering parameters).

    :param target:  The position in the Vega-Lite specification where the data
                    will be attached. This is a dot separated dictionary key
                    sequence.  If not provided, this defaults to `data.values`,
                    which is the primary data location for a Vega-Lite
                    specification.

    When referenced in HTML, these are formatted as strings in the form
    `<type>;<path>[;query[;target]`

    Examples
    --------
    -   `params;a.b.c`

        Get data from key a->b->c in the rendering parameters and attach it in
        the default location in the chart specification.

    -   `file;data/x.csv;;data.values`

        Get data from the CSV file `data/x.csv` and attach it in the chart
        specification at date->values (which happens to be the default).
        Note that the query is empty in this case.

    -   `file;data/x.sqlite;q.sql`

        Run a query on the SQLite3 database and attach the data at the
        degault location in the chart specification.

    """

    def __init__(self, src_type: str, location: str, query: str = None, target: str = None):
        """Initialise a data source specification."""

        if not all((src_type, location)):
            raise ValueError('Bad data source specification: type and location required')
        self.type = src_type
        self.location = location
        self.query = query
        self.target = target

    @classmethod
    def from_string(cls, s: str) -> DataSourceSpec:
        """
        Initialise a data source specification from a string.

        :param s:   A string in the form `<type>;<path>[;query[;target]`
        """

        src_type, location, query, target, *_ = (s + ';;;;').split(';')
        try:
            return cls(src_type, location, query, target)
        except ValueError as e:
            raise ValueError(f'{s}: {e}')

    def __str__(self) -> str:
        """Return string representation of data source specification."""
        return ';'.join((self.type, self.location, self.query or '', self.target or '')).rstrip(';')

    def __eq__(self, other: DataSourceSpec) -> bool:
        """Test for equality."""

        return all(
            (
                self.type == other.type,
                self.location == other.location,
                self.query == other.query,
                self.target == other.target,
            )
        )


# ------------------------------------------------------------------------------
def load_data(
    data_src: DataSourceSpec, context: DocmaRenderContext, **kwargs
) -> list[dict[str, Any]]:
    """
    Load a data set.

    :param data_src:    Data source specifier.
    :param context:     Document rendering context.
    :param kwargs:      Additional keyword arguments for the data loader.
    :return:            A list of dicts, each containing one row.
    """

    load_handler = data_provider_for_src_type(data_src.type)
    data = load_handler(data_src, context, **kwargs)

    if not isinstance(data, list) or (data and not isinstance(data[0], dict)):
        raise DocmaDataProviderError(f'{data_src}: Bad data - must be a list of dicts')

    return data
