"""Pydantic models for PostgreSQL casts."""

from __future__ import annotations

import typing

import pydantic


class Cast(pydantic.BaseModel):
    """Represents a PostgreSQL cast.

    A cast specifies how to convert between two data types. Casts can be
    defined using raw SQL, a conversion function, or I/O conversion through
    the source and target type's input/output functions.
    """

    schema_: str | None = pydantic.Field(
        default=None,
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema containing the cast',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role that owns the cast',
    )
    source_type: str = pydantic.Field(
        description='The source data type of the cast',
    )
    target_type: str = pydantic.Field(
        description='The target data type of the cast',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    function: str | None = pydantic.Field(
        default=None,
        description=(
            'The function used to perform the cast. The function name can be '
            'schema-qualified. If it is not, the function will be looked up in '
            "the schema search path. The function's result data type must match "
            'the target type of the cast. Its arguments are discussed below.'
        ),
    )
    inout: bool = pydantic.Field(
        default=False,
        description=(
            'Indicates that the cast is an I/O conversion cast, performed by '
            'invoking the output function of the source data type, and passing '
            'the resulting string to the input function of the target data type.'
        ),
    )
    assignment: bool = pydantic.Field(
        default=False,
        description=(
            'Indicates that the cast can be invoked implicitly in assignment '
            'contexts.'
        ),
    )
    implicit: bool = pydantic.Field(
        default=False,
        description=(
            'Indicates that the cast can be invoked implicitly in any context.'
        ),
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the cast',
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
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/cast.html',
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
    def validate_cast_definition(self) -> Cast:
        """Validate that cast is defined correctly.

        Either sql OR one of (function, inout, assignment, implicit) must be
        provided, with specific combinations allowed.
        """
        has_sql = self.sql is not None
        has_function = self.function is not None
        has_inout = self.inout
        has_assignment = self.assignment
        has_implicit = self.implicit

        if has_sql:
            # If using SQL, cannot use any other definition methods
            if has_function or has_inout or has_assignment or has_implicit:
                raise ValueError(
                    'Cannot specify function, inout, assignment, or implicit '
                    'when using sql'
                )
            return self

        # If not using SQL, must have function OR inout OR assignment OR implicit
        if not (has_function or has_inout or has_assignment or has_implicit):
            raise ValueError(
                'Must specify either sql OR one of: function, inout, '
                'assignment, implicit'
            )

        # If using function, cannot use inout
        if has_function and has_inout:
            raise ValueError('Cannot specify both function and inout')

        # If using inout, cannot use function
        if has_inout and has_function:
            raise ValueError('Cannot specify both inout and function')

        return self
