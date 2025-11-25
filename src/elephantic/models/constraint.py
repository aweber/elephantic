"""Pydantic models for PostgreSQL constraints."""

import pydantic


class Constraint(pydantic.BaseModel):
    """Represents a PostgreSQL constraint.

    A minimal constraint definition with just a name field.
    """

    name: str | None = pydantic.Field(
        default=None,
        description='The constraint name',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/constraint.html',
        },
    }
