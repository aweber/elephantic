"""Pydantic models for PostgreSQL views."""

from __future__ import annotations

import enum
import typing

import pydantic


class CheckOption(enum.StrEnum):
    """Check option enumeration."""

    LOCAL = 'LOCAL'
    CASCADED = 'CASCADED'


class ViewColumn(pydantic.BaseModel):
    """View column definition."""

    name: str = pydantic.Field(
        description='Column name',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='Comment',
    )

    model_config = {'extra': 'forbid'}


class View(pydantic.BaseModel):
    """Represents a PostgreSQL view.

    Defines a view.
    """

    schema_: str = pydantic.Field(
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema the view is created in',
    )
    name: str = pydantic.Field(
        description='The view name',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role that owns the view',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    recursive: bool | None = pydantic.Field(
        default=None,
        description='Specifies the view is a recursive view',
    )
    columns: list[str | ViewColumn] | None = pydantic.Field(
        default=None,
        description='An optional list of names to be used for columns of the view',
    )
    check_option: CheckOption | None = pydantic.Field(
        default=None,
        description='Controls the behavior of automatically updatable views',
    )
    security_barrier: bool | None = pydantic.Field(
        default=None,
        description='This should be used if the view is intended to provide row-level security',
    )
    query: str | None = pydantic.Field(
        default=None,
        description='A SELECT or VALUES command which will provide the columns and rows of the view',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the view',
    )
    dependencies: typing.Any = pydantic.Field(
        default=None,
        description='Database objects this object is dependent upon',
    )

    @property
    def schema(self) -> str:
        """Backward-compatible access to schema_ field."""
        return self.schema_

    model_config = {
        'extra': 'forbid',
        'populate_by_name': True,
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/view.html',
        },
    }

    @pydantic.model_serializer(mode='wrap')
    def _serialize_model(self, serializer, info):
        """Serialize model using aliases by default."""
        data = serializer(self)
        # Use aliases for all serialization
        if 'schema_' in data:
            data['schema'] = data.pop('schema_')
        return data

    @pydantic.model_validator(mode='after')
    def validate_view_definition(self) -> View:
        """Validate view definition.

        Either sql OR query must be provided.
        """
        has_sql = self.sql is not None
        has_query = self.query is not None

        if has_sql and has_query:
            raise ValueError('Cannot specify both sql and query')

        if has_sql:
            # If using sql, cannot use structured fields
            if any(
                [
                    self.recursive is not None,
                    self.columns is not None,
                    self.query is not None,
                ]
            ):
                raise ValueError(
                    'Cannot specify sql with structured fields (recursive, columns, query)'
                )
            return self

        if not has_query:
            raise ValueError('Must specify either sql or query')

        return self
