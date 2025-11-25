"""Pydantic models for PostgreSQL table columns."""

import enum

import pydantic


class SequenceBehavior(enum.StrEnum):
    """Sequence behavior for generated columns."""

    ALWAYS = 'ALWAYS'
    BY_DEFAULT = 'BY DEFAULT'


class GeneratedColumn(pydantic.BaseModel):
    """Options for specifying a generated column.

    A generated column can be either computed from an expression or
    generated from a sequence. These two options are mutually exclusive.
    """

    expression: str | None = pydantic.Field(
        default=None,
        description=(
            'The expression used to generate the column. Mutually exclusive '
            'with the sequence column.'
        ),
    )
    sequence: str | None = pydantic.Field(
        default=None,
        description=(
            'Specifies that the generated column value is provided by a '
            'sequence. Mutually exclusive with the expression attribute.'
        ),
    )
    sequence_behavior: SequenceBehavior | None = pydantic.Field(
        default=None,
        description=(
            'The clauses ALWAYS and BY DEFAULT determine how the sequence '
            'value is given precedence over a user-specified value in an '
            'INSERT statement. If ALWAYS is specified, a user-specified value '
            'is only accepted if the INSERT statement specifies OVERRIDING '
            'SYSTEM VALUE. If BY DEFAULT is specified, then the user-specified '
            'value takes precedence.'
        ),
    )

    model_config = {'extra': 'forbid'}

    @pydantic.model_validator(mode='after')
    def validate_generated_column(self) -> 'GeneratedColumn':
        """Validate that expression OR sequence is specified, not both."""
        has_expression = self.expression is not None
        has_sequence = self.sequence is not None
        has_sequence_behavior = self.sequence_behavior is not None

        if has_expression and (has_sequence or has_sequence_behavior):
            raise ValueError(
                'Cannot specify sequence or sequence_behavior when using expression'
            )

        if has_sequence and has_expression:
            raise ValueError('Cannot specify both expression and sequence')

        if not has_expression and not has_sequence:
            raise ValueError('Must specify either expression or sequence')

        return self


class Column(pydantic.BaseModel):
    """Represents a PostgreSQL table column.

    A column defines a field in a table with a specific data type,
    nullability, default value, and optional constraints.
    """

    name: str = pydantic.Field(
        description='The column name',
    )
    data_type: str = pydantic.Field(
        description='The column data type',
    )
    nullable: bool = pydantic.Field(
        default=True,
        description='Column is NULLABLE when True. Defaults to True.',
    )
    default: bool | int | float | str | None = pydantic.Field(
        default=None,
        description='Default value for the column',
    )
    collation: str | None = pydantic.Field(
        default=None,
        description=(
            'Assigns a collation to the column (which must be of a collatable '
            "data type). If not specified, the column data type's default "
            'collation is used.'
        ),
    )
    check_constraint: str | None = pydantic.Field(
        default=None,
        description=(
            'Specifies an expression producing a Boolean result which new or '
            'updated rows must satisfy for an insert or update operation to succeed.'
        ),
    )
    generated: GeneratedColumn | None = pydantic.Field(
        default=None,
        description='Options for specifying a generated column',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the column',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/column.html',
        },
    }
