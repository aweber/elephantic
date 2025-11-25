"""Tests for Column Pydantic models."""

import unittest

import pydantic

from elephantic.models import column


class TestSequenceBehavior(unittest.TestCase):
    """Test SequenceBehavior enumeration."""

    def test_sequence_behavior_values(self):
        """Test SequenceBehavior enum values."""
        self.assertEqual(column.SequenceBehavior.ALWAYS.value, 'ALWAYS')
        self.assertEqual(
            column.SequenceBehavior.BY_DEFAULT.value, 'BY DEFAULT'
        )


class TestGeneratedColumn(unittest.TestCase):
    """Test GeneratedColumn model."""

    def test_generated_column_with_expression(self):
        """Test creating a generated column with expression."""
        gen = column.GeneratedColumn(expression='col1 + col2')
        self.assertEqual(gen.expression, 'col1 + col2')
        self.assertIsNone(gen.sequence)
        self.assertIsNone(gen.sequence_behavior)

    def test_generated_column_with_sequence(self):
        """Test creating a generated column with sequence."""
        gen = column.GeneratedColumn(sequence='public.my_seq')
        self.assertEqual(gen.sequence, 'public.my_seq')
        self.assertIsNone(gen.expression)

    def test_generated_column_with_sequence_and_behavior(self):
        """Test creating a generated column with sequence and behavior."""
        gen = column.GeneratedColumn(
            sequence='public.my_seq',
            sequence_behavior=column.SequenceBehavior.ALWAYS,
        )
        self.assertEqual(gen.sequence, 'public.my_seq')
        self.assertEqual(gen.sequence_behavior, column.SequenceBehavior.ALWAYS)

    def test_generated_column_expression_excludes_sequence(self):
        """Test that expression cannot be used with sequence."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            column.GeneratedColumn(
                expression='col1 + col2',
                sequence='public.my_seq',
            )
        self.assertIn(
            'Cannot specify sequence or sequence_behavior when using expression',
            str(ctx.exception),
        )

    def test_generated_column_expression_excludes_sequence_behavior(self):
        """Test that expression cannot be used with sequence_behavior."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            column.GeneratedColumn(
                expression='col1 + col2',
                sequence_behavior=column.SequenceBehavior.ALWAYS,
            )
        self.assertIn(
            'Cannot specify sequence or sequence_behavior when using expression',
            str(ctx.exception),
        )

    def test_generated_column_requires_expression_or_sequence(self):
        """Test that either expression or sequence is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            column.GeneratedColumn()
        self.assertIn(
            'Must specify either expression or sequence', str(ctx.exception)
        )

    def test_generated_column_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            column.GeneratedColumn(
                expression='col1 + col2',
                invalid_field='value',
            )


class TestColumn(unittest.TestCase):
    """Test Column model."""

    def test_column_minimal(self):
        """Test creating a minimal column."""
        col = column.Column(name='id', data_type='integer')
        self.assertEqual(col.name, 'id')
        self.assertEqual(col.data_type, 'integer')
        self.assertTrue(col.nullable)
        self.assertIsNone(col.default)

    def test_column_with_nullable_false(self):
        """Test creating a non-nullable column."""
        col = column.Column(
            name='id',
            data_type='integer',
            nullable=False,
        )
        self.assertFalse(col.nullable)

    def test_column_with_string_default(self):
        """Test creating a column with string default."""
        col = column.Column(
            name='status',
            data_type='text',
            default='active',
        )
        self.assertEqual(col.default, 'active')

    def test_column_with_integer_default(self):
        """Test creating a column with integer default."""
        col = column.Column(
            name='count',
            data_type='integer',
            default=0,
        )
        self.assertEqual(col.default, 0)

    def test_column_with_boolean_default(self):
        """Test creating a column with boolean default."""
        col = column.Column(
            name='active',
            data_type='boolean',
            default=True,
        )
        self.assertTrue(col.default)

    def test_column_with_float_default(self):
        """Test creating a column with float default."""
        col = column.Column(
            name='price',
            data_type='numeric',
            default=99.99,
        )
        self.assertEqual(col.default, 99.99)

    def test_column_with_collation(self):
        """Test creating a column with collation."""
        col = column.Column(
            name='name',
            data_type='text',
            collation='en_US.UTF-8',
        )
        self.assertEqual(col.collation, 'en_US.UTF-8')

    def test_column_with_check_constraint(self):
        """Test creating a column with check constraint."""
        col = column.Column(
            name='age',
            data_type='integer',
            check_constraint='age >= 0',
        )
        self.assertEqual(col.check_constraint, 'age >= 0')

    def test_column_with_generated_expression(self):
        """Test creating a column with generated expression."""
        gen = column.GeneratedColumn(expression='col1 + col2')
        col = column.Column(
            name='total',
            data_type='integer',
            generated=gen,
        )
        self.assertIsNotNone(col.generated)
        self.assertEqual(col.generated.expression, 'col1 + col2')

    def test_column_with_generated_sequence(self):
        """Test creating a column with generated sequence."""
        gen = column.GeneratedColumn(
            sequence='public.my_seq',
            sequence_behavior=column.SequenceBehavior.ALWAYS,
        )
        col = column.Column(
            name='id',
            data_type='integer',
            generated=gen,
        )
        self.assertIsNotNone(col.generated)
        self.assertEqual(col.generated.sequence, 'public.my_seq')
        self.assertEqual(
            col.generated.sequence_behavior, column.SequenceBehavior.ALWAYS
        )

    def test_column_with_comment(self):
        """Test creating a column with comment."""
        col = column.Column(
            name='id',
            data_type='integer',
            comment='Primary key',
        )
        self.assertEqual(col.comment, 'Primary key')

    def test_column_nullable_defaults_to_true(self):
        """Test that nullable defaults to True."""
        col = column.Column(name='optional_field', data_type='text')
        self.assertTrue(col.nullable)

    def test_column_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            column.Column(data_type='integer')

    def test_column_requires_data_type(self):
        """Test that data_type is required."""
        with self.assertRaises(pydantic.ValidationError):
            column.Column(name='id')

    def test_column_complex_configuration(self):
        """Test creating a column with multiple options."""
        col = column.Column(
            name='email',
            data_type='text',
            nullable=False,
            collation='en_US.UTF-8',
            check_constraint="email LIKE '%@%'",
            comment='User email address',
        )
        self.assertEqual(col.name, 'email')
        self.assertEqual(col.data_type, 'text')
        self.assertFalse(col.nullable)
        self.assertEqual(col.collation, 'en_US.UTF-8')
        self.assertIsNotNone(col.check_constraint)
        self.assertEqual(col.comment, 'User email address')

    def test_column_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            column.Column(
                name='id',
                data_type='integer',
                invalid_field='value',
            )

    def test_column_model_dump(self):
        """Test serializing Column to dict."""
        col = column.Column(
            name='id',
            data_type='integer',
            nullable=False,
        )
        data = col.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('data_type', data)
        self.assertIn('nullable', data)
        self.assertNotIn('default', data)

    def test_column_model_dump_json(self):
        """Test serializing Column to JSON."""
        col = column.Column(
            name='username',
            data_type='text',
            default='guest',
        )
        json_str = col.model_dump_json(exclude_none=True)
        self.assertIn('username', json_str)
        self.assertIn('text', json_str)
        self.assertIn('guest', json_str)


if __name__ == '__main__':
    unittest.main()
