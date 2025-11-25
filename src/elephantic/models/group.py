"""Pydantic models for PostgreSQL groups."""

import enum

import pydantic

from elephantic.models import acls


class Environment(enum.StrEnum):
    """Environment enumeration."""

    DEVELOPMENT = 'DEVELOPMENT'
    STAGING = 'STAGING'
    TESTING = 'TESTING'
    PRODUCTION = 'PRODUCTION'


class GroupOptions(pydantic.BaseModel):
    """Options for a PostgreSQL group."""

    create_db: bool = pydantic.Field(
        default=False,
        description='Determines if members of a group are allowed to create databases',
    )
    create_role: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether members of a group will be permitted to '
            'create a new group, role or user'
        ),
    )
    inherit: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether the group inherits the privileges of any '
            'roles that are granted to it'
        ),
    )
    replication: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether members of the group are allowed to initiate '
            'streaming replication or put the system in and out of backup mode'
        ),
    )
    superuser: bool = pydantic.Field(
        default=False,
        description=(
            'Determines whether members of a group are superusers, who can '
            'override all access restrictions within the database'
        ),
    )

    model_config = {'extra': 'forbid'}


class Group(pydantic.BaseModel):
    """Represents a PostgreSQL group.

    A group is a type of role that defines permissions for one or more users.
    Groups do not have login capability.
    """

    name: str | None = pydantic.Field(
        default=None,
        description='The group name',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the group',
    )
    environments: list[Environment] | None = pydantic.Field(
        default=None,
        description=(
            'Used to limit the environments the group is created in. '
            'The default value is all environments.'
        ),
    )
    grants: acls.ACLs | None = pydantic.Field(
        default=None,
        description='ACLs to add to the group',
    )
    revocations: acls.ACLs | None = pydantic.Field(
        default=None,
        description='ACLs to remove from the group',
    )
    options: GroupOptions | None = pydantic.Field(
        default=None,
        description='Group options',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/group.html',
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
