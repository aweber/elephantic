"""Pydantic models for PostgreSQL conversions."""

from __future__ import annotations

import typing

import pydantic


class Conversion(pydantic.BaseModel):
    """Represents a PostgreSQL conversion.

    A conversion defines how to convert between character set encodings.
    Conversions can be defined using raw SQL or by specifying the source
    encoding, destination encoding, and conversion function.
    """

    name: str = pydantic.Field(
        description='The name of the conversion',
    )
    schema_: str = pydantic.Field(
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema for the conversion',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role that owns the conversion',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    default: bool | None = pydantic.Field(
        default=None,
        description=(
            'Indicates that this conversion is the default for this particular '
            'source to destination encoding. There should be only one default '
            'encoding in a schema for the encoding pair.'
        ),
    )
    encoding_from: str | None = pydantic.Field(
        default=None,
        description='The source encoding name',
    )
    encoding_to: str | None = pydantic.Field(
        default=None,
        description='The destination encoding name',
    )
    function: str | None = pydantic.Field(
        default=None,
        description='The function used to perform the conversion',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the conversion',
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
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/conversion.html',
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
    def validate_conversion_definition(self) -> Conversion:
        """Validate conversion definition.

        Either sql OR (encoding_from, encoding_to, function) must be provided.
        """
        has_sql = self.sql is not None
        has_encoding_from = self.encoding_from is not None
        has_encoding_to = self.encoding_to is not None
        has_function = self.function is not None
        has_default = self.default is not None

        if has_sql:
            # If using sql, cannot use encoding or function parameters
            if (
                has_default
                or has_encoding_from
                or has_encoding_to
                or has_function
            ):
                raise ValueError(
                    'Cannot specify default, encoding_from, encoding_to, or '
                    'function when using sql'
                )
            return self

        # If not using sql, must have encoding_from, encoding_to, and function
        if not has_sql:
            if not (has_encoding_from and has_encoding_to and has_function):
                raise ValueError(
                    'Must specify either sql OR (encoding_from, encoding_to, '
                    'and function)'
                )

        return self
