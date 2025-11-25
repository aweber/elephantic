"""Tests for Dependencies Pydantic models."""

import unittest

import pydantic

from elephantic.models import dependencies


class TestDependencies(unittest.TestCase):
    """Test Dependencies model."""

    def test_empty_dependencies(self):
        """Test creating an empty Dependencies object."""
        deps = dependencies.Dependencies()
        self.assertIsNone(deps.domains)
        self.assertIsNone(deps.extensions)
        self.assertIsNone(deps.foreign_data_wrappers)
        self.assertIsNone(deps.functions)
        self.assertIsNone(deps.languages)
        self.assertIsNone(deps.sequences)
        self.assertIsNone(deps.tables)
        self.assertIsNone(deps.types)
        self.assertIsNone(deps.views)

    def test_dependencies_with_domains(self):
        """Test Dependencies with domains."""
        deps = dependencies.Dependencies(
            domains=['public.email_domain', 'app.status_domain']
        )
        self.assertEqual(len(deps.domains), 2)
        self.assertIn('public.email_domain', deps.domains)
        self.assertIn('app.status_domain', deps.domains)

    def test_dependencies_with_extensions(self):
        """Test Dependencies with extensions."""
        deps = dependencies.Dependencies(extensions=['uuid-ossp', 'hstore'])
        self.assertEqual(len(deps.extensions), 2)

    def test_dependencies_with_tables(self):
        """Test Dependencies with tables."""
        deps = dependencies.Dependencies(tables=['public.users', 'app.orders'])
        self.assertEqual(len(deps.tables), 2)

    def test_dependencies_with_functions(self):
        """Test Dependencies with functions."""
        deps = dependencies.Dependencies(
            functions=['public.my_func()', 'app.calc(integer, text)']
        )
        self.assertEqual(len(deps.functions), 2)

    def test_dependencies_with_sequences(self):
        """Test Dependencies with sequences."""
        deps = dependencies.Dependencies(
            sequences=['public.users_id_seq', 'app.orders_id_seq']
        )
        self.assertEqual(len(deps.sequences), 2)

    def test_dependencies_with_types(self):
        """Test Dependencies with types."""
        deps = dependencies.Dependencies(
            types=['public.custom_type', 'app.status_enum']
        )
        self.assertEqual(len(deps.types), 2)

    def test_dependencies_with_views(self):
        """Test Dependencies with views."""
        deps = dependencies.Dependencies(
            views=['public.user_summary', 'app.report_view']
        )
        self.assertEqual(len(deps.views), 2)

    def test_dependencies_invalid_domain_pattern(self):
        """Test that invalid domain pattern raises error."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            dependencies.Dependencies(domains=['invalid'])
        self.assertIn('schema.object', str(ctx.exception))

    def test_dependencies_invalid_table_pattern(self):
        """Test that invalid table pattern raises error."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            dependencies.Dependencies(tables=['invalid'])
        self.assertIn('schema.object', str(ctx.exception))

    def test_dependencies_invalid_sequence_pattern(self):
        """Test that invalid sequence pattern raises error."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            dependencies.Dependencies(sequences=['invalid'])
        self.assertIn('schema.object', str(ctx.exception))

    def test_dependencies_invalid_type_pattern(self):
        """Test that invalid type pattern raises error."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            dependencies.Dependencies(types=['invalid'])
        self.assertIn('schema.object', str(ctx.exception))

    def test_dependencies_invalid_view_pattern(self):
        """Test that invalid view pattern raises error."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            dependencies.Dependencies(views=['invalid'])
        self.assertIn('schema.object', str(ctx.exception))

    def test_dependencies_invalid_function_pattern_no_parens(self):
        """Test that function without parentheses raises error."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            dependencies.Dependencies(functions=['public.my_func'])
        self.assertIn('schema.function(args)', str(ctx.exception))

    def test_dependencies_invalid_function_pattern_no_schema(self):
        """Test that function without schema raises error."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            dependencies.Dependencies(functions=['my_func()'])
        self.assertIn('schema.function(args)', str(ctx.exception))

    def test_dependencies_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            dependencies.Dependencies(invalid_field='value')

    def test_dependencies_complex_configuration(self):
        """Test creating Dependencies with multiple types."""
        deps = dependencies.Dependencies(
            extensions=['uuid-ossp'],
            tables=['public.users', 'public.orders'],
            sequences=['public.users_id_seq'],
            functions=['public.calc()'],
            languages=['plpgsql'],
        )
        self.assertEqual(len(deps.extensions), 1)
        self.assertEqual(len(deps.tables), 2)
        self.assertEqual(len(deps.sequences), 1)
        self.assertEqual(len(deps.functions), 1)
        self.assertEqual(len(deps.languages), 1)

    def test_dependencies_model_dump(self):
        """Test serializing Dependencies to dict."""
        deps = dependencies.Dependencies(
            tables=['public.users'],
            extensions=['uuid-ossp'],
        )
        data = deps.model_dump(exclude_none=True)
        self.assertIn('tables', data)
        self.assertIn('extensions', data)
        self.assertNotIn('domains', data)

    def test_dependencies_model_dump_json(self):
        """Test serializing Dependencies to JSON."""
        deps = dependencies.Dependencies(tables=['public.users'])
        json_str = deps.model_dump_json(exclude_none=True)
        self.assertIn('tables', json_str)
        self.assertIn('public.users', json_str)


if __name__ == '__main__':
    unittest.main()
