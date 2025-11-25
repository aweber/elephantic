"""Pydantic models for PostgreSQL operators."""

from __future__ import annotations

import typing

import pydantic


class Operator(pydantic.BaseModel):
    """Represents a PostgreSQL operator.

    User defined comparison operator.
    """

    name: str | None = pydantic.Field(
        default=None,
        description='The name of the operator to create',
    )
    schema_: str | None = pydantic.Field(
        default=None,
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema to create the operator in',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role that owns the operator',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    function: str | None = pydantic.Field(
        default=None,
        description='The function used to implement this operator',
    )
    left_arg: str | None = pydantic.Field(
        default=None,
        description=(
            "The data type of the operator's left operand, if any. This option would "
            'be omitted for a left-unary operator'
        ),
    )
    right_arg: str | None = pydantic.Field(
        default=None,
        description=(
            "The data type of the operator's right operand, if any. This option would "
            'be omitted for a right-unary operator'
        ),
    )
    commutator: str | None = pydantic.Field(
        default=None,
        description='The commutator of this operator',
    )
    negator: str | None = pydantic.Field(
        default=None,
        description='The negator of this operator',
    )
    restrict: str | None = pydantic.Field(
        default=None,
        description='The restriction selectivity estimator function for this operator',
    )
    join: str | None = pydantic.Field(
        default=None,
        description='The join selectivity estimator function for this operator',
    )
    hashes: bool | None = pydantic.Field(
        default=None,
        description='Indicates this operator can support a hash join',
    )
    merges: bool | None = pydantic.Field(
        default=None,
        description='Indicates this operator can support a merge join',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the operator',
    )
    dependencies: typing.Any = pydantic.Field(
        default=None,
        description='Database objects this object is dependent upon',
    )

    @property
    def schema(self) -> str | None:
        """Backward-compatible access to schema_ field."""
        return self.schema_

    model_config = {
        'extra': 'forbid',
        'populate_by_name': True,
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/operator.html',
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
    def validate_sql_or_function(self) -> Operator:
        """Validate that either sql OR function is provided, not both."""
        has_sql = self.sql is not None
        has_function = self.function is not None

        if has_sql and has_function:
            raise ValueError('Cannot specify both sql and function')

        if has_sql:
            # When using SQL, structured fields should not be provided
            structured_fields = [
                'left_arg',
                'right_arg',
                'commutator',
                'negator',
                'restrict',
                'join',
                'hashes',
                'merges',
            ]
            has_structured = any(
                getattr(self, field) is not None for field in structured_fields
            )
            if has_structured:
                raise ValueError(
                    'Cannot specify sql with structured fields (left_arg, right_arg, etc.)'
                )
            return self

        if not has_function:
            raise ValueError('Must specify either sql or function')

        return self
