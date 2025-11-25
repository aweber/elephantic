"""Pydantic models for database object dependencies."""

import pydantic


class Dependencies(pydantic.BaseModel):
    """Represents dependencies between database objects.

    Tracks references to other database objects that an object depends upon,
    such as domains, extensions, functions, sequences, tables, types, and views.
    """

    domains: list[str] | None = pydantic.Field(
        default=None,
        description='Dependent domains in schema.domain format',
    )
    extensions: list[str] | None = pydantic.Field(
        default=None,
        description='Dependent extensions',
    )
    foreign_data_wrappers: list[str] | None = pydantic.Field(
        default=None,
        description='Dependent foreign data wrappers',
    )
    functions: list[str] | None = pydantic.Field(
        default=None,
        description='Dependent functions in schema.function(args) format',
    )
    languages: list[str] | None = pydantic.Field(
        default=None,
        description='Dependent procedural languages',
    )
    sequences: list[str] | None = pydantic.Field(
        default=None,
        description='Dependent sequences in schema.sequence format',
    )
    tables: list[str] | None = pydantic.Field(
        default=None,
        description='Dependent tables in schema.table format',
    )
    types: list[str] | None = pydantic.Field(
        default=None,
        description='Dependent types in schema.type format',
    )
    views: list[str] | None = pydantic.Field(
        default=None,
        description='Dependent views in schema.view format',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/dependencies.html',
        },
    }

    @pydantic.field_validator(
        'domains', 'sequences', 'tables', 'types', 'views'
    )
    @classmethod
    def validate_schema_object_pattern(
        cls, v: list[str] | None
    ) -> list[str] | None:
        """Validate schema.object pattern."""
        if v is None:
            return v
        for item in v:
            if item.count('.') != 1:
                raise ValueError(
                    f'Must be in schema.object format, got: {item}'
                )
        return v

    @pydantic.field_validator('functions')
    @classmethod
    def validate_function_pattern(
        cls, v: list[str] | None
    ) -> list[str] | None:
        """Validate schema.function(args) pattern."""
        if v is None:
            return v
        for item in v:
            if '(' not in item or ')' not in item:
                raise ValueError(
                    f'Must be in schema.function(args) format, got: {item}'
                )
            if item.count('.') != 1 or item.index('.') > item.index('('):
                raise ValueError(
                    f'Must be in schema.function(args) format, got: {item}'
                )
        return v
