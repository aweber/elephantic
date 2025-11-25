"""Tests for Casts Pydantic models."""

import unittest

import pydantic

from elephantic.models import cast, casts


class TestCasts(unittest.TestCase):
    """Test Casts model."""

    def test_casts_requires_schema(self):
        """Test that schema is required."""
        with self.assertRaises(pydantic.ValidationError):
            casts.Casts(casts=[])

    def test_casts_requires_casts(self):
        """Test that casts is required."""
        with self.assertRaises(pydantic.ValidationError):
            casts.Casts(schema='public')

    def test_casts_with_schema_and_casts(self):
        """Test creating casts with schema and casts list."""
        c1 = cast.Cast(
            source_type='integer',
            target_type='text',
            sql='CREATE CAST ...',
        )
        c2 = cast.Cast(
            source_type='text',
            target_type='integer',
            function='text_to_int',
        )
        cs = casts.Casts(schema='public', casts=[c1, c2])
        self.assertEqual(cs.schema, 'public')
        self.assertEqual(len(cs.casts), 2)

    def test_casts_with_empty_list(self):
        """Test creating casts with empty casts list."""
        cs = casts.Casts(schema='public', casts=[])
        self.assertEqual(len(cs.casts), 0)

    def test_casts_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            casts.Casts(
                schema='public',
                casts=[],
                invalid_field='value',
            )

    def test_casts_model_dump(self):
        """Test serializing Casts to dict."""
        c = cast.Cast(
            source_type='integer',
            target_type='text',
            sql='CREATE CAST ...',
        )
        cs = casts.Casts(schema='public', casts=[c])
        data = cs.model_dump(exclude_none=True)
        self.assertIn('schema', data)
        self.assertIn('casts', data)

    def test_casts_model_dump_json(self):
        """Test serializing Casts to JSON."""
        c = cast.Cast(
            source_type='text',
            target_type='integer',
            function='text_to_int',
        )
        cs = casts.Casts(schema='public', casts=[c])
        json_str = cs.model_dump_json(exclude_none=True)
        self.assertIn('public', json_str)


if __name__ == '__main__':
    unittest.main()
