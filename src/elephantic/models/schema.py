"""Pydantic models for PostgreSQL schemas."""

import pydantic


class Schema(pydantic.BaseModel):
    """Represents a PostgreSQL schema.

    A schema is a namespace that contains database objects like tables,
    views, functions, etc. Schema names cannot begin with 'pg_' as that
    prefix is reserved for system schemas.
    """

    name: str | None = pydantic.Field(
        default=None,
        description='The schema name (cannot begin with pg_)',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role that owns the schema (defaults to project superuser)',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the schema',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/schema.html',
        },
    }

    @pydantic.model_validator(mode='after')
    def validate_name(self) -> 'Schema':
        """Validate that schema name doesn't begin with pg_."""
        if self.name and self.name.startswith('pg_'):
            raise ValueError(
                'Schema name cannot begin with pg_ (reserved for system schemas)'
            )
        return self
