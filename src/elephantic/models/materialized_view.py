"""Pydantic models for PostgreSQL materialized views."""

from __future__ import annotations

import typing

import pydantic


class MaterializedViewColumn(pydantic.BaseModel):
    """Materialized view column definition."""

    name: str = pydantic.Field(
        description='Column name',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='Comment',
    )

    model_config = {'extra': 'forbid'}


class MaterializedView(pydantic.BaseModel):
    """Represents a PostgreSQL materialized view.

    Defines a materialized view.
    """

    schema_: str = pydantic.Field(
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema the materialized view is created in',
    )
    name: str = pydantic.Field(
        description='The materialized view name',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role that owns the materialized view',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    columns: list[str | MaterializedViewColumn] | None = pydantic.Field(
        default=None,
        description='An optional list of names to be used for columns of the materialized view',
    )
    table_access_method: str | None = pydantic.Field(
        default=None,
        description='Define the table access method',
    )
    storage_parameters: dict[str, str | int | float | bool] | None = (
        pydantic.Field(
            default=None,
            description='Storage parameter settings for the materialized view',
        )
    )
    tablespace: str | None = pydantic.Field(
        default=None,
        description='Specifies the name of the tablespace in which the materialized view is to be created',
    )
    query: str | None = pydantic.Field(
        default=None,
        description='A SELECT or VALUES command which will provide the columns and rows',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the materialized view',
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
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/materialized_view.html',
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

    @pydantic.field_validator('storage_parameters')
    @classmethod
    def validate_storage_parameter_names(
        cls, v: dict[str, str | int | float | bool] | None
    ) -> dict[str, str | int | float | bool] | None:
        """Validate that storage parameter names match the required pattern."""
        import re

        if v is None:
            return v
        pattern = re.compile(r'^[A-Za-z0-9_]*$')
        for key in v.keys():
            if not pattern.match(key):
                raise ValueError(
                    f'Storage parameter name "{key}" does not match required pattern: ^[A-Za-z0-9_]*$'
                )
        return v

    @pydantic.model_validator(mode='after')
    def validate_materialized_view_definition(self) -> MaterializedView:
        """Validate materialized view definition.

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
                    self.columns is not None,
                    self.storage_parameters is not None,
                    self.tablespace is not None,
                    self.query is not None,
                ]
            ):
                raise ValueError(
                    'Cannot specify sql with structured fields '
                    '(columns, storage_parameters, tablespace, query)'
                )
            return self

        if not has_query:
            raise ValueError('Must specify either sql or query')

        return self
