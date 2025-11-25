"""Pydantic models for PostgreSQL publications."""

from __future__ import annotations

import enum

import pydantic


class PublishOperation(enum.StrEnum):
    """Publish operation enumeration."""

    INSERT = 'insert'
    UPDATE = 'update'
    DELETE = 'delete'
    TRUNCATE = 'truncate'


class PublicationParameters(pydantic.BaseModel):
    """Publication parameters."""

    publish: list[PublishOperation] = pydantic.Field(
        description='This parameter determines which DML operations will be published',
    )

    model_config = {'extra': 'forbid'}


class Publication(pydantic.BaseModel):
    """Represents a PostgreSQL publication.

    A publication is essentially a group of tables whose data changes are intended
    to be replicated through logical replication.
    """

    name: str = pydantic.Field(
        description='The name of the publication to create',
    )
    tables: list[str] | None = pydantic.Field(
        default=None,
        description='Specifies a list of tables to add to the publication',
        min_length=1,
    )
    all_tables: bool | None = pydantic.Field(
        default=None,
        description='Use to replicate all tables',
    )
    parameters: PublicationParameters | None = pydantic.Field(
        default=None,
        description='Publication parameters',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the publication',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/publication.html',
        },
    }

    @pydantic.model_validator(mode='after')
    def validate_tables_or_all_tables(self) -> Publication:
        """Validate that either tables OR all_tables is provided, not both."""
        has_tables = self.tables is not None
        has_all_tables = self.all_tables is not None

        if has_tables and has_all_tables:
            raise ValueError('Cannot specify both tables and all_tables')
        if not has_tables and not has_all_tables:
            raise ValueError('Must specify either tables or all_tables')

        return self
