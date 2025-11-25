"""Pydantic models for PostgreSQL text search."""

from __future__ import annotations

import pydantic


class Configuration(pydantic.BaseModel):
    """Text search configuration."""

    name: str = pydantic.Field(
        description='The name of the text search configuration to be created',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided SQL',
    )
    parser: str | None = pydantic.Field(
        default=None,
        description='The name of the text search parser to use',
    )
    source: str | None = pydantic.Field(
        default=None,
        description='The name of an existing text search configuration to copy',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='Comment',
    )

    model_config = {'extra': 'forbid'}

    @pydantic.model_validator(mode='after')
    def validate_sql_or_parser_or_source(self) -> Configuration:
        """Validate that exactly one of sql, parser, or source is provided."""
        has_sql = self.sql is not None
        has_parser = self.parser is not None
        has_source = self.source is not None

        count = sum([has_sql, has_parser, has_source])
        if count == 0:
            raise ValueError('Must specify one of: sql, parser, or source')
        if count > 1:
            raise ValueError(
                'Cannot specify more than one of: sql, parser, or source'
            )

        return self


class Dictionary(pydantic.BaseModel):
    """Text search dictionary."""

    name: str = pydantic.Field(
        description='The name of the text search dictionary to be created',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided SQL',
    )
    template: str | None = pydantic.Field(
        default=None,
        description=(
            'The name of the text search template that will define the basic behavior '
            'of this dictionary'
        ),
    )
    options: dict[str, str | int | float | bool] | None = pydantic.Field(
        default=None,
        description='Template specific options',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='Comment',
    )

    model_config = {'extra': 'forbid'}

    @pydantic.field_validator('options')
    @classmethod
    def validate_option_names(
        cls, v: dict[str, str | int | float | bool] | None
    ) -> dict[str, str | int | float | bool] | None:
        """Validate that option names match the required pattern."""
        import re

        if v is None:
            return v
        pattern = re.compile(r'^[A-Za-z0-9_]*$')
        for key in v.keys():
            if not pattern.match(key):
                raise ValueError(
                    f'Option name "{key}" does not match required pattern: ^[A-Za-z0-9_]*$'
                )
        return v

    @pydantic.model_validator(mode='after')
    def validate_sql_or_template(self) -> Dictionary:
        """Validate that either sql OR template is provided, not both."""
        has_sql = self.sql is not None
        has_template = self.template is not None

        if has_sql and (has_template or self.options is not None):
            raise ValueError('Cannot specify sql with template or options')

        if not has_sql and not has_template:
            raise ValueError('Must specify either sql or template')

        return self


class Parser(pydantic.BaseModel):
    """Text search parser."""

    name: str = pydantic.Field(
        description='The name of the text search parser to be created',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided SQL',
    )
    start_function: str | None = pydantic.Field(
        default=None,
        description='The name of the start function for the parser',
    )
    gettoken_function: str | None = pydantic.Field(
        default=None,
        description='The name of the get-next-token function for the parser',
    )
    end_function: str | None = pydantic.Field(
        default=None,
        description='The name of the end function for the parser',
    )
    lextypes_function: str | None = pydantic.Field(
        default=None,
        description=(
            'The name of the lextypes function for the parser (a function that '
            'returns information about the set of token types it produces)'
        ),
    )
    headline_function: str | None = pydantic.Field(
        default=None,
        description=(
            'The name of the headline function for the parser (a function that '
            'summarizes a set of tokens)'
        ),
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='Comment',
    )

    model_config = {'extra': 'forbid'}

    @pydantic.model_validator(mode='after')
    def validate_sql_or_functions(self) -> Parser:
        """Validate that either sql OR required functions are provided."""
        has_sql = self.sql is not None
        has_required_functions = all(
            [
                self.start_function is not None,
                self.gettoken_function is not None,
                self.end_function is not None,
                self.lextypes_function is not None,
            ]
        )

        if has_sql and has_required_functions:
            raise ValueError(
                'Cannot specify sql with start_function, gettoken_function, '
                'end_function, or lextypes_function'
            )

        if not has_sql and not has_required_functions:
            raise ValueError(
                'Must specify either sql or all of: start_function, gettoken_function, '
                'end_function, and lextypes_function'
            )

        return self


class Template(pydantic.BaseModel):
    """Text search template."""

    name: str = pydantic.Field(
        description='The name of the text search template to be created',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided SQL',
    )
    init_function: str | None = pydantic.Field(
        default=None,
        description='The name of the init function for the template',
    )
    lexize_function: str | None = pydantic.Field(
        default=None,
        description='The name of the lexize function for the template',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='Comment',
    )

    model_config = {'extra': 'forbid'}

    @pydantic.model_validator(mode='after')
    def validate_sql_or_lexize_function(self) -> Template:
        """Validate that either sql OR lexize_function is provided, not both."""
        has_sql = self.sql is not None
        has_lexize = self.lexize_function is not None

        if has_sql and (has_lexize or self.init_function is not None):
            raise ValueError(
                'Cannot specify sql with lexize_function or init_function'
            )

        if not has_sql and not has_lexize:
            raise ValueError('Must specify either sql or lexize_function')

        return self


class TextSearch(pydantic.BaseModel):
    """Represents PostgreSQL text search objects.

    Defines all properties for text-search in a schema.
    """

    schema_: str = pydantic.Field(
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema for the text search objects',
    )
    configurations: list[Configuration] | None = pydantic.Field(
        default=None,
        description='Text search configurations',
    )
    dictionaries: list[Dictionary] | None = pydantic.Field(
        default=None,
        description='Text search dictionaries',
    )
    parsers: list[Parser] | None = pydantic.Field(
        default=None,
        description='Text search parsers',
    )
    templates: list[Template] | None = pydantic.Field(
        default=None,
        description='Text search templates',
    )

    @property
    def schema(self) -> str:
        """Backward-compatible access to schema_ field."""
        return self.schema_

    model_config = {
        'extra': 'forbid',
        'populate_by_name': True,
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/text_search.html',
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
