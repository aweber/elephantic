"""Pydantic models for PostgreSQL subscriptions."""

from __future__ import annotations

import enum

import pydantic


class SynchronousCommit(enum.StrEnum):
    """Synchronous commit enumeration."""

    ON = 'on'
    REMOTE_APPLY = 'remote_apply'
    REMOTE_WRITE = 'remote_write'
    LOCAL = 'local'
    OFF = 'off'


class SubscriptionParameters(pydantic.BaseModel):
    """Subscription parameters."""

    copy_data: bool | None = pydantic.Field(
        default=None,
        description='Specifies whether existing data should be copied once replication starts',
    )
    create_slot: bool | None = pydantic.Field(
        default=None,
        description='Specifies whether the command should create the replication slot on the publisher',
    )
    enabled: bool | None = pydantic.Field(
        default=None,
        description='Specifies whether the subscription should be actively replicating',
    )
    slot_name: str | None = pydantic.Field(
        default=None,
        description='Name of the replication slot to use',
    )
    synchronous_commit: SynchronousCommit | None = pydantic.Field(
        default=None,
        description='The value of this parameter overrides the synchronous_commit setting',
    )
    connect: bool | None = pydantic.Field(
        default=None,
        description='Specifies whether the subscription should connect to the publisher at all',
    )

    model_config = {'extra': 'forbid'}


class Subscription(pydantic.BaseModel):
    """Represents a PostgreSQL subscription.

    The subscription represents a replication connection to the publisher.
    """

    name: str = pydantic.Field(
        description='The name of the subscription to create',
    )
    connection: str = pydantic.Field(
        description='The connection string to the publisher',
    )
    publications: list[str] = pydantic.Field(
        description='Publications to subscribe to on the publisher',
        min_length=1,
    )
    parameters: SubscriptionParameters | None = pydantic.Field(
        default=None,
        description='Subscription parameters',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the subscription',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/subscription.html',
        },
    }
