"""Pydantic models for PostgreSQL users."""

import datetime
import enum

import pydantic

from elephantic.models import acls


class Environment(enum.StrEnum):
    """Environment enumeration."""

    DEVELOPMENT = 'DEVELOPMENT'
    STAGING = 'STAGING'
    TESTING = 'TESTING'
    PRODUCTION = 'PRODUCTION'


class UserOptions(pydantic.BaseModel):
    """Options for a PostgreSQL user."""

    bypass_rls: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether the user may bypass every row-level security (RLS) policy'
        ),
    )
    connection_limit: int = pydantic.Field(
        default=-1,
        description=(
            'How many concurrent connections the user can make. -1 (the default) '
            'means no limit.'
        ),
    )
    create_db: bool = pydantic.Field(
        default=False,
        description='Determines if the user is allowed to create databases',
    )
    create_role: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether the user will be permitted to create a new group, '
            'role or user'
        ),
    )
    inherit: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether the user inherits the privileges of groups it is '
            'a member of and roles it is granted'
        ),
    )
    replication: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether a user is allowed to initiate streaming '
            'replication or put the system in and out of backup mode'
        ),
    )
    superuser: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether the user role is a superuser, who can override '
            'all access restrictions within the database'
        ),
    )

    model_config = {'extra': 'forbid'}


class User(pydantic.BaseModel):
    """Represents a PostgreSQL user.

    A user is a role that is permitted to login to the database.
    """

    name: str | None = pydantic.Field(
        default=None,
        description='The user name',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the user',
    )
    environments: list[Environment] | None = pydantic.Field(
        default=None,
        description=(
            'Used to limit the environments the user is created in. '
            'The default value is all environments.'
        ),
    )
    password: str | None = pydantic.Field(
        default=None,
        description='The password that is used to authenticate the user upon login',
    )
    valid_until: datetime.datetime | None = pydantic.Field(
        default=None,
        description=(
            "Sets a date and time after which the user's password is no longer valid"
        ),
    )
    grants: acls.ACLs | None = pydantic.Field(
        default=None,
        description='ACLs to add to the user',
    )
    revocations: acls.ACLs | None = pydantic.Field(
        default=None,
        description='ACLs to remove from the user',
    )
    options: UserOptions | None = pydantic.Field(
        default=None,
        description='User options',
    )
    settings: list[dict[str, str | int | float | bool]] | None = (
        pydantic.Field(
            default=None,
            description='User-specific configuration settings',
        )
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/user.html',
        },
    }

    @pydantic.field_validator('environments')
    @classmethod
    def validate_unique_environments(
        cls, v: list[Environment] | None
    ) -> list[Environment] | None:
        """Validate that environments are unique."""
        if v is not None and len(v) != len(set(v)):
            raise ValueError('Environment values must be unique')
        return v

    @pydantic.field_validator('settings')
    @classmethod
    def validate_setting_names(
        cls, v: list[dict[str, str | int | float | bool]] | None
    ) -> list[dict[str, str | int | float | bool]] | None:
        """Validate that setting names match the required pattern."""
        import re

        if v is None:
            return v
        pattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_\.]*$')
        for setting in v:
            for key in setting.keys():
                if not pattern.match(key):
                    raise ValueError(
                        f'Setting name "{key}" does not match required pattern: '
                        f'^[A-Za-z_][A-Za-z0-9_\\.]*$'
                    )
        return v
