"""Pydantic models for PostgreSQL operators container."""

from __future__ import annotations

import pydantic

from .operator import Operator


class Operators(pydantic.BaseModel):
    """Represents a container for PostgreSQL operators in a schema.

    Specifies all user-defined operators in a schema.
    """

    schema_: str = pydantic.Field(
        validation_alias='schema',
        serialization_alias='schema',
        description='The schema containing the operators',
    )
    operators: list[Operator] = pydantic.Field(
        description='User-defined operators',
        min_length=1,
    )

    @property
    def schema(self) -> str:
        """Backward-compatible access to schema_ field."""
        return self.schema_

    model_config = {
        'extra': 'forbid',
        'populate_by_name': True,
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/operators.html',
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
