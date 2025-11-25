"""Pydantic models for function/aggregate arguments."""

import enum

import pydantic


class ArgumentMode(enum.StrEnum):
    """Argument mode enumeration."""

    IN = 'IN'
    VARIADIC = 'VARIADIC'


class Argument(pydantic.BaseModel):
    """Represents a function or aggregate argument.

    An argument defines the input parameters for functions and aggregates,
    including the data type and optionally the argument name and mode.
    """

    mode: ArgumentMode = pydantic.Field(
        default=ArgumentMode.IN,
        description='The mode of the argument',
    )
    name: str | None = pydantic.Field(
        default=None,
        description='The name of the function argument',
    )
    data_type: str = pydantic.Field(
        description=(
            'An input data type on which this aggregate function operates. '
            'To create a zero-argument aggregate function, write * in place '
            'of the list of argument specifications.'
        ),
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/argument.html',
        },
    }
