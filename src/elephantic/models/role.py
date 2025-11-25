"""Pydantic models for PostgreSQL roles."""

import enum

import pydantic

from elephantic.models import acls


class Environment(enum.StrEnum):
    """Environment enumeration."""

    DEVELOPMENT = 'DEVELOPMENT'
    STAGING = 'STAGING'
    TESTING = 'TESTING'
    PRODUCTION = 'PRODUCTION'


class RoleOptions(pydantic.BaseModel):
    """Options for a PostgreSQL role."""

    bypass_rls: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether a role bypasses every row-level security (RLS) policy'
        ),
    )
    connection_limit: int = pydantic.Field(
        default=-1,
        description=(
            'If role can log in, this specifies how many concurrent connections '
            'the role can make. -1 (the default) means no limit.'
        ),
    )
    create_db: bool = pydantic.Field(
        default=False,
        description='Determines if the role is allowed to create databases',
    )
    create_role: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether a role will be permitted to create a new group, '
            'role or user'
        ),
    )
    inherit: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether a role inherits the privileges of roles it is '
            'a member of'
        ),
    )
    login: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether a role is allowed to log in; that is, whether '
            'the role can be given as the initial session authorization name '
            'during client connection'
        ),
    )
    replication: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether a role is allowed to initiate streaming '
            'replication or put the system in and out of backup mode'
        ),
    )
    superuser: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether the new role is a superuser, who can override '
            'all access restrictions within the database'
        ),
    )

    model_config = {'extra': 'forbid'}


class Role(pydantic.BaseModel):
    """Represents a PostgreSQL role.

    A role is an entity that can own database objects and have database
    privileges. Roles can have the ability to log in (users) or can be
    used to group permissions (groups).
    """

    name: str | None = pydantic.Field(
        default=None,
        description='The role name',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the role',
    )
    create: bool = pydantic.Field(
        default=True,
        description=(
            'Used in special cases where a role should be defined, but not '
            'created, such as "PUBLIC"'
        ),
    )
    environments: list[Environment] | None = pydantic.Field(
        default=None,
        description=(
            'Used to limit the environments the role is created in. '
            'The default value is all environments.'
        ),
    )
    grants: acls.ACLs | None = pydantic.Field(
        default=None,
        description='ACLs to add to the role',
    )
    revocations: acls.ACLs | None = pydantic.Field(
        default=None,
        description='ACLs to remove from the role',
    )
    options: RoleOptions | None = pydantic.Field(
        default=None,
        description='Role options',
    )
    settings: list[dict[str, str | int | float | bool]] | None = (
        pydantic.Field(
            default=None,
            description='Role-specific configuration settings',
        )
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/role.html',
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
