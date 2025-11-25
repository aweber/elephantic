"""Pydantic models for PostgreSQL event triggers."""

from __future__ import annotations

import enum
import typing

import pydantic


class Event(enum.StrEnum):
    """Event trigger event types."""

    DDL_COMMAND_START = 'ddl_command_start'
    DDL_COMMAND_END = 'ddl_command_end'
    TABLE_REWRITE = 'table_rewrite'
    SQL_DROP = 'sql_drop'


class Filter(pydantic.BaseModel):
    """Filter for event trigger."""

    tags: list[str] = pydantic.Field(
        description='A list of tag values to filter on (e.g. DROP FUNCTION)',
    )

    model_config = {'extra': 'forbid'}


class EventTrigger(pydantic.BaseModel):
    """Represents a PostgreSQL event trigger.

    Event triggers fire in response to database-level events.
    """

    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    name: str | None = pydantic.Field(
        default=None,
        description='The event trigger name',
    )
    event: Event | None = pydantic.Field(
        default=None,
        description='The event that causes the trigger to fire',
    )
    filter: Filter | None = pydantic.Field(
        default=None,
        description=(
            'The name of a variable used to filter events. This makes it possible to '
            'restrict the firing of the trigger to a subset of the cases in which it '
            'is supported'
        ),
    )
    function: str | None = pydantic.Field(
        default=None,
        description='The trigger function to execute',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the event trigger',
    )
    dependencies: typing.Any = pydantic.Field(
        default=None,
        description='Database objects this object is dependent upon',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/event_trigger.html',
        },
    }

    @pydantic.model_validator(mode='after')
    def validate_sql_or_structured(self) -> EventTrigger:
        """Validate that either sql OR structured fields are provided, not both."""
        has_sql = self.sql is not None
        has_structured = any(
            [
                self.name is not None,
                self.event is not None,
                self.filter is not None,
                self.function is not None,
            ]
        )

        if has_sql and has_structured:
            raise ValueError(
                'Cannot specify sql with structured fields (name, event, filter, function)'
            )

        if has_sql:
            return self

        # If not using SQL, name, event, and function are required
        if not self.name or not self.event or not self.function:
            raise ValueError(
                'Must specify either sql or all of: name, event, and function'
            )

        return self
