"""Pydantic models for PostgreSQL foreign servers."""

from __future__ import annotations

import typing

import pydantic


class Server(pydantic.BaseModel):
    """Represents a PostgreSQL foreign server.

    A foreign server typically encapsulates connection information that a
    foreign-data wrapper uses to access an external data resource.
    """

    name: str = pydantic.Field(
        description='The name of the server to be created',
    )
    foreign_data_wrapper: str = pydantic.Field(
        description='The name of the foreign-data wrapper that manages the server',
    )
    type: str | None = pydantic.Field(
        default=None,
        description='Optional server type, potentially useful to foreign-data wrappers',
    )
    version: str | None = pydantic.Field(
        default=None,
        description='Optional server version, potentially useful to foreign-data wrappers',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the server',
    )
    options: dict[str, str | int | float | bool] | None = pydantic.Field(
        default=None,
        description=(
            'This clause specifies the options for the server. The options typically '
            'define the connection details of the server, but the actual names and '
            "values are dependent on the server's foreign-data wrapper"
        ),
    )
    dependencies: typing.Any = pydantic.Field(
        description='Database objects this object is dependent upon',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/server.html',
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
