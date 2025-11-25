"""Pydantic models for PostgreSQL aggregate functions."""

from __future__ import annotations

import enum

import pydantic

from elephantic.models import argument
from elephantic.models.dependencies import Dependencies


class FinalFuncModify(enum.StrEnum):
    """Final function modification behavior enumeration."""

    READ_ONLY = 'READ_ONLY'
    SHAREABLE = 'SHAREABLE'
    READ_WRITE = 'READ_WRITE'


class ParallelSafety(enum.StrEnum):
    """Parallelization safety enumeration."""

    SAFE = 'SAFE'
    RESTRICTED = 'RESTRICTED'
    UNSAFE = 'UNSAFE'


class Aggregate(pydantic.BaseModel):
    """Represents a PostgreSQL aggregate function.

    An aggregate function computes a single result from a set of input values.
    Aggregates can be defined either using raw SQL or by specifying the
    component functions and state information.
    """

    name: str = pydantic.Field(
        description='The name of the aggregate function to create',
    )
    schema_: str = pydantic.Field(
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema to create the aggregate function in',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role that owns the aggregate function',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    arguments: list[argument.Argument] | None = pydantic.Field(
        default=None,
        description='An array of arguments that are passed into the function',
    )
    order_by: list[argument.Argument] | None = pydantic.Field(
        default=None,
        description=(
            'An array of arguments that are passed into the function '
            'for ordered-set behavior'
        ),
    )
    sfunc: str | None = pydantic.Field(
        default=None,
        description=(
            'The name of the state transition function to be called '
            'for each input row'
        ),
    )
    state_data_type: str | None = pydantic.Field(
        default=None,
        description="The data type for the aggregate's state value",
    )
    state_data_size: int | None = pydantic.Field(
        default=None,
        description=(
            "The approximate average size (in bytes) of the aggregate's "
            'state value'
        ),
    )
    ffunc: str | None = pydantic.Field(
        default=None,
        description=(
            "The name of the final function called to compute the aggregate's "
            'result after all input rows have been traversed'
        ),
    )
    finalfunc_extra: bool | None = pydantic.Field(
        default=None,
        description=(
            'If true then in addition to the final state value and any direct '
            'arguments, the final function receives extra NULL values corresponding '
            "to the aggregate's regular (aggregated) arguments. This is mainly "
            'useful to allow correct resolution of the aggregate result type when '
            'a polymorphic aggregate is being defined.'
        ),
    )
    finalfunc_modify: FinalFuncModify | None = pydantic.Field(
        default=None,
        description=(
            'This option specifies whether the final function is a pure function '
            'that does not modify its arguments. READ_ONLY indicates it does not; '
            'the other two values indicate that it may change the transition state '
            'value.'
        ),
    )
    combinefunc: str | None = pydantic.Field(
        default=None,
        description=(
            'A function may optionally be specified to allow the aggregate '
            'function to support partial aggregation'
        ),
    )
    serialfunc: str | None = pydantic.Field(
        default=None,
        description=(
            'An aggregate function whose state_data_type is internal can '
            'participate in parallel aggregation only if it has a serialfunc '
            'function, which must serialize the aggregate state into a bytea '
            'value for transmission to another process. This function must take '
            'a single argument of type internal and return type bytea. A '
            'corresponding deserialfunc is also required.'
        ),
    )
    deserialfunc: str | None = pydantic.Field(
        default=None,
        description=(
            'Deserialize a previously serialized aggregate state back into '
            'state_data_type. This function must take two arguments of types '
            'bytea and internal, and produce a result of type internal. (Note: '
            'the second, internal argument is unused, but is required for type '
            'safety reasons.)'
        ),
    )
    initial_condition: str | None = pydantic.Field(
        default=None,
        description='The initial setting for the state value',
    )
    msfunc: str | None = pydantic.Field(
        default=None,
        description=(
            'The name of the forward state transition function to be called '
            'for each input row in moving-aggregate mode. This is exactly like '
            'the regular transition function, except that its first argument '
            'and result are of type mstate_data_type, which might be different '
            'from state_data_type.'
        ),
    )
    minvfunc: str | None = pydantic.Field(
        default=None,
        description=(
            'The name of the inverse state transition function to be used in '
            'moving-aggregate mode. This function has the same argument and '
            'result types as msfunc, but it is used to remove a value from the '
            'current aggregate state, rather than add a value to it. The inverse '
            'transition function must have the same strictness attribute as the '
            'forward state transition function.'
        ),
    )
    mstate_data_type: str | None = pydantic.Field(
        default=None,
        description=(
            "The data type for the aggregate's state value, when using "
            'moving-aggregate mode'
        ),
    )
    mstate_data_size: int | None = pydantic.Field(
        default=None,
        description=(
            "The approximate average size (in bytes) of the aggregate's state "
            'value, when using moving-aggregate mode. This works the same as '
            'state_data_size.'
        ),
    )
    mffunc: str | None = pydantic.Field(
        default=None,
        description=(
            "The name of the final function called to compute the aggregate's "
            'result after all input rows have been traversed, when using '
            'moving-aggregate mode'
        ),
    )
    mfinalfunc_extra: bool | None = pydantic.Field(
        default=None,
        description='Include extra dummy arguments',
    )
    mfinalfunc_modify: FinalFuncModify | None = pydantic.Field(
        default=None,
        description=(
            'This option specifies whether the Moving Average final function is '
            'a pure function that does not modify its arguments. READ_ONLY '
            'indicates it does not; the other two values indicate that it may '
            'change the transition state value.'
        ),
    )
    minitial_condition: str | None = pydantic.Field(
        default=None,
        description=(
            'The initial setting for the state value, when using '
            'moving-aggregate mode'
        ),
    )
    sort_operator: str | None = pydantic.Field(
        default=None,
        description=(
            'The associated sort operator for a MIN- or MAX-like aggregate. '
            'This is just an operator name (possibly schema-qualified). The '
            'operator is assumed to have the same input data types as the '
            'aggregate (which must be a single-argument normal aggregate).'
        ),
    )
    parallel: ParallelSafety | None = pydantic.Field(
        default=None,
        description=(
            'An aggregate will not be considered for parallelization if it is '
            'marked PARALLEL UNSAFE (which is the default!) or PARALLEL RESTRICTED. '
            "Note that the parallel-safety markings of the aggregate's support "
            'functions are not consulted by the planner, only the marking of the '
            'aggregate itself.'
        ),
    )
    hypothetical: bool | None = pydantic.Field(
        default=None,
        description=(
            'For ordered-set aggregates only, this flag specifies that the '
            'aggregate arguments are to be processed according to the requirements '
            'for hypothetical-set aggregates: that is, the last few direct '
            'arguments must match the data types of the aggregated (WITHIN GROUP) '
            'arguments. The HYPOTHETICAL flag has no effect on run-time behavior, '
            'only on parse-time resolution of the data types and collations of the '
            "aggregate's arguments."
        ),
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the aggregate',
    )
    dependencies: Dependencies | None = pydantic.Field(
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
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/aggregate.html',
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
    def validate_sql_or_components(self) -> Aggregate:
        """Validate that either sql OR component fields are provided, not both."""
        has_sql = self.sql is not None

        component_fields = [
            'arguments',
            'sfunc',
            'state_data_type',
            'state_data_size',
            'ffunc',
            'finalfunc_extra',
            'finalfunc_modify',
            'combinefunc',
            'serialfunc',
            'deserialfunc',
            'initial_condition',
            'msfunc',
            'minvfunc',
            'mstate_data_type',
            'mstate_data_size',
            'mffunc',
            'mfinalfunc_extra',
            'mfinalfunc_modify',
            'minitial_condition',
            'sort_operator',
            'parallel',
            'hypothetical',
        ]

        has_components = any(
            getattr(self, field) is not None for field in component_fields
        )

        if has_sql and has_components:
            raise ValueError(
                'Cannot specify both sql and component fields '
                '(arguments, sfunc, state_data_type, etc.)'
            )

        if has_sql:
            return self

        # If not using SQL, require the essential component fields
        if (
            self.arguments is None
            or self.sfunc is None
            or self.state_data_type is None
        ):
            raise ValueError(
                'When not using sql, must specify arguments, sfunc, and state_data_type'
            )

        return self
