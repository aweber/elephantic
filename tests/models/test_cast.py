"""Tests for Cast Pydantic models."""

import unittest

import pydantic

from elephantic.models import cast, dependencies


class TestCast(unittest.TestCase):
    """Test Cast model."""

    def test_cast_with_sql(self):
        """Test creating a cast with raw SQL."""
        c = cast.Cast(
            source_type='integer',
            target_type='text',
            sql='CREATE CAST...',
        )
        self.assertEqual(c.source_type, 'integer')
        self.assertEqual(c.target_type, 'text')
        self.assertIsNotNone(c.sql)
        self.assertIsNone(c.function)

    def test_cast_with_function(self):
        """Test creating a cast with a function."""
        c = cast.Cast(
            source_type='integer',
            target_type='text',
            function='public.int_to_text',
        )
        self.assertEqual(c.source_type, 'integer')
        self.assertEqual(c.target_type, 'text')
        self.assertEqual(c.function, 'public.int_to_text')
        self.assertIsNone(c.sql)

    def test_cast_with_inout(self):
        """Test creating a cast with I/O conversion."""
        c = cast.Cast(
            source_type='integer',
            target_type='text',
            inout=True,
        )
        self.assertEqual(c.source_type, 'integer')
        self.assertEqual(c.target_type, 'text')
        self.assertTrue(c.inout)
        self.assertIsNone(c.function)

    def test_cast_with_assignment(self):
        """Test that assignment requires a conversion mechanism."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            cast.Cast(
                source_type='integer',
                target_type='text',
                assignment=True,
            )
        self.assertIn('Must specify either sql OR one of', str(ctx.exception))

    def test_cast_with_implicit(self):
        """Test that implicit requires a conversion mechanism."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            cast.Cast(
                source_type='integer',
                target_type='text',
                implicit=True,
            )
        self.assertIn('Must specify either sql OR one of', str(ctx.exception))

    def test_cast_requires_source_type(self):
        """Test that source_type is required."""
        with self.assertRaises(pydantic.ValidationError):
            cast.Cast(target_type='text', sql='CREATE CAST...')

    def test_cast_requires_target_type(self):
        """Test that target_type is required."""
        with self.assertRaises(pydantic.ValidationError):
            cast.Cast(source_type='integer', sql='CREATE CAST...')

    def test_cast_sql_excludes_function(self):
        """Test that sql cannot be used with function."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            cast.Cast(
                source_type='integer',
                target_type='text',
                sql='CREATE CAST...',
                function='public.int_to_text',
            )
        self.assertIn('Cannot specify function', str(ctx.exception))

    def test_cast_sql_excludes_inout(self):
        """Test that sql cannot be used with inout."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            cast.Cast(
                source_type='integer',
                target_type='text',
                sql='CREATE CAST...',
                inout=True,
            )
        self.assertIn('Cannot specify', str(ctx.exception))

    def test_cast_sql_excludes_assignment(self):
        """Test that sql cannot be used with assignment."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            cast.Cast(
                source_type='integer',
                target_type='text',
                sql='CREATE CAST...',
                assignment=True,
            )
        self.assertIn('Cannot specify', str(ctx.exception))

    def test_cast_function_and_inout_mutually_exclusive(self):
        """Test that function and inout cannot be used together."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            cast.Cast(
                source_type='integer',
                target_type='text',
                function='public.int_to_text',
                inout=True,
            )
        self.assertIn(
            'Cannot specify both function and inout', str(ctx.exception)
        )

    def test_cast_requires_definition_method(self):
        """Test that at least one definition method is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            cast.Cast(
                source_type='integer',
                target_type='text',
            )
        self.assertIn('Must specify either sql OR one of', str(ctx.exception))

    def test_cast_with_schema(self):
        """Test cast with schema."""
        c = cast.Cast(
            source_type='integer',
            target_type='text',
            schema='public',
            sql='CREATE CAST...',
        )
        self.assertEqual(c.schema, 'public')

    def test_cast_with_owner(self):
        """Test cast with owner."""
        c = cast.Cast(
            source_type='integer',
            target_type='text',
            owner='postgres',
            sql='CREATE CAST...',
        )
        self.assertEqual(c.owner, 'postgres')

    def test_cast_with_comment(self):
        """Test cast with comment."""
        c = cast.Cast(
            source_type='integer',
            target_type='text',
            sql='CREATE CAST...',
            comment='Test cast',
        )
        self.assertEqual(c.comment, 'Test cast')

    def test_cast_with_dependencies(self):
        """Test cast with dependencies."""
        deps = dependencies.Dependencies(functions=['public.int_to_text()'])
        c = cast.Cast(
            source_type='integer',
            target_type='text',
            sql='CREATE CAST...',
            dependencies=deps,
        )
        self.assertIsNotNone(c.dependencies)
        self.assertEqual(len(c.dependencies.functions), 1)

    def test_cast_with_function_and_assignment(self):
        """Test cast with function and assignment."""
        c = cast.Cast(
            source_type='integer',
            target_type='text',
            function='public.int_to_text',
            assignment=True,
        )
        self.assertEqual(c.function, 'public.int_to_text')
        self.assertTrue(c.assignment)

    def test_cast_with_inout_and_assignment(self):
        """Test cast with inout and assignment."""
        c = cast.Cast(
            source_type='integer',
            target_type='text',
            inout=True,
            assignment=True,
        )
        self.assertTrue(c.inout)
        self.assertTrue(c.assignment)

    def test_cast_with_assignment_and_implicit(self):
        """Test that assignment and implicit together require a conversion mechanism."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            cast.Cast(
                source_type='integer',
                target_type='text',
                assignment=True,
                implicit=True,
            )
        self.assertIn('Must specify either sql OR one of', str(ctx.exception))

    def test_cast_defaults(self):
        """Test cast default values."""
        c = cast.Cast(
            source_type='integer',
            target_type='text',
            sql='CREATE CAST...',
        )
        self.assertFalse(c.inout)
        self.assertFalse(c.assignment)
        self.assertFalse(c.implicit)

    def test_cast_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            cast.Cast(
                source_type='integer',
                target_type='text',
                sql='CREATE CAST...',
                invalid_field='value',
            )

    def test_cast_model_dump(self):
        """Test serializing Cast to dict."""
        c = cast.Cast(
            source_type='integer',
            target_type='text',
            sql='CREATE CAST...',
        )
        data = c.model_dump(exclude_none=True)
        self.assertIn('source_type', data)
        self.assertIn('target_type', data)
        self.assertIn('sql', data)
        self.assertNotIn('schema', data)

    def test_cast_model_dump_json(self):
        """Test serializing Cast to JSON."""
        c = cast.Cast(
            source_type='integer',
            target_type='text',
            sql='CREATE CAST...',
        )
        json_str = c.model_dump_json(exclude_none=True)
        self.assertIn('integer', json_str)
        self.assertIn('text', json_str)


if __name__ == '__main__':
    unittest.main()
