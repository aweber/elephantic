"""Pydantic models for PostgreSQL user-defined types."""

from __future__ import annotations

import enum
import typing

import pydantic


class TypeForm(enum.StrEnum):
    """Type form enumeration."""

    BASE = 'base'
    COMPOSITE = 'composite'
    ENUM = 'enum'
    RANGE = 'range'


class Alignment(enum.StrEnum):
    """Storage alignment enumeration."""

    CHAR = 'char'
    DOUBLE = 'double'
    INT2 = 'int2'
    INT4 = 'int4'


class Storage(enum.StrEnum):
    """Storage strategy enumeration."""

    PLAIN = 'plain'
    EXTENDED = 'extended'
    EXTERNAL = 'external'
    MAIN = 'main'


class Category(enum.StrEnum):
    """Type category enumeration."""

    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    G = 'G'
    I = 'I'  # noqa: E741 - PostgreSQL category code
    N = 'N'
    P = 'P'
    R = 'R'
    S = 'S'
    T = 'T'
    U = 'U'
    V = 'V'
    X = 'X'


class TypeColumn(pydantic.BaseModel):
    """Column definition for composite types."""

    name: str = pydantic.Field(
        description='The name of an attribute (column) for the composite type',
    )
    data_type: str = pydantic.Field(
        description='The name of an existing data type to become a column of the composite type',
    )
    collation: str | None = pydantic.Field(
        default=None,
        description='The name of an existing collation to use for the column',
    )

    model_config = {'extra': 'forbid'}


class Type(pydantic.BaseModel):
    """Represents a PostgreSQL user-defined type.

    User defined data type. There are five forms of types. They respectively
    create a composite type, an enum type, a range type, a base type, or a
    shell type.
    """

    name: str | None = pydantic.Field(
        default=None,
        description='The name of the type to be created',
    )
    schema_: str | None = pydantic.Field(
        default=None,
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema to create the type in',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role name of the superuser who owns the type',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='User-provided raw SQL snippet',
    )
    type: TypeForm | None = pydantic.Field(
        default=None,
        description='Specifies the form of the type. Defaults to composite',
    )
    # Base type fields
    input: str | None = pydantic.Field(
        default=None,
        description="Function that converts the type's external textual representation to internal",
    )
    output: str | None = pydantic.Field(
        default=None,
        description="Function that converts the type's external binary representation to internal",
    )
    receive: str | None = pydantic.Field(
        default=None,
        description="Optional function to convert the type's external binary representation to internal",
    )
    send: str | None = pydantic.Field(
        default=None,
        description='Optional converts from internal representation to external binary representation',
    )
    typmod_in: str | None = pydantic.Field(
        default=None,
        description='Type modifier input function',
    )
    typmod_out: str | None = pydantic.Field(
        default=None,
        description='Type modifier output function',
    )
    analyze: str | None = pydantic.Field(
        default=None,
        description='Optional function that performs type-specific statistics collection',
    )
    internal_length: int | str | None = pydantic.Field(
        default=None,
        description='Internal length (integer or "VARIABLE")',
    )
    passed_by_value: bool | None = pydantic.Field(
        default=None,
        description='Indicates that values of this data type are passed by value',
    )
    alignment: Alignment | None = pydantic.Field(
        default=None,
        description='Specifies the storage alignment required for the data type',
    )
    storage: Storage | None = pydantic.Field(
        default=None,
        description='Allows selection of storage strategies for variable-length data types',
    )
    like_type: str | None = pydantic.Field(
        default=None,
        description='Copy basic representation properties from an existing type',
    )
    category: Category | None = pydantic.Field(
        default=None,
        description='Used to help control which implicit cast will be applied in ambiguous situations',
    )
    preferred: bool | None = pydantic.Field(
        default=None,
        description='Marks this type as preferred for implicit casts in ambiguous situations',
    )
    default: bool | int | float | str | None = pydantic.Field(
        default=None,
        description='Value to use instead of NULL as a default',
    )
    element: str | None = pydantic.Field(
        default=None,
        description='The type being created is an array; this specifies the type of array elements',
    )
    delimiter: str | None = pydantic.Field(
        default=None,
        description='The delimiter character to be used between values in arrays made of this type',
    )
    collatable: bool | None = pydantic.Field(
        default=None,
        description="This type's operations can use collation information",
    )
    # Composite type fields
    columns: list[TypeColumn] | None = pydantic.Field(
        default=None,
        description='Type columns for composite types',
        min_length=1,
    )
    # Enum type fields
    enum: list[str] | None = pydantic.Field(
        default=None,
        description='A list of quoted labels for enum types',
        min_length=1,
    )
    # Range type fields
    subtype: str | None = pydantic.Field(
        default=None,
        description='The name of the element type that the range type will represent ranges of',
    )
    subtype_opclass: str | None = pydantic.Field(
        default=None,
        description='The name of a b-tree operator class for the subtype',
    )
    collation: str | None = pydantic.Field(
        default=None,
        description='The name of an existing collation to use for the range type',
    )
    canonical: str | None = pydantic.Field(
        default=None,
        description='Function used to convert range values into canonical form',
    )
    subtype_diff: str | None = pydantic.Field(
        default=None,
        description='Function to provide the difference between two values',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the type',
    )
    dependencies: typing.Any = pydantic.Field(
        default=None,
        description='Database objects this object is dependent upon',
    )

    @property
    def schema(self) -> str | None:
        """Backward-compatible access to schema_ field."""
        return self.schema_

    model_config = {
        'extra': 'forbid',
        'populate_by_name': True,
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/type.html',
        },
    }

    @pydantic.model_serializer(mode='wrap')
    def _serialize_model(self, serializer, info):
        """Serialize model using aliases by default."""
        data = serializer(self)
        # Use aliases for all serialization
        if 'schema_' in data:
            data['schema'] = data.pop('schema_')
        return data

    @pydantic.field_validator('internal_length')
    @classmethod
    def validate_internal_length(cls, v: int | str | None) -> int | str | None:
        """Validate that internal_length is an integer or 'VARIABLE'."""
        if v is None:
            return v
        if isinstance(v, str) and v != 'VARIABLE':
            raise ValueError(
                'internal_length must be an integer or "VARIABLE"'
            )
        return v

    @pydantic.field_validator('enum')
    @classmethod
    def validate_enum_values(cls, v: list[str] | None) -> list[str] | None:
        """Validate that enum values are not too long."""
        if v is None:
            return v
        for value in v:
            if len(value) > 64:
                raise ValueError(
                    f'Enum value "{value}" exceeds maximum length of 64 bytes'
                )
        return v

    @pydantic.model_validator(mode='after')
    def validate_type_requirements(self) -> Type:  # noqa: C901
        """Validate that type requirements are met based on type form."""
        has_sql = self.sql is not None
        has_type = self.type is not None

        # Either sql OR type must be specified
        if has_sql and has_type:
            raise ValueError('Cannot specify both sql and type')
        if not has_sql and not has_type:
            raise ValueError('Must specify either sql or type')

        # If using SQL, no structured fields should be provided
        if has_sql:
            return self

        # Validate type-specific requirements
        if self.type == TypeForm.BASE:
            if not self.input or not self.output:
                raise ValueError(
                    'Base type requires input and output functions'
                )
            # Ensure composite/enum/range fields are not set
            if self.columns or self.enum or self.subtype:
                raise ValueError(
                    'Base type cannot have columns, enum, or subtype fields'
                )

        elif self.type == TypeForm.COMPOSITE:
            if not self.columns:
                raise ValueError('Composite type requires columns')
            # Ensure base/enum/range fields are not set
            if any(
                [
                    self.input,
                    self.output,
                    self.receive,
                    self.send,
                    self.enum,
                    self.subtype,
                ]
            ):
                raise ValueError(
                    'Composite type cannot have base type, enum, or range type fields'
                )

        elif self.type == TypeForm.ENUM:
            if not self.enum:
                raise ValueError('Enum type requires enum values')
            # Ensure base/composite/range fields are not set
            if any(
                [
                    self.input,
                    self.output,
                    self.receive,
                    self.send,
                    self.columns,
                    self.subtype,
                ]
            ):
                raise ValueError(
                    'Enum type cannot have base type, composite type, or range type fields'
                )

        elif self.type == TypeForm.RANGE:
            if not self.subtype:
                raise ValueError('Range type requires subtype')
            # Ensure base/composite/enum fields are not set
            if any(
                [
                    self.input,
                    self.output,
                    self.receive,
                    self.send,
                    self.columns,
                    self.enum,
                ]
            ):
                raise ValueError(
                    'Range type cannot have base type, composite type, or enum type fields'
                )

        return self
