"""Pydantic models for PostgreSQL user-defined types collection."""

from __future__ import annotations

import pydantic

from .type import Type


class Types(pydantic.BaseModel):
    """Represents all user-defined types in a schema.

    Specifies all user-defined types in a schema.
    """

    schema_: str = pydantic.Field(
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema containing the types',
    )
    types: list[Type] = pydantic.Field(
        description='User-defined types',
    )

    @property
    def schema(self) -> str:
        """Backward-compatible access to schema_ field."""
        return self.schema_

    model_config = {
        'extra': 'forbid',
        'populate_by_name': True,
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/types.html',
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
