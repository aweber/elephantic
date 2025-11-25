"""Pydantic models for PostgreSQL functions."""

from __future__ import annotations

import enum
import typing

import pydantic


class ParameterMode(enum.StrEnum):
    """Function parameter mode enumeration."""

    IN = 'IN'
    OUT = 'OUT'
    BOTH = 'BOTH'
    VARIADIC = 'VARIADIC'
    TABLE = 'TABLE'


class Security(enum.StrEnum):
    """Function security mode enumeration."""

    INVOKER = 'INVOKER'
    DEFINER = 'DEFINER'


class Parallel(enum.StrEnum):
    """Function parallel execution mode enumeration."""

    SAFE = 'SAFE'
    UNSAFE = 'UNSAFE'
    RESTRICTED = 'RESTRICTED'


class Parameter(pydantic.BaseModel):
    """Function parameter definition."""

    mode: ParameterMode = pydantic.Field(
        description='Parameter mode',
    )
    name: str | None = pydantic.Field(
        default=None,
        description='Parameter name',
    )
    data_type: str = pydantic.Field(
        description='Parameter data type',
    )
    default: bool | int | float | str | None = pydantic.Field(
        default=None,
        description='Default value for parameter',
    )

    model_config = {'extra': 'forbid'}


class Function(pydantic.BaseModel):
    """Represents a PostgreSQL function.

    Defines a user-defined function.
    """

    schema_: str = pydantic.Field(
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema the function is created in',
    )
    name: str = pydantic.Field(
        description='The function name',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role that owns the function',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    parameters: list[Parameter] | None = pydantic.Field(
        default=None,
        description='An array of IN, OUT, BOTH, VARIADIC, and TABLE args',
    )
    returns: str | None = pydantic.Field(
        default=None,
        description='The return type for the function',
    )
    language: str | None = pydantic.Field(
        default=None,
        description=(
            'The name of the language that the function is implemented in. It can be '
            'sql, c, internal, or the name of a user-defined procedural language'
        ),
    )
    transform_types: list[str] | None = pydantic.Field(
        default=None,
        description='Lists which transforms a call to the function should apply',
    )
    window: bool | None = pydantic.Field(
        default=None,
        description=(
            'Indicates that the function is a window function rather than a plain function'
        ),
    )
    immutable: bool | None = pydantic.Field(
        default=None,
        description=(
            'Indicates that the function cannot modify the database and always returns '
            'the same result when given the same argument values'
        ),
    )
    stable: bool | None = pydantic.Field(
        default=None,
        description=(
            'Indicates that the function cannot modify the database, and that within '
            'a single table scan it will consistently return the same result for the '
            'same argument values'
        ),
    )
    volatile: bool | None = pydantic.Field(
        default=None,
        description=(
            'Indicates that the function value can change even within a single table scan'
        ),
    )
    leak_proof: bool | None = pydantic.Field(
        default=None,
        description=(
            'Indicates that the function has no side effects. It reveals no information '
            'about its arguments other than by its return value'
        ),
    )
    called_on_null_input: bool = pydantic.Field(
        default=True,
        description=(
            'Indicates that the function will be called normally when some of its '
            'arguments are null'
        ),
    )
    strict: bool = pydantic.Field(
        default=False,
        description=(
            'Indicates that the function always returns null whenever any of its '
            'arguments are null'
        ),
    )
    security: Security | None = pydantic.Field(
        default=None,
        description=(
            'INVOKER indicates that the function is to be executed with the privileges '
            'of the user that calls it. DEFINER specifies that the function is to be '
            'executed with the privileges of the user that owns it'
        ),
    )
    parallel: Parallel | None = pydantic.Field(
        default=None,
        description=(
            'Indicates whether the function can be executed in parallel mode'
        ),
    )
    cost: int | None = pydantic.Field(
        default=None,
        description=(
            'A positive number giving the estimated execution cost for the function, '
            'in units of cpu_operator_cost'
        ),
    )
    rows: int | None = pydantic.Field(
        default=None,
        description=(
            'A positive number giving the estimated number of rows that the planner '
            'should expect the function to return'
        ),
    )
    support: str | None = pydantic.Field(
        default=None,
        description=(
            'The name (optionally schema-qualified) of a planner support function to '
            'use for this function'
        ),
    )
    configuration: dict[str, str | int | float | bool] | None = pydantic.Field(
        default=None,
        description=(
            'Configuration parameters to be set to the specified value when the '
            'function is entered, and then restored to its prior value when the '
            'function exits'
        ),
    )
    definition: str | None = pydantic.Field(
        default=None,
        description=(
            'A string constant defining the function; the meaning depends on the language'
        ),
    )
    object_file: str | None = pydantic.Field(
        default=None,
        description=(
            'Used for dynamically loadable C language functions when the function name '
            'in the C language source code is not the same as the name of the SQL function'
        ),
    )
    link_symbol: str | None = pydantic.Field(
        default=None,
        description=(
            "The string link_symbol is the function's link symbol when used in "
            'conjunction with object_file'
        ),
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the function',
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
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/function.html',
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

    @pydantic.field_validator('configuration')
    @classmethod
    def validate_configuration_names(
        cls, v: dict[str, str | int | float | bool] | None
    ) -> dict[str, str | int | float | bool] | None:
        """Validate that configuration parameter names match the required pattern."""
        import re

        if v is None:
            return v
        pattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_\.]*$')
        for key in v.keys():
            if not pattern.match(key):
                raise ValueError(
                    f'Configuration parameter name "{key}" does not match required '
                    f'pattern: ^[A-Za-z_][A-Za-z0-9_\\.]*$'
                )
        return v

    @pydantic.model_validator(mode='after')
    def validate_sql_or_structured(self) -> Function:
        """Validate that either sql OR structured fields are provided, not both."""
        has_sql = self.sql is not None

        if has_sql:
            # When using SQL, structured fields should not be provided
            structured_fields = [
                'returns',
                'language',
                'transform_types',
                'window',
                'immutable',
                'stable',
                'volatile',
                'leak_proof',
                'called_on_null_input',
                'strict',
                'security',
                'parallel',
                'cost',
                'rows',
                'support',
                'configuration',
                'definition',
                'object_file',
                'link_symbol',
            ]
            has_structured = False
            for field in structured_fields:
                value = getattr(self, field)
                # Check if value is not None and not default
                if field == 'called_on_null_input':
                    if value is not True:
                        has_structured = True
                        break
                elif field == 'strict':
                    if value is not False:
                        has_structured = True
                        break
                elif value is not None:
                    has_structured = True
                    break

            if has_structured:
                raise ValueError(
                    'Cannot specify sql with structured fields (returns, language, etc.)'
                )
            return self

        # If not using SQL, require language, returns, and definition
        if not self.language or not self.returns or not self.definition:
            raise ValueError(
                'Must specify either sql or all of: language, returns, and definition'
            )

        # Cannot have object_file or link_symbol without using SQL
        if self.object_file is not None or self.link_symbol is not None:
            raise ValueError(
                'Cannot specify object_file or link_symbol without sql'
            )

        return self
