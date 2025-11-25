"""Tests for Server Pydantic models."""

import unittest

import pydantic

from elephantic.models import dependencies, server


class TestServer(unittest.TestCase):
    """Test Server model."""

    def test_server_with_required_fields(self):
        """Test creating a server with required fields."""
        deps = dependencies.Dependencies(
            foreign_data_wrappers=['postgres_fdw']
        )
        s = server.Server(
            name='my_server',
            foreign_data_wrapper='postgres_fdw',
            dependencies=deps,
        )
        self.assertEqual(s.name, 'my_server')
        self.assertEqual(s.foreign_data_wrapper, 'postgres_fdw')

    def test_server_requires_name(self):
        """Test that name is required."""
        deps = dependencies.Dependencies(
            foreign_data_wrappers=['postgres_fdw']
        )
        with self.assertRaises(pydantic.ValidationError):
            server.Server(
                foreign_data_wrapper='postgres_fdw',
                dependencies=deps,
            )

    def test_server_requires_foreign_data_wrapper(self):
        """Test that foreign_data_wrapper is required."""
        deps = dependencies.Dependencies(
            foreign_data_wrappers=['postgres_fdw']
        )
        with self.assertRaises(pydantic.ValidationError):
            server.Server(
                name='my_server',
                dependencies=deps,
            )

    def test_server_requires_dependencies(self):
        """Test that dependencies is required."""
        with self.assertRaises(pydantic.ValidationError):
            server.Server(
                name='my_server',
                foreign_data_wrapper='postgres_fdw',
            )

    def test_server_with_type(self):
        """Test creating a server with type."""
        deps = dependencies.Dependencies(
            foreign_data_wrappers=['postgres_fdw']
        )
        s = server.Server(
            name='my_server',
            foreign_data_wrapper='postgres_fdw',
            dependencies=deps,
            type='PostgreSQL',
        )
        self.assertEqual(s.type, 'PostgreSQL')

    def test_server_with_version(self):
        """Test creating a server with version."""
        deps = dependencies.Dependencies(
            foreign_data_wrappers=['postgres_fdw']
        )
        s = server.Server(
            name='my_server',
            foreign_data_wrapper='postgres_fdw',
            dependencies=deps,
            version='15.0',
        )
        self.assertEqual(s.version, '15.0')

    def test_server_with_comment(self):
        """Test creating a server with comment."""
        deps = dependencies.Dependencies(
            foreign_data_wrappers=['postgres_fdw']
        )
        s = server.Server(
            name='my_server',
            foreign_data_wrapper='postgres_fdw',
            dependencies=deps,
            comment='Production server',
        )
        self.assertEqual(s.comment, 'Production server')

    def test_server_with_options(self):
        """Test creating a server with options."""
        deps = dependencies.Dependencies(
            foreign_data_wrappers=['postgres_fdw']
        )
        s = server.Server(
            name='my_server',
            foreign_data_wrapper='postgres_fdw',
            dependencies=deps,
            options={'host': 'localhost', 'port': 5432, 'dbname': 'postgres'},
        )
        self.assertEqual(len(s.options), 3)
        self.assertEqual(s.options['host'], 'localhost')

    def test_server_options_validate_names(self):
        """Test that option names are validated."""
        deps = dependencies.Dependencies(
            foreign_data_wrappers=['postgres_fdw']
        )
        with self.assertRaises(pydantic.ValidationError) as ctx:
            server.Server(
                name='my_server',
                foreign_data_wrapper='postgres_fdw',
                dependencies=deps,
                options={'invalid-name!': 'value'},
            )
        self.assertIn('does not match required pattern', str(ctx.exception))

    def test_server_options_allow_valid_names(self):
        """Test that valid option names are allowed."""
        deps = dependencies.Dependencies(
            foreign_data_wrappers=['postgres_fdw']
        )
        s = server.Server(
            name='my_server',
            foreign_data_wrapper='postgres_fdw',
            dependencies=deps,
            options={
                'host': 'localhost',
                'port_number': 5432,
                '_private': 'value',
                'option.name': 'value',
            },
        )
        self.assertEqual(len(s.options), 4)

    def test_server_complex_configuration(self):
        """Test creating a server with all fields."""
        deps = dependencies.Dependencies(
            foreign_data_wrappers=['postgres_fdw']
        )
        s = server.Server(
            name='my_server',
            foreign_data_wrapper='postgres_fdw',
            type='PostgreSQL',
            version='15.0',
            comment='Production server',
            options={'host': 'localhost', 'port': 5432},
            dependencies=deps,
        )
        self.assertEqual(s.name, 'my_server')
        self.assertEqual(s.type, 'PostgreSQL')
        self.assertEqual(s.version, '15.0')
        self.assertIsNotNone(s.options)

    def test_server_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        deps = dependencies.Dependencies(
            foreign_data_wrappers=['postgres_fdw']
        )
        with self.assertRaises(pydantic.ValidationError):
            server.Server(
                name='my_server',
                foreign_data_wrapper='postgres_fdw',
                dependencies=deps,
                invalid_field='value',
            )

    def test_server_model_dump(self):
        """Test serializing Server to dict."""
        deps = dependencies.Dependencies(
            foreign_data_wrappers=['postgres_fdw']
        )
        s = server.Server(
            name='my_server',
            foreign_data_wrapper='postgres_fdw',
            dependencies=deps,
        )
        data = s.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('foreign_data_wrapper', data)
        self.assertNotIn('comment', data)

    def test_server_model_dump_json(self):
        """Test serializing Server to JSON."""
        deps = dependencies.Dependencies(
            foreign_data_wrappers=['postgres_fdw']
        )
        s = server.Server(
            name='my_server',
            foreign_data_wrapper='postgres_fdw',
            dependencies=deps,
        )
        json_str = s.model_dump_json(exclude_none=True)
        self.assertIn('my_server', json_str)


if __name__ == '__main__':
    unittest.main()
