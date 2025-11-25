"""Tests for Sequence Pydantic models."""

import unittest

import pydantic

from elephantic.models import sequence


class TestDataType(unittest.TestCase):
    """Test DataType enumeration."""

    def test_data_type_values(self):
        """Test DataType enum values."""
        self.assertEqual(sequence.DataType.SMALLINT.value, 'smallint')
        self.assertEqual(sequence.DataType.SMALLINT_UPPER.value, 'SMALLINT')
        self.assertEqual(sequence.DataType.INT2.value, 'int2')
        self.assertEqual(sequence.DataType.INT2_UPPER.value, 'INT2')
        self.assertEqual(sequence.DataType.INTEGER.value, 'integer')
        self.assertEqual(sequence.DataType.INTEGER_UPPER.value, 'INTEGER')
        self.assertEqual(sequence.DataType.INT4.value, 'int4')
        self.assertEqual(sequence.DataType.INT4_UPPER.value, 'INT4')
        self.assertEqual(sequence.DataType.BIGINT.value, 'bigint')
        self.assertEqual(sequence.DataType.BIGINT_UPPER.value, 'BIGINT')
        self.assertEqual(sequence.DataType.INT8.value, 'int8')
        self.assertEqual(sequence.DataType.INT8_UPPER.value, 'INT8')


class TestSequence(unittest.TestCase):
    """Test Sequence model."""

    def test_sequence_with_schema_and_name(self):
        """Test creating a sequence with schema and name."""
        s = sequence.Sequence(schema='public', name='my_seq')
        self.assertEqual(s.schema, 'public')
        self.assertEqual(s.name, 'my_seq')

    def test_sequence_with_sql(self):
        """Test creating a sequence with SQL."""
        s = sequence.Sequence(sql='CREATE SEQUENCE public.my_seq')
        self.assertIsNotNone(s.sql)

    def test_sequence_defaults(self):
        """Test Sequence default values."""
        s = sequence.Sequence(schema='public', name='my_seq')
        self.assertEqual(s.data_type, sequence.DataType.BIGINT_UPPER)
        self.assertEqual(s.increment_by, 1)
        self.assertEqual(s.min_value, 1)
        self.assertEqual(s.cache, 1)
        self.assertIsNone(s.max_value)
        self.assertIsNone(s.cycle)

    def test_sequence_with_data_type(self):
        """Test creating a sequence with data_type."""
        s = sequence.Sequence(
            schema='public',
            name='my_seq',
            data_type=sequence.DataType.INTEGER,
        )
        self.assertEqual(s.data_type, sequence.DataType.INTEGER)

    def test_sequence_with_increment_by(self):
        """Test creating a sequence with increment_by."""
        s = sequence.Sequence(
            schema='public',
            name='my_seq',
            increment_by=5,
        )
        self.assertEqual(s.increment_by, 5)

    def test_sequence_with_min_value(self):
        """Test creating a sequence with min_value."""
        s = sequence.Sequence(
            schema='public',
            name='my_seq',
            min_value=100,
        )
        self.assertEqual(s.min_value, 100)

    def test_sequence_with_max_value(self):
        """Test creating a sequence with max_value."""
        s = sequence.Sequence(
            schema='public',
            name='my_seq',
            max_value=1000,
        )
        self.assertEqual(s.max_value, 1000)

    def test_sequence_with_start_with(self):
        """Test creating a sequence with start_with."""
        s = sequence.Sequence(
            schema='public',
            name='my_seq',
            start_with=100,
        )
        self.assertEqual(s.start_with, 100)

    def test_sequence_with_cache(self):
        """Test creating a sequence with cache."""
        s = sequence.Sequence(
            schema='public',
            name='my_seq',
            cache=10,
        )
        self.assertEqual(s.cache, 10)

    def test_sequence_with_cycle_true(self):
        """Test creating a sequence with cycle=True."""
        s = sequence.Sequence(
            schema='public',
            name='my_seq',
            cycle=True,
        )
        self.assertTrue(s.cycle)

    def test_sequence_with_cycle_false(self):
        """Test creating a sequence with cycle=False."""
        s = sequence.Sequence(
            schema='public',
            name='my_seq',
            cycle=False,
        )
        self.assertFalse(s.cycle)

    def test_sequence_with_owned_by(self):
        """Test creating a sequence with owned_by."""
        s = sequence.Sequence(
            schema='public',
            name='my_seq',
            owned_by='public.users.id',
        )
        self.assertEqual(s.owned_by, 'public.users.id')

    def test_sequence_with_owner(self):
        """Test creating a sequence with owner."""
        s = sequence.Sequence(
            schema='public',
            name='my_seq',
            owner='app_user',
        )
        self.assertEqual(s.owner, 'app_user')

    def test_sequence_with_comment(self):
        """Test creating a sequence with comment."""
        s = sequence.Sequence(
            schema='public',
            name='my_seq',
            comment='User ID sequence',
        )
        self.assertEqual(s.comment, 'User ID sequence')

    def test_sequence_requires_sql_or_schema_name(self):
        """Test that either sql or (schema and name) is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            sequence.Sequence()
        self.assertIn(
            'Must specify either sql or both schema and name',
            str(ctx.exception),
        )

    def test_sequence_cannot_have_sql_with_structured_fields(self):
        """Test that sql and structured fields are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            sequence.Sequence(
                sql='CREATE SEQUENCE ...',
                data_type=sequence.DataType.INTEGER,
            )
        self.assertIn(
            'Cannot specify sql with structured fields', str(ctx.exception)
        )

    def test_sequence_sql_with_non_default_increment(self):
        """Test that sql cannot be used with non-default increment_by."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            sequence.Sequence(
                sql='CREATE SEQUENCE ...',
                increment_by=5,
            )
        self.assertIn(
            'Cannot specify sql with structured fields', str(ctx.exception)
        )

    def test_sequence_complex_configuration(self):
        """Test creating a sequence with all fields."""
        s = sequence.Sequence(
            schema='public',
            name='my_seq',
            owner='app_user',
            data_type=sequence.DataType.INTEGER,
            increment_by=5,
            min_value=1,
            max_value=1000,
            start_with=100,
            cache=10,
            cycle=True,
            owned_by='public.users.id',
            comment='User ID sequence',
        )
        self.assertEqual(s.schema, 'public')
        self.assertEqual(s.name, 'my_seq')
        self.assertEqual(s.data_type, sequence.DataType.INTEGER)
        self.assertEqual(s.increment_by, 5)
        self.assertEqual(s.max_value, 1000)
        self.assertTrue(s.cycle)

    def test_sequence_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            sequence.Sequence(
                schema='public',
                name='my_seq',
                invalid_field='value',
            )

    def test_sequence_model_dump(self):
        """Test serializing Sequence to dict."""
        s = sequence.Sequence(schema='public', name='my_seq')
        data = s.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('schema', data)
        self.assertNotIn('max_value', data)

    def test_sequence_model_dump_json(self):
        """Test serializing Sequence to JSON."""
        s = sequence.Sequence(schema='public', name='my_seq')
        json_str = s.model_dump_json(exclude_none=True)
        self.assertIn('my_seq', json_str)


if __name__ == '__main__':
    unittest.main()
