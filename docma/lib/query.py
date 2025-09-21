"""Manage query specifications."""

from __future__ import annotations

from decimal import Decimal
from enum import Enum
from functools import cached_property
from typing import Any, Callable

import jsonschema
from pydantic import BaseModel, ConfigDict, Field, constr, field_validator
from referencing.jsonschema import EMPTY_REGISTRY

from docma.exceptions import DocmaDataProviderError
from docma.jinja import DocmaRenderContext
from docma.lib.jsonschema import FORMAT_CHECKER
from docma.lib.misc import str2bool

# ------------------------------------------------------------------------------
NameTypeString = constr(pattern='^[a-zA-Z][a-zA-Z0-9_]*$')


# ------------------------------------------------------------------------------
class QueryParameterType(Enum):
    """Allow for some basic type casting in query parameters."""

    def __new__(cls, value: str, cast: Callable):
        """Allow our values to have an associated type cast function."""
        obj = object.__new__(cls)
        obj._value_ = value
        obj.cast = cast
        return obj

    # Order is important if we are redefining value of a type e.g. str
    string = 'string', str
    str = 'str', str  # noqa: A003
    integer = 'integer', int
    int = 'int', int  # noqa: A003
    float = 'float', float  # noqa: A003
    decimal = 'decimal', Decimal
    boolean = 'boolean', str2bool  # noqa: A003
    bool = 'bool', str2bool  # noqa: A003


# ------------------------------------------------------------------------------
class QueryParameter(BaseModel):
    """Model for managing query parameters."""

    model_config = ConfigDict(extra='forbid')

    name: NameTypeString
    value: str
    type: QueryParameterType = QueryParameterType.str  # noqa: A003


# ------------------------------------------------------------------------------
class QueryOptions(BaseModel):
    """Configuration options for a query."""

    model_config = ConfigDict(extra='forbid')

    fold_headers: bool = False
    row_limit: int = 0


# ------------------------------------------------------------------------------
class DocmaQuerySpecification(BaseModel):
    """Model for managing query specifications."""

    model_config = ConfigDict(extra='forbid')

    name: str
    description: constr(min_length=1)
    parameters: list[QueryParameter] = Field(None, description='A list of query parameters')
    query: constr(min_length=1)
    row_schema: dict[str, Any] = Field(None, alias='schema')
    options: QueryOptions = Field(default_factory=QueryOptions)

    # --------------------------------------------------------------------------
    @field_validator('row_schema')  # noqa
    @classmethod
    def _(cls, value: dict[str, Any]) -> dict[str, Any]:
        """Validate row schema."""

        validator_cls = jsonschema.validators.validator_for(value)
        try:
            validator_cls.check_schema(value)
        except (jsonschema.ValidationError, jsonschema.SchemaError) as e:
            raise ValueError(f'Bad row schema: {e}') from e
        return value

    # --------------------------------------------------------------------------
    @cached_property
    def row_checker(self) -> jsonschema.Validator:
        """Row validator for data coming from the database."""
        return (
            jsonschema.validators.validator_for(self.row_schema)(
                schema=self.row_schema, registry=EMPTY_REGISTRY, format_checker=FORMAT_CHECKER
            )
            if self.row_schema
            else None
        )

    # --------------------------------------------------------------------------
    def check_row(self, data: dict[str, Any]):
        """Validate a row of data from the database against the schema."""

        if v := self.row_checker:
            v.validate(data)

    # ------------------------------------------------------------------------------
    def prepare_query(
        self, context: DocmaRenderContext, params: dict[str, Any] = None, paramstyle: str = 'format'
    ) -> tuple[str, list] | tuple[str, dict[str, Any]]:
        """
        Prepare a query from a query specification.

        :param context:     Document rendering context.
        :param params:      Additional rendering parameters.
        :param paramstyle:  DBAPI 2.0 paramstyle.

        :return:    For named param styles: A tuple:
                    (rendered query text, dict of rendered param values)
                    For positional param styles: A tuple:
                    (rendered query text, list of rendered query parameters)
                    The rationale for this structure is that the query and param
                    values get fed directly to a DBAPI 2.0 cursor.execute() so
                    they need to be in the right format for the respective paramstyle.
        """

        query_txt = context.render(self.query, {'docma': {'paramstyle': paramstyle}}, params)

        if not self.parameters:
            return query_txt, []

        if paramstyle in ('format', 'qmark', 'numeric'):
            return query_txt, [
                p.type.cast(context.render(p.value, params)) for p in self.parameters
            ]

        if paramstyle in ('named', 'pyformat'):
            return query_txt, {
                p.name: p.type.cast(context.render(p.value, params)) for p in self.parameters
            }

        raise ValueError(f'Unknown paramstyle: {paramstyle}')

    # --------------------------------------------------------------------------
    def fetch_from_cursor(self, cursor) -> list[dict[str, Any]]:
        """
        Consume the data from a cursor on which a query has been executed.

        :param cursor:  DBAPI 2.0 cursor. The query must have already been
                        executed.
        """

        data = []
        columns = [f[0] for f in cursor.description]
        if self.options.fold_headers:
            columns = [f.lower() for f in columns]

        row_count = 0
        while True:
            row = cursor.fetchone()
            if not row:
                break
            row_count += 1
            if self.options.row_limit and row_count > self.options.row_limit:
                raise DocmaDataProviderError(
                    f'{self.name}: Row limit ({self.options.row_limit}) reached.'
                )

            r = dict(zip(columns, row))
            try:
                self.check_row(r)
            except Exception as e:
                raise DocmaDataProviderError(f'{self.name}: Bad data {r}: {e}') from e
            data.append(r)
        return data
