"""Pydantic models for PostgreSQL tablespaces."""

from __future__ import annotations

import pydantic


class Tablespace(pydantic.BaseModel):
    """Represents a PostgreSQL tablespace.

    A tablespace allows superusers to define an alternative location on the file
    system where the data files containing database objects (such as tables and
    indexes) can reside.
    """

    name: str = pydantic.Field(
        description='The name of the tablespace to create',
    )
    owner: str | None = pydantic.Field(
        default=None,
        description='The role that owns the tablespace',
    )
    location: str = pydantic.Field(
        description=(
            'The directory that will be used for the tablespace. The directory must '
            'exist (CREATE TABLESPACE will not create it), should be empty, and must '
            'be owned by the PostgreSQL system user. The directory must be specified '
            'by an absolute path name'
        ),
    )
    options: list[dict[str, float]] | None = pydantic.Field(
        default=None,
        description='Tablespace options',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the tablespace',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/tablespace.html',
        },
    }

    @pydantic.field_validator('options')
    @classmethod
    def validate_option_names(
        cls, v: list[dict[str, float]] | None
    ) -> list[dict[str, float]] | None:
        """Validate that option names match the required pattern."""
        import re

        if v is None:
            return v
        pattern = re.compile(
            r'^(seq_page_cost|random_page_cost|effective_io_concurrency)$'
        )
        for option in v:
            for key in option.keys():
                if not pattern.match(key):
                    raise ValueError(
                        f'Option name "{key}" does not match required pattern. '
                        f'Must be one of: seq_page_cost, random_page_cost, '
                        f'effective_io_concurrency'
                    )
        return v
