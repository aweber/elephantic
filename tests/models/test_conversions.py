"""Tests for Conversions Pydantic models."""

import unittest

import pydantic

from elephantic.models import conversion, conversions


class TestConversions(unittest.TestCase):
    """Test Conversions model."""

    def test_conversions_requires_schema(self):
        """Test that schema is required."""
        with self.assertRaises(pydantic.ValidationError):
            conversions.Conversions(conversions=[])

    def test_conversions_requires_conversions(self):
        """Test that conversions is required."""
        with self.assertRaises(pydantic.ValidationError):
            conversions.Conversions(schema='public')

    def test_conversions_with_schema_and_conversions(self):
        """Test creating conversions with schema and conversions list."""
        c1 = conversion.Conversion(
            name='conv1',
            schema='public',
            sql='CREATE CONVERSION ...',
        )
        c2 = conversion.Conversion(
            name='my_conversion',
            schema='public',
            encoding_from='UTF8',
            encoding_to='LATIN1',
            function='my_conv_func',
        )
        cs = conversions.Conversions(schema='public', conversions=[c1, c2])
        self.assertEqual(cs.schema, 'public')
        self.assertEqual(len(cs.conversions), 2)

    def test_conversions_with_empty_list(self):
        """Test creating conversions with empty conversions list."""
        cs = conversions.Conversions(schema='public', conversions=[])
        self.assertEqual(len(cs.conversions), 0)

    def test_conversions_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            conversions.Conversions(
                schema='public',
                conversions=[],
                invalid_field='value',
            )

    def test_conversions_model_dump(self):
        """Test serializing Conversions to dict."""
        c = conversion.Conversion(
            name='conv1',
            schema='public',
            sql='CREATE CONVERSION ...',
        )
        cs = conversions.Conversions(schema='public', conversions=[c])
        data = cs.model_dump(exclude_none=True)
        self.assertIn('schema', data)
        self.assertIn('conversions', data)

    def test_conversions_model_dump_json(self):
        """Test serializing Conversions to JSON."""
        c = conversion.Conversion(
            name='my_conversion',
            schema='public',
            encoding_from='UTF8',
            encoding_to='LATIN1',
            function='my_func',
        )
        cs = conversions.Conversions(schema='public', conversions=[c])
        json_str = cs.model_dump_json(exclude_none=True)
        self.assertIn('public', json_str)


if __name__ == '__main__':
    unittest.main()
