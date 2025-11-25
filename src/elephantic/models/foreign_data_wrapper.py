"""Pydantic models for PostgreSQL foreign data wrappers."""

from __future__ import annotations

import pydantic


class ForeignDataWrapper(pydantic.BaseModel):
    """Represents a PostgreSQL foreign data wrapper.

    Foreign Data Wrappers provide a standardized way of handling access to remote
    data stores.
    """

    name: str | None = pydantic.Field(
        default=None,
        description='The name of the foreign data wrapper to be created',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role name of the superuser who owns the Foreign Data Wrapper',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the Foreign Data Wrapper',
    )
    handler: str | None = pydantic.Field(
        default=None,
        description=(
            'The name of a previously registered function that will be called to '
            'retrieve the execution functions for foreign tables. The handler function '
            'must take no arguments, and its return type must be fdw_handler'
        ),
    )
    validator: str | None = pydantic.Field(
        default=None,
        description=(
            'The name of a previously registered function that will be called to check '
            'the generic options given to the foreign-data wrapper'
        ),
    )
    options: dict[str, str | int | float | bool] | None = pydantic.Field(
        default=None,
        description=(
            'This clause specifies options for the new foreign-data wrapper. The '
            'allowed option names and values are specific to each foreign data wrapper '
            "and are validated using the foreign-data wrapper's validator function"
        ),
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/foreign_data_wrapper.html',
        },
    }

    @pydantic.field_validator('options')
    @classmethod
    def validate_option_names(
        cls, v: dict[str, str | int | float | bool] | None
    ) -> dict[str, str | int | float | bool] | None:
        """Validate that option names match the required pattern."""
        import re

        if v is None:
            return v
        pattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_\.]*$')
        for key in v.keys():
            if not pattern.match(key):
                raise ValueError(
                    f'Option name "{key}" does not match required pattern: '
                    f'^[A-Za-z_][A-Za-z0-9_\\.]*$'
                )
        return v
