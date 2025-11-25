"""Tests for Type Pydantic models."""

import unittest

import pydantic

from elephantic.models import dependencies
from elephantic.models import type as type_module


class TestTypeForm(unittest.TestCase):
    """Test TypeForm enum."""

    def test_type_form_values(self):
        """Test TypeForm enum values."""
        self.assertEqual(type_module.TypeForm.BASE, 'base')
        self.assertEqual(type_module.TypeForm.COMPOSITE, 'composite')
        self.assertEqual(type_module.TypeForm.ENUM, 'enum')
        self.assertEqual(type_module.TypeForm.RANGE, 'range')


class TestAlignment(unittest.TestCase):
    """Test Alignment enum."""

    def test_alignment_values(self):
        """Test Alignment enum values."""
        self.assertEqual(type_module.Alignment.CHAR, 'char')
        self.assertEqual(type_module.Alignment.DOUBLE, 'double')
        self.assertEqual(type_module.Alignment.INT2, 'int2')
        self.assertEqual(type_module.Alignment.INT4, 'int4')


class TestStorage(unittest.TestCase):
    """Test Storage enum."""

    def test_storage_values(self):
        """Test Storage enum values."""
        self.assertEqual(type_module.Storage.PLAIN, 'plain')
        self.assertEqual(type_module.Storage.EXTENDED, 'extended')
        self.assertEqual(type_module.Storage.EXTERNAL, 'external')
        self.assertEqual(type_module.Storage.MAIN, 'main')


class TestCategory(unittest.TestCase):
    """Test Category enum."""

    def test_category_values(self):
        """Test Category enum values."""
        self.assertEqual(type_module.Category.A, 'A')
        self.assertEqual(type_module.Category.B, 'B')
        self.assertEqual(type_module.Category.N, 'N')
        self.assertEqual(type_module.Category.S, 'S')


class TestTypeColumn(unittest.TestCase):
    """Test TypeColumn model."""

    def test_type_column_requires_name_and_data_type(self):
        """Test that name and data_type are required."""
        with self.assertRaises(pydantic.ValidationError):
            type_module.TypeColumn(name='column1')
        with self.assertRaises(pydantic.ValidationError):
            type_module.TypeColumn(data_type='text')

    def test_type_column_with_name_and_data_type(self):
        """Test creating type column with name and data_type."""
        col = type_module.TypeColumn(name='column1', data_type='text')
        self.assertEqual(col.name, 'column1')
        self.assertEqual(col.data_type, 'text')

    def test_type_column_with_collation(self):
        """Test creating type column with collation."""
        col = type_module.TypeColumn(
            name='column1',
            data_type='text',
            collation='en_US',
        )
        self.assertEqual(col.collation, 'en_US')


class TestType(unittest.TestCase):
    """Test Type model."""

    def test_type_with_sql(self):
        """Test creating a type with SQL."""
        t = type_module.Type(sql='CREATE TYPE ...')
        self.assertIsNotNone(t.sql)

    def test_type_requires_sql_or_type(self):
        """Test that either sql or type is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            type_module.Type(name='my_type')
        self.assertIn('Must specify either sql or type', str(ctx.exception))

    def test_type_cannot_have_both_sql_and_type(self):
        """Test that sql and type are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            type_module.Type(
                sql='CREATE TYPE ...',
                type=type_module.TypeForm.COMPOSITE,
            )
        self.assertIn('Cannot specify both sql and type', str(ctx.exception))

    def test_type_base_requires_input_and_output(self):
        """Test that base type requires input and output functions."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            type_module.Type(type=type_module.TypeForm.BASE)
        self.assertIn(
            'Base type requires input and output functions', str(ctx.exception)
        )

    def test_type_base_with_input_and_output(self):
        """Test creating base type with input and output."""
        t = type_module.Type(
            type=type_module.TypeForm.BASE,
            input='my_input_func',
            output='my_output_func',
        )
        self.assertEqual(t.type, type_module.TypeForm.BASE)
        self.assertEqual(t.input, 'my_input_func')

    def test_type_base_with_all_fields(self):
        """Test creating base type with all optional fields."""
        t = type_module.Type(
            name='my_base_type',
            schema='public',
            type=type_module.TypeForm.BASE,
            input='my_input',
            output='my_output',
            receive='my_receive',
            send='my_send',
            typmod_in='my_typmod_in',
            typmod_out='my_typmod_out',
            analyze='my_analyze',
            internal_length=8,
            passed_by_value=True,
            alignment=type_module.Alignment.INT4,
            storage=type_module.Storage.PLAIN,
            like_type='integer',
            category=type_module.Category.N,
            preferred='true',
            default=0,
            element='text',
            delimiter=',',
            collatable=True,
        )
        self.assertEqual(t.internal_length, 8)
        self.assertTrue(t.passed_by_value)

    def test_type_base_with_variable_length(self):
        """Test creating base type with VARIABLE length."""
        t = type_module.Type(
            type=type_module.TypeForm.BASE,
            input='my_input',
            output='my_output',
            internal_length='VARIABLE',
        )
        self.assertEqual(t.internal_length, 'VARIABLE')

    def test_type_base_invalid_internal_length(self):
        """Test that internal_length validates correctly."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            type_module.Type(
                type=type_module.TypeForm.BASE,
                input='my_input',
                output='my_output',
                internal_length='invalid',
            )
        self.assertIn('must be an integer or "VARIABLE"', str(ctx.exception))

    def test_type_base_cannot_have_columns(self):
        """Test that base type cannot have columns."""
        col = type_module.TypeColumn(name='col1', data_type='text')
        with self.assertRaises(pydantic.ValidationError) as ctx:
            type_module.Type(
                type=type_module.TypeForm.BASE,
                input='my_input',
                output='my_output',
                columns=[col],
            )
        self.assertIn('Base type cannot have columns', str(ctx.exception))

    def test_type_composite_requires_columns(self):
        """Test that composite type requires columns."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            type_module.Type(type=type_module.TypeForm.COMPOSITE)
        self.assertIn('Composite type requires columns', str(ctx.exception))

    def test_type_composite_with_columns(self):
        """Test creating composite type with columns."""
        col1 = type_module.TypeColumn(name='col1', data_type='text')
        col2 = type_module.TypeColumn(name='col2', data_type='integer')
        t = type_module.Type(
            name='my_composite',
            schema='public',
            type=type_module.TypeForm.COMPOSITE,
            columns=[col1, col2],
        )
        self.assertEqual(len(t.columns), 2)
        self.assertEqual(t.columns[0].name, 'col1')

    def test_type_composite_cannot_have_input_output(self):
        """Test that composite type cannot have input/output functions."""
        col = type_module.TypeColumn(name='col1', data_type='text')
        with self.assertRaises(pydantic.ValidationError) as ctx:
            type_module.Type(
                type=type_module.TypeForm.COMPOSITE,
                columns=[col],
                input='my_input',
            )
        self.assertIn(
            'Composite type cannot have base type', str(ctx.exception)
        )

    def test_type_enum_requires_enum_values(self):
        """Test that enum type requires enum values."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            type_module.Type(type=type_module.TypeForm.ENUM)
        self.assertIn('Enum type requires enum values', str(ctx.exception))

    def test_type_enum_with_values(self):
        """Test creating enum type with values."""
        t = type_module.Type(
            name='my_enum',
            schema='public',
            type=type_module.TypeForm.ENUM,
            enum=['value1', 'value2', 'value3'],
        )
        self.assertEqual(len(t.enum), 3)
        self.assertEqual(t.enum[0], 'value1')

    def test_type_enum_value_max_length(self):
        """Test that enum values cannot exceed 64 bytes."""
        long_value = 'a' * 65
        with self.assertRaises(pydantic.ValidationError) as ctx:
            type_module.Type(
                type=type_module.TypeForm.ENUM,
                enum=[long_value],
            )
        self.assertIn('exceeds maximum length of 64 bytes', str(ctx.exception))

    def test_type_enum_cannot_have_columns(self):
        """Test that enum type cannot have columns."""
        col = type_module.TypeColumn(name='col1', data_type='text')
        with self.assertRaises(pydantic.ValidationError) as ctx:
            type_module.Type(
                type=type_module.TypeForm.ENUM,
                enum=['val1', 'val2'],
                columns=[col],
            )
        self.assertIn('Enum type cannot have', str(ctx.exception))

    def test_type_range_requires_subtype(self):
        """Test that range type requires subtype."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            type_module.Type(type=type_module.TypeForm.RANGE)
        self.assertIn('Range type requires subtype', str(ctx.exception))

    def test_type_range_with_subtype(self):
        """Test creating range type with subtype."""
        t = type_module.Type(
            name='my_range',
            schema='public',
            type=type_module.TypeForm.RANGE,
            subtype='integer',
        )
        self.assertEqual(t.type, type_module.TypeForm.RANGE)
        self.assertEqual(t.subtype, 'integer')

    def test_type_range_with_all_fields(self):
        """Test creating range type with all optional fields."""
        t = type_module.Type(
            name='my_range',
            schema='public',
            type=type_module.TypeForm.RANGE,
            subtype='integer',
            subtype_opclass='int4_ops',
            collation='en_US',
            canonical='my_canonical',
            subtype_diff='my_diff',
        )
        self.assertEqual(t.subtype_opclass, 'int4_ops')
        self.assertEqual(t.canonical, 'my_canonical')

    def test_type_range_cannot_have_columns(self):
        """Test that range type cannot have columns."""
        col = type_module.TypeColumn(name='col1', data_type='text')
        with self.assertRaises(pydantic.ValidationError) as ctx:
            type_module.Type(
                type=type_module.TypeForm.RANGE,
                subtype='integer',
                columns=[col],
            )
        self.assertIn('Range type cannot have', str(ctx.exception))

    def test_type_with_comment(self):
        """Test creating type with comment."""
        t = type_module.Type(
            sql='CREATE TYPE ...',
            comment='Custom type comment',
        )
        self.assertEqual(t.comment, 'Custom type comment')

    def test_type_with_owner(self):
        """Test creating type with owner."""
        t = type_module.Type(
            sql='CREATE TYPE ...',
            owner='app_user',
        )
        self.assertEqual(t.owner, 'app_user')

    def test_type_with_dependencies(self):
        """Test creating type with dependencies."""
        deps = dependencies.Dependencies(functions=['public.my_func()'])
        t = type_module.Type(
            sql='CREATE TYPE ...',
            dependencies=deps,
        )
        self.assertIsNotNone(t.dependencies)

    def test_type_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            type_module.Type(
                sql='CREATE TYPE ...',
                invalid_field='value',
            )

    def test_type_model_dump(self):
        """Test serializing Type to dict."""
        t = type_module.Type(sql='CREATE TYPE ...')
        data = t.model_dump(exclude_none=True)
        self.assertIn('sql', data)

    def test_type_model_dump_json(self):
        """Test serializing Type to JSON."""
        t = type_module.Type(
            type=type_module.TypeForm.ENUM,
            enum=['val1', 'val2'],
        )
        json_str = t.model_dump_json(exclude_none=True)
        self.assertIn('enum', json_str)


if __name__ == '__main__':
    unittest.main()
