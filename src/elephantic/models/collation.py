"""Pydantic models for PostgreSQL collations."""

from __future__ import annotations

import enum

import pydantic

from elephantic.models.dependencies import Dependencies


class LocaleProvider(enum.StrEnum):
    """Locale provider enumeration."""

    ICU = 'icu'
    LIBC = 'libc'


class Collation(pydantic.BaseModel):
    """Represents a PostgreSQL collation.

    A collation specifies locale-based text sorting and comparison rules.
    Collations can be defined using raw SQL, by copying from an existing
    collation, or by specifying locale parameters.
    """

    name: str = pydantic.Field(
        description='The name of the collation to create',
    )
    schema_: str = pydantic.Field(
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema to create the collation in',
    )
    owner: str = pydantic.Field(
        description='The role that owns the collation',
    )
    sql: str | None = pydantic.Field(
        default=None,
        description='Raw SQL for the object',
    )
    locale: str | None = pydantic.Field(
        default=None,
        description=(
            'This is a shortcut for setting lc_collate and lc_ctype at once. '
            'If you specify this, you cannot specify either of those parameters.'
        ),
    )
    lc_collate: str | None = pydantic.Field(
        default=None,
        description=(
            'Use the specified operating system locale for the LC_COLLATE '
            'locale category.'
        ),
    )
    lc_ctype: str | None = pydantic.Field(
        default=None,
        description=(
            'Use the specified operating system locale for the LC_CTYPE '
            'locale category.'
        ),
    )
    provider: LocaleProvider | None = pydantic.Field(
        default=None,
        description=(
            'Specifies the provider to use for locale services associated '
            'with this collation. Possible values are: icu, libc. libc is '
            'the default. The available choices depend on the operating '
            'system and build options.'
        ),
    )
    deterministic: bool = pydantic.Field(
        default=True,
        description='Specifies whether the collation should use deterministic comparisons',
    )
    copy_from: str | None = pydantic.Field(
        default=None,
        description='Copy the collation from a pre-existing collation',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the collation',
    )
    dependencies: Dependencies | None = pydantic.Field(
        default=None,
        description='Database objects this object is dependent upon',
    )

    @property
    def schema(self) -> str:
        """Backward-compatible access to schema_ field."""
        return self.schema_

    model_config = {
        'extra': 'forbid',
        'populate_by_name': True,
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/collation.html',
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

    @pydantic.model_validator(mode='after')
    def validate_collation_definition(self) -> Collation:
        """Validate collation definition.

        Must use one of: sql, copy_from, or locale parameters.
        Various combinations are mutually exclusive.
        """
        has_sql = self.sql is not None
        has_copy_from = self.copy_from is not None
        has_locale = self.locale is not None
        has_lc_collate = self.lc_collate is not None
        has_lc_ctype = self.lc_ctype is not None
        has_provider = self.provider is not None

        locale_params = [
            has_locale,
            has_lc_collate,
            has_lc_ctype,
            has_provider,
        ]

        # If using sql, cannot use copy_from or any locale parameters
        if has_sql:
            if has_copy_from:
                raise ValueError('Cannot specify both sql and copy_from')
            if any(locale_params):
                raise ValueError(
                    'Cannot specify locale parameters when using sql'
                )
            return self

        # If using copy_from, cannot use sql or any locale parameters
        if has_copy_from:
            if has_sql:
                raise ValueError('Cannot specify both copy_from and sql')
            if any(locale_params):
                raise ValueError(
                    'Cannot specify locale parameters when using copy_from'
                )
            return self

        # If locale is specified, cannot specify lc_collate or lc_ctype
        if has_locale:
            if has_lc_collate or has_lc_ctype:
                raise ValueError(
                    'Cannot specify lc_collate or lc_ctype when using locale shortcut'
                )

        # If not using sql or copy_from, must have at least one locale parameter
        if not has_sql and not has_copy_from:
            if not any(locale_params):
                raise ValueError(
                    'Must specify either sql, copy_from, or at least one locale parameter'
                )

        return self
