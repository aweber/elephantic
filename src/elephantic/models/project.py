"""Pydantic models for PostgreSQL project."""

from __future__ import annotations

import pydantic

from .foreign_data_wrapper import ForeignDataWrapper


class Extension(pydantic.BaseModel):
    """PostgreSQL extension configuration."""

    name: str = pydantic.Field(
        description=(
            'The name of the extension to be installed. PostgreSQL will create the '
            'extension using details from the file SHAREDIR/extension/extension_name.control.'
        ),
    )
    schema_: str | None = pydantic.Field(
        default=None,
        validation_alias='schema',
        serialization_alias='schema',
        description=(
            "The name of the schema in which to install the extension's objects, "
            'given that the extension allows its contents to be relocated.'
        ),
    )
    version: str | None = pydantic.Field(
        default=None,
        description=(
            'The version of the extension to install. This can be written as either an '
            'identifier or a string literal. The default version is whatever is '
            "specified in the extension's control file."
        ),
    )
    cascade: bool | None = pydantic.Field(
        default=None,
        description=(
            'Automatically install any extensions that this extension depends on '
            'that are not already installed.'
        ),
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the extension',
    )

    @property
    def schema(self) -> str | None:
        """Backward-compatible access to schema_ field."""
        return self.schema_

    model_config = {'extra': 'forbid', 'populate_by_name': True}

    @pydantic.model_serializer(mode='wrap')
    def _serialize_model(self, serializer, info):
        """Serialize model using aliases by default."""
        data = serializer(self)
        # Use aliases for all serialization
        if 'schema_' in data:
            data['schema'] = data.pop('schema_')
        return data


class Language(pydantic.BaseModel):
    """Procedural language configuration."""

    name: str = pydantic.Field(
        description='The name of the language to load',
    )
    comment: str | None = pydantic.Field(
        default=None,
        description='An optional comment about the language',
    )
    trusted: bool | None = pydantic.Field(
        default=None,
        description=(
            'Specifies if the language grants access to data that the user would not '
            'otherwise have access to.'
        ),
    )
    replace: bool | None = pydantic.Field(
        default=None,
        description='Use CREATE or REPLACE syntax',
    )
    handler: str | None = pydantic.Field(
        default=None,
        description=(
            'Specifies the name of a previously registered function that will '
            "be called to execute the procedural language's functions."
        ),
    )
    inline_handler: str | None = pydantic.Field(
        default=None,
        description=(
            'Specifies the name of a previously registered function that will be '
            'called to execute an anonymous code block (DO command) in this language.'
        ),
    )
    validator: str | None = pydantic.Field(
        default=None,
        description=(
            'Specifies the name of a previously registered function that will '
            'be called when a new function in the language is created, to validate '
            'the new function.'
        ),
    )

    model_config = {'extra': 'forbid'}


class Project(pydantic.BaseModel):
    """Represents a PostgreSQL project configuration.

    Defines the project-level configuration for a PostgreSQL database.
    """

    name: str = pydantic.Field(
        description='The name of the database that is saved in the build artifact when generating a dump.',
    )
    encoding: str | None = pydantic.Field(
        default=None,
        description='The database encoding to use',
    )
    stdstrings: bool | None = pydantic.Field(
        default=None,
        description='Turn standard confirming strings on/off in the created build artifact',
    )
    superuser: str | None = pydantic.Field(
        default=None,
        description='The PostgreSQL super user',
    )
    extensions: list[Extension] | None = pydantic.Field(
        default=None,
        description='An array of PostgreSQL extensions to load into the database',
    )
    foreign_data_wrappers: list[ForeignDataWrapper] | None = pydantic.Field(
        default=None,
        description='An array of Foreign Data Wrappers to create in the database',
    )
    languages: list[Language] | None = pydantic.Field(
        default=None,
        description='An array of Procedural Languages to load into the database',
    )

    model_config = {
        'extra': 'forbid',
        'json_schema_extra': {
            '$id': 'https://pglifecycle.readthedocs.io/en/stable/schemata/project.html',
        },
    }
