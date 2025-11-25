"""Pydantic models for PostgreSQL tables."""

from __future__ import annotations

import enum
import typing

import pydantic

from .column import Column
from .foreign_key import ForeignKey
from .index import Index
from .trigger import Trigger


class PartitionType(enum.StrEnum):
    """Partition type enumeration."""

    HASH = 'HASH'
    LIST = 'LIST'
    RANGE = 'RANGE'


class LikeTable(pydantic.BaseModel):
    """Like table definition for copying structure."""

    name: str = pydantic.Field(
        description='The table to copy',
    )
    include_comments: bool | None = pydantic.Field(
        default=None,
        description='Include comments when creating the new table',
    )
    include_constraints: bool | None = pydantic.Field(
        default=None,
        description='Include constraints',
    )
    include_defaults: bool | None = pydantic.Field(
        default=None,
        description='Include defaults',
    )
    include_generated: bool | None = pydantic.Field(
        default=None,
        description='Include generated expressions',
    )
    include_identity: bool | None = pydantic.Field(
        default=None,
        description='Include identity specifications',
    )
    include_indexes: bool | None = pydantic.Field(
        default=None,
        description='Include indexes',
    )
    include_statistics: bool | None = pydantic.Field(
        default=None,
        description='Include extended statistics',
    )
    include_storage: bool | None = pydantic.Field(
        default=None,
        description='Include storage settings',
    )
    include_all: bool | None = pydantic.Field(
        default=None,
        description='Include all options',
    )

    model_config = {'extra': 'forbid'}


class PrimaryKey(pydantic.BaseModel):
    """Primary key definition."""

    columns: list[str] = pydantic.Field(
        description='The list of columns that provide the uniqueness',
        min_length=1,
    )
    include: list[str] | None = pydantic.Field(
        default=None,
        description='Use to provide a list of non-key columns to provide in the primary key index',
    )

    model_config = {'extra': 'forbid'}


class CheckConstraint(pydantic.BaseModel):
    """Check constraint definition."""

    name: str | None = pydantic.Field(
        default=None,
        description='Constraint name',
    )
    expression: str = pydantic.Field(
        description='Check constraint expression',
    )

    model_config = {'extra': 'forbid'}


class UniqueConstraint(pydantic.BaseModel):
    """Unique constraint definition."""

    columns: list[str] = pydantic.Field(
        description='The list of columns that provide the uniqueness',
        min_length=1,
    )
    include: list[str] | None = pydantic.Field(
        default=None,
        description='Use to provide a list of non-key columns to provide in the index',
    )

    model_config = {'extra': 'forbid'}


class ForeignTableOptions(pydantic.BaseModel):
    """Foreign table options."""

    schema_: str = pydantic.Field(
        validation_alias='schema',
        serialization_alias='schema',
        description='Foreign schema name',
    )
    name: str = pydantic.Field(
        description='Foreign table name',
    )

    @property
    def schema(self) -> str:
        """Backward-compatible access to schema_ field."""
        return self.schema_

    model_config = {'extra': 'forbid'}

    @pydantic.model_serializer(mode='wrap')
    def _serialize_model(self, serializer, info):
        """Serialize model using aliases by default."""
        data = serializer(self)
        # Use aliases for all serialization
        if 'schema_' in data:
            data['schema'] = data.pop('schema_')
        return data


class Table(pydantic.BaseModel):
    """Represents a PostgreSQL table.

    Defines a table.
    """

    name: str = pydantic.Field(
        description='The table name',
    )
    schema_: str = pydantic.Field(
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema to create the table in',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role name that owns the table',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    unlogged: bool | None = pydantic.Field(
        default=None,
        description='If specified, the table is created as an unlogged table',
    )
    from_type: str | None = pydantic.Field(
        default=None,
        description='Creates a typed table from the specified composite type',
    )
    parents: list[str] | None = pydantic.Field(
        default=None,
        description='A list of tables from which the new table automatically inherits all columns',
    )
    like_table: LikeTable | None = pydantic.Field(
        default=None,
        description='Specifies a table from which the new table automatically copies structure',
    )
    columns: list[Column] | None = pydantic.Field(
        default=None,
        description='Defines the columns in the table',
    )
    primary_key: str | list[str] | PrimaryKey | None = pydantic.Field(
        default=None,
        description='The PRIMARY KEY constraint',
    )
    indexes: list[Index] | None = pydantic.Field(
        default=None,
        description='An array of indexes on the table',
    )
    check_constraints: list[CheckConstraint] | None = pydantic.Field(
        default=None,
        description='Table check constraints',
    )
    unique_constraints: list[str | list[str] | UniqueConstraint] | None = (
        pydantic.Field(
            default=None,
            description='Unique constraints',
        )
    )
    foreign_keys: list[ForeignKey] | None = pydantic.Field(
        default=None,
        description='An array of foreign keys on the table',
    )
    triggers: list[Trigger] | None = pydantic.Field(
        default=None,
        description='An array of triggers on the table',
    )
    access_method: str | None = pydantic.Field(
        default=None,
        description='Specifies the table access method to use',
    )
    storage_parameters: dict[str, str | int | float | bool] | None = (
        pydantic.Field(
            default=None,
            description='Storage parameter settings for the table',
        )
    )
    tablespace: str | None = pydantic.Field(
        default=None,
        description='Specifies the name of the tablespace in which the new table is to be created',
    )
    index_tablespace: str | None = pydantic.Field(
        default=None,
        description='Tablespace for indexes associated with constraints',
    )
    server: str | None = pydantic.Field(
        default=None,
        description='Used to specify the server if this is a foreign table',
    )
    options: ForeignTableOptions | None = pydantic.Field(
        default=None,
        description='Used to specify the details of the foreign table',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the table',
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
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/table.html',
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
    def validate_table_definition(self) -> Table:
        """Validate table definition."""
        has_sql = self.sql is not None
        has_columns = self.columns is not None
        has_parents = self.parents is not None
        has_server = self.server is not None and self.options is not None

        # Count mutually exclusive definition types
        definition_count = sum([has_sql, has_columns, has_parents, has_server])

        if definition_count == 0:
            raise ValueError(
                'Must specify one of: sql, columns, parents, or (server and options)'
            )
        if definition_count > 1:
            raise ValueError(
                'Cannot specify more than one of: sql, columns, parents, or (server and options)'
            )

        return self
