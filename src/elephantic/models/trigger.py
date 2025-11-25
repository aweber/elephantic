"""Pydantic models for PostgreSQL triggers."""

from __future__ import annotations

import enum
import typing

import pydantic


class TriggerWhen(enum.StrEnum):
    """Trigger when enumeration."""

    BEFORE = 'BEFORE'
    AFTER = 'AFTER'
    INSTEAD_OF = 'INSTEAD OF'


class TriggerEvent(enum.StrEnum):
    """Trigger event enumeration."""

    INSERT = 'INSERT'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    TRUNCATE = 'TRUNCATE'


class TriggerForEach(enum.StrEnum):
    """Trigger for each enumeration."""

    ROW = 'ROW'
    STATEMENT = 'STATEMENT'


class Trigger(pydantic.BaseModel):
    """Represents a PostgreSQL trigger.

    Defines a trigger on a table.
    """

    name: str | None = pydantic.Field(
        default=None,
        description='The trigger name',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    when: TriggerWhen | None = pydantic.Field(
        default=None,
        description='When to fire the trigger',
    )
    events: list[TriggerEvent] | None = pydantic.Field(
        default=None,
        description='The events that cause the trigger to fire',
    )
    for_each: TriggerForEach | None = pydantic.Field(
        default=None,
        description='For each row or statement',
    )
    condition: str | None = pydantic.Field(
        default=None,
        description='A Boolean expression that determines whether the trigger function will be executed',
    )
    function: str | None = pydantic.Field(
        default=None,
        description='The trigger function to execute',
    )
    arguments: list[bool | int | float | str] | None = pydantic.Field(
        default=None,
        description='An optional comma-separated list of arguments to be provided to the function',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the trigger',
    )
    dependencies: typing.Any = pydantic.Field(
        default=None,
        description='Database objects this object is dependent upon',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/trigger.html',
        },
    }

    @pydantic.model_validator(mode='after')
    def validate_trigger_definition(self) -> Trigger:
        """Validate trigger definition.

        Either sql OR (name, when, events, function) must be provided.
        """
        has_sql = self.sql is not None
        has_required_fields = all(
            [
                self.name is not None,
                self.when is not None,
                self.events is not None,
                self.function is not None,
            ]
        )

        if has_sql and has_required_fields:
            raise ValueError('Cannot specify both sql and structured fields')

        if has_sql:
            # If using sql, cannot use structured fields
            if any(
                [
                    self.name is not None,
                    self.when is not None,
                    self.for_each is not None,
                    self.condition is not None,
                    self.function is not None,
                    self.arguments is not None,
                ]
            ):
                raise ValueError(
                    'Cannot specify sql with structured fields '
                    '(name, when, for_each, condition, function, arguments)'
                )
            return self

        if not has_required_fields:
            raise ValueError(
                'Must specify either sql OR (name, when, events, and function)'
            )

        return self
