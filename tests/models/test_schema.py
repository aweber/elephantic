"""Tests for Schema Pydantic models."""

import unittest

import pydantic

from elephantic.models import schema


class TestSchema(unittest.TestCase):
    """Test Schema model."""

    def test_schema_with_name(self):
        """Test creating a schema with name."""
        s = schema.Schema(name='my_schema')
        self.assertEqual(s.name, 'my_schema')
        self.assertIsNone(s.owner)
        self.assertIsNone(s.comment)

    def test_schema_with_all_fields(self):
        """Test creating a schema with all fields."""
        s = schema.Schema(
            name='my_schema',
            owner='postgres',
            comment='Test schema',
        )
        self.assertEqual(s.name, 'my_schema')
        self.assertEqual(s.owner, 'postgres')
        self.assertEqual(s.comment, 'Test schema')

    def test_schema_without_name(self):
        """Test creating a schema without name."""
        s = schema.Schema()
        self.assertIsNone(s.name)

    def test_schema_name_cannot_start_with_pg(self):
        """Test that schema name cannot begin with pg_."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            schema.Schema(name='pg_myschema')
        self.assertIn('cannot begin with pg_', str(ctx.exception))

    def test_schema_name_can_contain_pg(self):
        """Test that schema name can contain pg but not start with it."""
        s = schema.Schema(name='my_pg_schema')
        self.assertEqual(s.name, 'my_pg_schema')

    def test_schema_with_owner(self):
        """Test creating a schema with owner."""
        s = schema.Schema(name='my_schema', owner='app_user')
        self.assertEqual(s.owner, 'app_user')

    def test_schema_with_comment(self):
        """Test creating a schema with comment."""
        s = schema.Schema(name='my_schema', comment='Application schema')
        self.assertEqual(s.comment, 'Application schema')

    def test_schema_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            schema.Schema(name='test', invalid_field='value')

    def test_schema_model_dump(self):
        """Test serializing Schema to dict."""
        s = schema.Schema(name='my_schema', owner='postgres')
        data = s.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('owner', data)
        self.assertNotIn('comment', data)

    def test_schema_model_dump_json(self):
        """Test serializing Schema to JSON."""
        s = schema.Schema(name='my_schema')
        json_str = s.model_dump_json(exclude_none=True)
        self.assertIn('my_schema', json_str)


if __name__ == '__main__':
    unittest.main()
