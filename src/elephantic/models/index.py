"""Pydantic models for PostgreSQL indexes."""

from __future__ import annotations

import enum
import typing

import pydantic


class IndexMethod(enum.StrEnum):
    """Index method enumeration."""

    BRIN = 'brin'
    BTREE = 'btree'
    GIN = 'gin'
    GIST = 'gist'
    HASH = 'hash'
    SPGIST = 'spgist'


class SortDirection(enum.StrEnum):
    """Sort direction enumeration."""

    ASC = 'ASC'
    DESC = 'DESC'


class NullPlacement(enum.StrEnum):
    """NULL value placement enumeration."""

    FIRST = 'FIRST'
    LAST = 'LAST'


class IndexColumn(pydantic.BaseModel):
    """Index column definition."""

    name: str | None = pydantic.Field(
        default=None,
        description='The column name',
    )
    expression: str | None = pydantic.Field(
        default=None,
        description='Expression for the column',
    )
    collation: str | None = pydantic.Field(
        default=None,
        description='Assigns a collation to the column',
    )
    opclass: str | None = pydantic.Field(
        default=None,
        description='The name of an operator class',
    )
    direction: SortDirection | None = pydantic.Field(
        default=None,
        description='Specifies the sort direction in the index for the column',
    )
    null_placement: NullPlacement | None = pydantic.Field(
        default=None,
        description='Specifies the placement of null values in the index',
    )

    model_config = {'extra': 'forbid'}

    @pydantic.model_validator(mode='after')
    def validate_name_or_expression(self) -> IndexColumn:
        """Validate that exactly one of name or expression is provided."""
        has_name = self.name is not None
        has_expression = self.expression is not None

        if has_name and has_expression:
            raise ValueError('Cannot specify both name and expression')
        if not has_name and not has_expression:
            raise ValueError('Must specify either name or expression')

        return self


class Index(pydantic.BaseModel):
    """Represents a PostgreSQL index.

    Defines an index on a table.
    """

    name: str | None = pydantic.Field(
        default=None,
        description='The index name',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    unique: bool | None = pydantic.Field(
        default=None,
        description='Specifies that the index is a unique index',
    )
    recurse: bool | None = pydantic.Field(
        default=None,
        description='Used to specify that the index should be created on partitions of the table',
    )
    method: IndexMethod | None = pydantic.Field(
        default=None,
        description='The name of the index method to be used',
    )
    columns: list[IndexColumn] | None = pydantic.Field(
        default=None,
        description='Defines the columns that are indexed',
    )
    include: list[str] | None = pydantic.Field(
        default=None,
        description='Use to provide a list of non-key columns to provide in the index',
    )
    storage_parameters: dict[str, str | int | float | bool] | None = (
        pydantic.Field(
            default=None,
            description='Storage parameter settings for the index',
        )
    )
    tablespace: str | None = pydantic.Field(
        default=None,
        description='Specifies the tablespace to use when creating the index',
    )
    where: str | None = pydantic.Field(
        default=None,
        description='Use to provide an expression for creating a partial index',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the index',
    )
    dependencies: typing.Any = pydantic.Field(
        default=None,
        description='Database objects this object is dependent upon',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/index.html',
        },
    }

    @pydantic.field_validator('storage_parameters')
    @classmethod
    def validate_storage_parameter_names(
        cls, v: dict[str, str | int | float | bool] | None
    ) -> dict[str, str | int | float | bool] | None:
        """Validate that storage parameter names match the required pattern."""
        import re

        if v is None:
            return v
        pattern = re.compile(r'^[A-Za-z0-9_]+$')
        for key in v.keys():
            if not pattern.match(key):
                raise ValueError(
                    f'Storage parameter name "{key}" does not match required pattern: ^[A-Za-z0-9_]+$'
                )
        return v

    @pydantic.model_validator(mode='after')
    def validate_index_definition(self) -> Index:
        """Validate index definition.

        Either sql OR (name and columns) must be provided.
        """
        has_sql = self.sql is not None
        has_name = self.name is not None
        has_columns = self.columns is not None

        if has_sql and (has_name or has_columns):
            raise ValueError('Cannot specify sql with name or columns')

        if has_sql:
            # If using sql, cannot use structured fields
            if any(
                [
                    self.method is not None,
                    self.storage_parameters is not None,
                    self.unique is not None,
                    self.recurse is not None,
                    self.include is not None,
                    self.where is not None,
                ]
            ):
                raise ValueError(
                    'Cannot specify sql with structured fields '
                    '(method, storage_parameters, unique, recurse, include, where)'
                )
            return self

        if not has_name or not has_columns:
            raise ValueError('Must specify either sql OR (name and columns)')

        return self
