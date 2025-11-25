"""Tests for Conversion Pydantic models."""

import unittest

import pydantic

from elephantic.models import conversion, dependencies


class TestConversion(unittest.TestCase):
    """Test Conversion model."""

    def test_conversion_with_sql(self):
        """Test creating a conversion with raw SQL."""
        conv = conversion.Conversion(
            name='my_conversion',
            schema='public',
            sql='CREATE CONVERSION...',
        )
        self.assertEqual(conv.name, 'my_conversion')
        self.assertEqual(conv.schema, 'public')
        self.assertIsNotNone(conv.sql)
        self.assertIsNone(conv.encoding_from)

    def test_conversion_with_encodings_and_function(self):
        """Test creating a conversion with encoding parameters."""
        conv = conversion.Conversion(
            name='my_conversion',
            schema='public',
            encoding_from='UTF8',
            encoding_to='LATIN1',
            function='public.utf8_to_latin1',
        )
        self.assertEqual(conv.encoding_from, 'UTF8')
        self.assertEqual(conv.encoding_to, 'LATIN1')
        self.assertEqual(conv.function, 'public.utf8_to_latin1')
        self.assertIsNone(conv.sql)

    def test_conversion_with_default(self):
        """Test creating a default conversion."""
        conv = conversion.Conversion(
            name='my_conversion',
            schema='public',
            encoding_from='UTF8',
            encoding_to='LATIN1',
            function='public.utf8_to_latin1',
            default=True,
        )
        self.assertTrue(conv.default)

    def test_conversion_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            conversion.Conversion(
                schema='public',
                sql='CREATE CONVERSION...',
            )

    def test_conversion_requires_schema(self):
        """Test that schema is required."""
        with self.assertRaises(pydantic.ValidationError):
            conversion.Conversion(
                name='my_conversion',
                sql='CREATE CONVERSION...',
            )

    def test_conversion_sql_excludes_encoding_params(self):
        """Test that sql cannot be used with encoding parameters."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            conversion.Conversion(
                name='my_conversion',
                schema='public',
                sql='CREATE CONVERSION...',
                encoding_from='UTF8',
            )
        self.assertIn(
            'Cannot specify default, encoding_from, encoding_to, or function when using sql',
            str(ctx.exception),
        )

    def test_conversion_sql_excludes_default(self):
        """Test that sql cannot be used with default."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            conversion.Conversion(
                name='my_conversion',
                schema='public',
                sql='CREATE CONVERSION...',
                default=True,
            )
        self.assertIn('Cannot specify', str(ctx.exception))

    def test_conversion_requires_all_encoding_params(self):
        """Test that encoding_from, encoding_to, and function are all required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            conversion.Conversion(
                name='my_conversion',
                schema='public',
                encoding_from='UTF8',
                encoding_to='LATIN1',
            )
        self.assertIn(
            'Must specify either sql OR (encoding_from, encoding_to, and function)',
            str(ctx.exception),
        )

    def test_conversion_requires_definition_method(self):
        """Test that at least one definition method is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            conversion.Conversion(
                name='my_conversion',
                schema='public',
            )
        self.assertIn('Must specify either sql OR', str(ctx.exception))

    def test_conversion_with_owner(self):
        """Test conversion with owner."""
        conv = conversion.Conversion(
            name='my_conversion',
            schema='public',
            owner='postgres',
            sql='CREATE CONVERSION...',
        )
        self.assertEqual(conv.owner, 'postgres')

    def test_conversion_with_comment(self):
        """Test conversion with comment."""
        conv = conversion.Conversion(
            name='my_conversion',
            schema='public',
            sql='CREATE CONVERSION...',
            comment='Test conversion',
        )
        self.assertEqual(conv.comment, 'Test conversion')

    def test_conversion_with_dependencies(self):
        """Test conversion with dependencies."""
        deps = dependencies.Dependencies(functions=['public.utf8_to_latin1()'])
        conv = conversion.Conversion(
            name='my_conversion',
            schema='public',
            sql='CREATE CONVERSION...',
            dependencies=deps,
        )
        self.assertIsNotNone(conv.dependencies)
        self.assertEqual(len(conv.dependencies.functions), 1)

    def test_conversion_complete_configuration(self):
        """Test conversion with all encoding parameters."""
        conv = conversion.Conversion(
            name='my_conversion',
            schema='public',
            owner='postgres',
            encoding_from='UTF8',
            encoding_to='LATIN1',
            function='public.utf8_to_latin1',
            default=True,
            comment='Default UTF8 to LATIN1 conversion',
        )
        self.assertEqual(conv.name, 'my_conversion')
        self.assertEqual(conv.schema, 'public')
        self.assertEqual(conv.owner, 'postgres')
        self.assertEqual(conv.encoding_from, 'UTF8')
        self.assertEqual(conv.encoding_to, 'LATIN1')
        self.assertEqual(conv.function, 'public.utf8_to_latin1')
        self.assertTrue(conv.default)
        self.assertEqual(conv.comment, 'Default UTF8 to LATIN1 conversion')

    def test_conversion_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            conversion.Conversion(
                name='my_conversion',
                schema='public',
                sql='CREATE CONVERSION...',
                invalid_field='value',
            )

    def test_conversion_model_dump(self):
        """Test serializing Conversion to dict."""
        conv = conversion.Conversion(
            name='my_conversion',
            schema='public',
            encoding_from='UTF8',
            encoding_to='LATIN1',
            function='public.utf8_to_latin1',
        )
        data = conv.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('schema', data)
        self.assertIn('encoding_from', data)
        self.assertIn('encoding_to', data)
        self.assertIn('function', data)
        self.assertNotIn('sql', data)

    def test_conversion_model_dump_json(self):
        """Test serializing Conversion to JSON."""
        conv = conversion.Conversion(
            name='my_conversion',
            schema='public',
            encoding_from='UTF8',
            encoding_to='LATIN1',
            function='public.utf8_to_latin1',
        )
        json_str = conv.model_dump_json(exclude_none=True)
        self.assertIn('my_conversion', json_str)
        self.assertIn('UTF8', json_str)
        self.assertIn('LATIN1', json_str)


if __name__ == '__main__':
    unittest.main()
