"""Pydantic models for PostgreSQL domains."""

from __future__ import annotations

import typing

import pydantic


class CheckConstraint(pydantic.BaseModel):
    """Check constraint for a domain."""

    name: str | None = pydantic.Field(
        default=None,
        description='Constraint name',
    )
    nullable: bool | None = pydantic.Field(
        default=None,
        description='Domain is nullable',
    )
    expression: str | None = pydantic.Field(
        default=None,
        description='Constraint expression',
    )

    model_config = {'extra': 'forbid'}

    @pydantic.model_validator(mode='after')
    def validate_expression_or_nullable(self) -> CheckConstraint:
        """Validate that either expression OR nullable is provided, not both."""
        has_expression = self.expression is not None
        has_nullable = self.nullable is not None

        if has_expression and has_nullable:
            raise ValueError(
                'Cannot specify both expression and nullable in a check constraint'
            )

        if not has_expression and not has_nullable:
            raise ValueError(
                'Must specify either expression or nullable in a check constraint'
            )

        return self


class Domain(pydantic.BaseModel):
    """Represents a PostgreSQL domain.

    A domain creates a user-defined data type with optional constraints.
    """

    name: str = pydantic.Field(
        description='The name of the domain to create',
    )
    schema_: str = pydantic.Field(
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema to create the domain in',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role that owns the domain',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    data_type: str | None = pydantic.Field(
        default=None,
        description='The underlying data type of the domain',
    )
    collation: str | None = pydantic.Field(
        default=None,
        description=(
            'An optional collation for the domain. If no collation is specified, '
            "the underlying data type's default collation is used"
        ),
    )
    default: bool | int | float | str | None = pydantic.Field(
        default=None,
        description=(
            'The DEFAULT clause specifies a default value for columns of the '
            'domain data type'
        ),
    )
    check_constraints: list[CheckConstraint] | None = pydantic.Field(
        default=None,
        description='An array of one or more check constraints',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the domain',
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
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/domain.html',
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

    @pydantic.field_validator('check_constraints')
    @classmethod
    def validate_unique_constraints(
        cls, v: list[CheckConstraint] | None
    ) -> list[CheckConstraint] | None:
        """Validate that check constraints are unique."""
        if v is not None and len(v) != len({str(c.model_dump()) for c in v}):
            raise ValueError('Check constraints must be unique')
        return v

    @pydantic.model_validator(mode='after')
    def validate_sql_or_data_type(self) -> Domain:
        """Validate that either sql OR data_type is provided, not both."""
        has_sql = self.sql is not None
        has_data_type = self.data_type is not None
        has_check_constraints = self.check_constraints is not None

        if has_sql and (has_data_type or has_check_constraints):
            raise ValueError(
                'Cannot specify sql with data_type or check_constraints'
            )

        if not has_sql and not has_data_type:
            raise ValueError('Must specify either sql or data_type')

        return self
