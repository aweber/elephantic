"""PostgreSQL Access Control Lists (ACLs) models."""

import enum
import re

import pydantic
from pydantic import ConfigDict


class ColumnPrivilege(str, enum.Enum):
    """Column-level privileges."""

    SELECT = 'SELECT'
    INSERT = 'INSERT'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    ALL = 'ALL'


class DatabasePrivilege(str, enum.Enum):
    """Database-level privileges."""

    CREATE = 'CREATE'
    CONNECT = 'CONNECT'
    TEMP = 'TEMP'
    TEMPORARY = 'TEMPORARY'
    ALL = 'ALL'


class UsagePrivilege(str, enum.Enum):
    """USAGE privilege."""

    USAGE = 'USAGE'
    ALL = 'ALL'


class ExecutePrivilege(str, enum.Enum):
    """EXECUTE privilege for functions."""

    EXECUTE = 'EXECUTE'
    ALL = 'ALL'


class LargeObjectPrivilege(str, enum.Enum):
    """Large object privileges."""

    SELECT = 'SELECT'
    UPDATE = 'UPDATE'
    ALL = 'ALL'


class SchemaPrivilege(str, enum.Enum):
    """Schema-level privileges."""

    CREATE = 'CREATE'
    USAGE = 'USAGE'
    ALL = 'ALL'


class SequencePrivilege(str, enum.Enum):
    """Sequence privileges."""

    SELECT = 'SELECT'
    UPDATE = 'UPDATE'
    USAGE = 'USAGE'
    ALL = 'ALL'


class TablePrivilege(str, enum.Enum):
    """Table-level privileges."""

    SELECT = 'SELECT'
    INSERT = 'INSERT'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    ALL = 'ALL'


class ViewPrivilege(str, enum.Enum):
    """View privileges."""

    SELECT = 'SELECT'
    ALL = 'ALL'


class ACLs(pydantic.BaseModel):
    """
    Access Control Lists for PostgreSQL database objects.

    Defines permissions for various database objects including tables, columns,
    functions, schemas, and other database resources.
    """

    columns: dict[str, list[ColumnPrivilege]] | None = pydantic.Field(
        default=None,
        description='Column-level privileges in format schema.table.column',
    )
    databases: dict[str, list[DatabasePrivilege]] | None = pydantic.Field(
        default=None, description='Database-level privileges'
    )
    domains: dict[str, list[UsagePrivilege]] | None = pydantic.Field(
        default=None,
        description='Domain privileges in format schema.domain',
    )
    foreign_data_wrappers: dict[str, list[UsagePrivilege]] | None = (
        pydantic.Field(
            default=None, description='Foreign data wrapper privileges'
        )
    )
    foreign_servers: dict[str, list[UsagePrivilege]] | None = pydantic.Field(
        default=None, description='Foreign server privileges'
    )
    functions: dict[str, list[ExecutePrivilege]] | None = pydantic.Field(
        default=None,
        description='Function privileges in format schema.function(args)',
    )
    groups: list[str] | None = pydantic.Field(
        default=None, description='List of groups'
    )
    languages: dict[str, list[UsagePrivilege]] | None = pydantic.Field(
        default=None, description='Language privileges'
    )
    large_objects: dict[str, list[LargeObjectPrivilege]] | None = (
        pydantic.Field(
            default=None, description='Large object privileges by OID'
        )
    )
    roles: list[str] | None = pydantic.Field(
        default=None, description='List of roles'
    )
    schemata: dict[str, list[SchemaPrivilege]] | None = pydantic.Field(
        default=None, description='Schema privileges'
    )
    sequences: dict[str, list[SequencePrivilege]] | None = pydantic.Field(
        default=None,
        description='Sequence privileges in format schema.sequence',
    )
    tables: dict[str, list[TablePrivilege]] | None = pydantic.Field(
        default=None, description='Table privileges in format schema.table'
    )
    tablespaces: dict[str, list[SchemaPrivilege]] | None = pydantic.Field(
        default=None, description='Tablespace privileges'
    )
    types: dict[str, list[UsagePrivilege]] | None = pydantic.Field(
        default=None, description='Type privileges in format schema.type'
    )
    views: dict[str, list[ViewPrivilege]] | None = pydantic.Field(
        default=None, description='View privileges in format schema.view'
    )

    model_config = ConfigDict(extra='forbid')

    @pydantic.field_validator('columns')
    @classmethod
    def validate_column_pattern(
        cls, v: dict[str, list[ColumnPrivilege]] | None
    ) -> dict[str, list[ColumnPrivilege]] | None:
        """Validate column names follow schema.table.column pattern."""
        if v is None:
            return v
        pattern = re.compile(
            r'^([A-Za-z0-9_\-]+)\.([A-Za-z0-9_\-]+)\.([A-Za-z0-9_\-]+)$'
        )
        for key in v:
            if not pattern.match(key):
                msg = (
                    f'Column key "{key}" must match pattern '
                    'schema.table.column'
                )
                raise ValueError(msg)
        return v

    @pydantic.field_validator(
        'domains', 'sequences', 'tables', 'types', 'views'
    )
    @classmethod
    def validate_schema_object_pattern(
        cls, v: dict[str, list] | None
    ) -> dict[str, list] | None:
        """Validate object names follow schema.object pattern."""
        if v is None:
            return v
        pattern = re.compile(r'^([A-Za-z0-9_\-]+)\.([A-Za-z0-9_\-]+)$')
        for key in v:
            if not pattern.match(key):
                raise ValueError(
                    f'Object key "{key}" must match pattern schema.object'
                )
        return v

    @pydantic.field_validator('functions')
    @classmethod
    def validate_function_pattern(
        cls, v: dict[str, list[ExecutePrivilege]] | None
    ) -> dict[str, list[ExecutePrivilege]] | None:
        """Validate function names follow schema.function(args) pattern."""
        if v is None:
            return v
        pattern = re.compile(r'^([A-Za-z0-9_\-]+)\.([A-Za-z0-9_\-]+)\((.*)\)$')
        for key in v:
            if not pattern.match(key):
                raise ValueError(
                    f'Function key "{key}" must match pattern '
                    'schema.function(args)'
                )
        return v

    @pydantic.field_validator('large_objects')
    @classmethod
    def validate_large_object_pattern(
        cls, v: dict[str, list[LargeObjectPrivilege]] | None
    ) -> dict[str, list[LargeObjectPrivilege]] | None:
        """Validate large object OIDs are numeric."""
        if v is None:
            return v
        pattern = re.compile(r'^[0-9]+$')
        for key in v:
            if not pattern.match(key):
                raise ValueError(
                    f'Large object key "{key}" must be numeric OID'
                )
        return v

    @pydantic.field_validator('groups', 'roles')
    @classmethod
    def validate_unique_items(cls, v: list[str] | None) -> list[str] | None:
        """Validate list items are unique."""
        if v is None:
            return v
        if len(v) != len(set(v)):
            raise ValueError('List must contain unique items')
        return v
