"""Tests for Types Pydantic models."""

import unittest

import pydantic

from elephantic.models import type as type_module
from elephantic.models import types


class TestTypes(unittest.TestCase):
    """Test Types model."""

    def test_types_requires_schema(self):
        """Test that schema is required."""
        with self.assertRaises(pydantic.ValidationError):
            types.Types(types=[])

    def test_types_requires_types(self):
        """Test that types is required."""
        with self.assertRaises(pydantic.ValidationError):
            types.Types(schema='public')

    def test_types_with_schema_and_types(self):
        """Test creating types with schema and types list."""
        t1 = type_module.Type(sql='CREATE TYPE ...')
        t2 = type_module.Type(
            type=type_module.TypeForm.ENUM,
            enum=['val1', 'val2'],
        )
        ts = types.Types(schema='public', types=[t1, t2])
        self.assertEqual(ts.schema, 'public')
        self.assertEqual(len(ts.types), 2)

    def test_types_with_empty_list(self):
        """Test creating types with empty types list."""
        ts = types.Types(schema='public', types=[])
        self.assertEqual(len(ts.types), 0)

    def test_types_with_composite_type(self):
        """Test creating types with composite type."""
        col = type_module.TypeColumn(name='col1', data_type='text')
        t = type_module.Type(
            name='address',
            type=type_module.TypeForm.COMPOSITE,
            columns=[col],
        )
        ts = types.Types(schema='public', types=[t])
        self.assertEqual(ts.types[0].name, 'address')

    def test_types_with_range_type(self):
        """Test creating types with range type."""
        t = type_module.Type(
            name='int_range',
            type=type_module.TypeForm.RANGE,
            subtype='integer',
        )
        ts = types.Types(schema='public', types=[t])
        self.assertEqual(ts.types[0].subtype, 'integer')

    def test_types_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            types.Types(
                schema='public',
                types=[],
                invalid_field='value',
            )

    def test_types_model_dump(self):
        """Test serializing Types to dict."""
        t = type_module.Type(sql='CREATE TYPE ...')
        ts = types.Types(schema='public', types=[t])
        data = ts.model_dump(exclude_none=True)
        self.assertIn('schema', data)
        self.assertIn('types', data)

    def test_types_model_dump_json(self):
        """Test serializing Types to JSON."""
        t = type_module.Type(
            type=type_module.TypeForm.ENUM,
            enum=['val1'],
        )
        ts = types.Types(schema='public', types=[t])
        json_str = ts.model_dump_json(exclude_none=True)
        self.assertIn('public', json_str)


if __name__ == '__main__':
    unittest.main()
