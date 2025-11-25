"""Pydantic models for PostgreSQL foreign keys."""

from __future__ import annotations

import enum

import pydantic


class MatchType(enum.StrEnum):
    """Match type enumeration."""

    FULL = 'FULL'
    PARTIAL = 'PARTIAL'
    SIMPLE = 'SIMPLE'


class ReferentialAction(enum.StrEnum):
    """Referential action enumeration."""

    NO_ACTION = 'NO ACTION'
    RESTRICT = 'RESTRICT'
    CASCADE = 'CASCADE'
    SET_NULL = 'SET NULL'
    SET_DEFAULT = 'SET DEFAULT'


class ForeignKeyReference(pydantic.BaseModel):
    """Foreign key reference definition."""

    name: str = pydantic.Field(
        description='The name of the foreign key table',
    )
    columns: list[str] = pydantic.Field(
        description='The columns in the table in the foreign key table',
        min_length=1,
    )

    model_config = {'extra': 'forbid'}


class ForeignKey(pydantic.BaseModel):
    """Represents a PostgreSQL foreign key constraint.

    Defines a foreign key on a table.
    """

    name: str | None = pydantic.Field(
        default=None,
        description='The foreign key name',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    columns: list[str] | None = pydantic.Field(
        default=None,
        description='The columns in the table that the foreign key enforces the value of',
        min_length=1,
    )
    references: ForeignKeyReference | None = pydantic.Field(
        default=None,
        description='Defines the information about the foreign key table and columns',
    )
    match_type: MatchType | None = pydantic.Field(
        default=None,
        description='Match type for the foreign key',
    )
    on_delete: ReferentialAction | None = pydantic.Field(
        default=None,
        description='Action to take on delete of the column value in the referenced table',
    )
    on_update: ReferentialAction | None = pydantic.Field(
        default=None,
        description='Action to take on update of the column value in the referenced table',
    )
    deferrable: bool | None = pydantic.Field(
        default=None,
        description='Controls whether the constraint can be deferred',
    )
    initially_deferred: bool | None = pydantic.Field(
        default=None,
        description='Initial constraint check behavior',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/foreign_key.html',
        },
    }

    @pydantic.model_validator(mode='after')
    def validate_foreign_key_definition(self) -> ForeignKey:
        """Validate foreign key definition.

        Either sql OR columns must be provided.
        """
        has_sql = self.sql is not None
        has_columns = self.columns is not None

        if has_sql and has_columns:
            raise ValueError('Cannot specify both sql and columns')

        if has_sql:
            # If using sql, cannot use structured fields
            if any(
                [
                    self.references is not None,
                    self.on_delete is not None,
                    self.on_update is not None,
                    self.deferrable is not None,
                    self.initially_deferred is not None,
                ]
            ):
                raise ValueError(
                    'Cannot specify sql with structured fields '
                    '(references, on_delete, on_update, deferrable, initially_deferred)'
                )
            return self

        if not has_columns:
            raise ValueError('Must specify either sql or columns')

        return self
