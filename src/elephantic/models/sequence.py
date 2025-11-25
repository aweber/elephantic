"""Pydantic models for PostgreSQL sequences."""

from __future__ import annotations

import enum

import pydantic


class DataType(enum.StrEnum):
    """Sequence data type enumeration."""

    SMALLINT = 'smallint'
    SMALLINT_UPPER = 'SMALLINT'
    INT2 = 'int2'
    INT2_UPPER = 'INT2'
    INTEGER = 'integer'
    INTEGER_UPPER = 'INTEGER'
    INT4 = 'int4'
    INT4_UPPER = 'INT4'
    BIGINT = 'bigint'
    BIGINT_UPPER = 'BIGINT'
    INT8 = 'int8'
    INT8_UPPER = 'INT8'


class Sequence(pydantic.BaseModel):
    """Represents a PostgreSQL sequence object.

    A sequence generates unique numeric identifiers.
    """

    schema_: str | None = pydantic.Field(
        default=None,
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema the sequence is created in',
    )
    name: str | None = pydantic.Field(
        default=None,
        description='The sequence name',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role that owns the sequence',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    data_type: DataType = pydantic.Field(
        default=DataType.BIGINT_UPPER,
        description='Specifies the data type of the sequence',
    )
    increment_by: int = pydantic.Field(
        default=1,
        description=(
            'Specifies which value is added to the current sequence value to create '
            'a new value. A positive value will make an ascending sequence, a '
            'negative one a descending sequence'
        ),
    )
    min_value: int = pydantic.Field(
        default=1,
        description='Specifies the minimum value a sequence can generate',
    )
    max_value: int | None = pydantic.Field(
        default=None,
        description='Specifies the maximum value for the sequence',
    )
    start_with: int | None = pydantic.Field(
        default=None,
        description='Specifies the value to start the sequence at',
    )
    cache: int = pydantic.Field(
        default=1,
        description=(
            'Specifies how many sequence numbers are to be preallocated and stored '
            'in memory for faster access'
        ),
    )
    cycle: bool | None = pydantic.Field(
        default=None,
        description=(
            'When set to true, the sequence can wrap around when it hits the maximum '
            'value. When false, the sequence will return an error when it hits the '
            'maximum value'
        ),
    )
    owned_by: str | None = pydantic.Field(
        default=None,
        description=(
            'Specifies the schema.table.column that owns the column. In pglifecycle '
            'this setting will allow the sequence to automatically be set when DML '
            'is provided for a table that has a sequence column'
        ),
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the sequence',
    )

    @property
    def schema(self) -> str | None:
        """Backward-compatible access to schema_ field."""
        return self.schema_

    model_config = {
        'extra': 'forbid',
        'populate_by_name': True,
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/sequence.html',
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
    def validate_sql_or_name_schema(self) -> Sequence:
        """Validate that either sql OR (schema and name) is provided."""
        has_sql = self.sql is not None
        has_schema_name = self.schema_ is not None and self.name is not None

        if has_sql:
            # Check if any non-default structured fields are set
            has_structured = False
            if self.data_type != DataType.BIGINT_UPPER:
                has_structured = True
            if self.increment_by != 1:
                has_structured = True
            if self.min_value != 1:
                has_structured = True
            if self.cache != 1:
                has_structured = True
            if self.max_value is not None:
                has_structured = True
            if self.start_with is not None:
                has_structured = True
            if self.cycle is not None:
                has_structured = True

            if has_structured:
                raise ValueError(
                    'Cannot specify sql with structured fields (data_type, increment_by, etc.)'
                )

        if not has_sql and not has_schema_name:
            raise ValueError('Must specify either sql or both schema and name')

        return self
