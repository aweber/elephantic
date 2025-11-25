"""Pydantic models for PostgreSQL user mappings."""

from __future__ import annotations

import pydantic


class ServerMapping(pydantic.BaseModel):
    """Server mapping configuration for a user."""

    name: str = pydantic.Field(
        description='The name of an existing server for which the user mapping is to be created',
    )
    options: dict[str, str | int | float | bool] | None = pydantic.Field(
        default=None,
        description=(
            'This clause specifies the options of the user mapping. The options '
            'typically define the actual user name and password of the mapping. Option '
            'names must be unique. The allowed option names and values are specific to '
            "the server's foreign-data wrapper"
        ),
    )

    model_config = {'extra': 'forbid'}

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


class UserMapping(pydantic.BaseModel):
    """Represents a PostgreSQL user mapping.

    A user mapping typically encapsulates connection information that a
    foreign-data wrapper uses together with the information encapsulated by a
    foreign server to access an external data resource.
    """

    name: str = pydantic.Field(
        description='The name of a local role that is mapped to foreign server',
    )
    servers: list[ServerMapping] = pydantic.Field(
        description='Array of server and options for the user',
        min_length=1,
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/user_mapping.html',
        },
    }
