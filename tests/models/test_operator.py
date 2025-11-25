"""Tests for Operator Pydantic models."""

import unittest

import pydantic

from elephantic.models import dependencies, operator


class TestOperator(unittest.TestCase):
    """Test Operator model."""

    def test_operator_with_sql(self):
        """Test creating an operator with SQL."""
        op = operator.Operator(sql='CREATE OPERATOR ...')
        self.assertIsNotNone(op.sql)

    def test_operator_with_function(self):
        """Test creating an operator with function."""
        op = operator.Operator(function='my_function')
        self.assertEqual(op.function, 'my_function')

    def test_operator_requires_sql_or_function(self):
        """Test that either sql or function is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            operator.Operator()
        self.assertIn(
            'Must specify either sql or function', str(ctx.exception)
        )

    def test_operator_cannot_have_both_sql_and_function(self):
        """Test that sql and function are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            operator.Operator(
                sql='CREATE OPERATOR ...',
                function='my_function',
            )
        self.assertIn(
            'Cannot specify both sql and function', str(ctx.exception)
        )

    def test_operator_cannot_have_sql_with_structured_fields(self):
        """Test that sql and structured fields are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            operator.Operator(
                sql='CREATE OPERATOR ...',
                left_arg='integer',
            )
        self.assertIn(
            'Cannot specify sql with structured fields', str(ctx.exception)
        )

    def test_operator_with_name(self):
        """Test creating an operator with name."""
        op = operator.Operator(name='===', function='my_function')
        self.assertEqual(op.name, '===')

    def test_operator_with_schema(self):
        """Test creating an operator with schema."""
        op = operator.Operator(
            schema='public',
            function='my_function',
        )
        self.assertEqual(op.schema, 'public')

    def test_operator_with_owner(self):
        """Test creating an operator with owner."""
        op = operator.Operator(
            function='my_function',
            owner='app_user',
        )
        self.assertEqual(op.owner, 'app_user')

    def test_operator_with_left_arg(self):
        """Test creating an operator with left_arg."""
        op = operator.Operator(
            function='my_function',
            left_arg='integer',
        )
        self.assertEqual(op.left_arg, 'integer')

    def test_operator_with_right_arg(self):
        """Test creating an operator with right_arg."""
        op = operator.Operator(
            function='my_function',
            right_arg='integer',
        )
        self.assertEqual(op.right_arg, 'integer')

    def test_operator_with_both_args(self):
        """Test creating an operator with both args."""
        op = operator.Operator(
            function='my_function',
            left_arg='integer',
            right_arg='integer',
        )
        self.assertEqual(op.left_arg, 'integer')
        self.assertEqual(op.right_arg, 'integer')

    def test_operator_with_commutator(self):
        """Test creating an operator with commutator."""
        op = operator.Operator(
            function='my_function',
            commutator='@@@',
        )
        self.assertEqual(op.commutator, '@@@')

    def test_operator_with_negator(self):
        """Test creating an operator with negator."""
        op = operator.Operator(
            function='my_function',
            negator='!==',
        )
        self.assertEqual(op.negator, '!==')

    def test_operator_with_restrict(self):
        """Test creating an operator with restrict function."""
        op = operator.Operator(
            function='my_function',
            restrict='my_restrict_func',
        )
        self.assertEqual(op.restrict, 'my_restrict_func')

    def test_operator_with_join(self):
        """Test creating an operator with join function."""
        op = operator.Operator(
            function='my_function',
            join='my_join_func',
        )
        self.assertEqual(op.join, 'my_join_func')

    def test_operator_with_hashes(self):
        """Test creating an operator with hashes flag."""
        op = operator.Operator(
            function='my_function',
            hashes=True,
        )
        self.assertTrue(op.hashes)

    def test_operator_with_merges(self):
        """Test creating an operator with merges flag."""
        op = operator.Operator(
            function='my_function',
            merges=True,
        )
        self.assertTrue(op.merges)

    def test_operator_with_comment(self):
        """Test creating an operator with comment."""
        op = operator.Operator(
            function='my_function',
            comment='Custom equality operator',
        )
        self.assertEqual(op.comment, 'Custom equality operator')

    def test_operator_with_dependencies(self):
        """Test creating an operator with dependencies."""
        deps = dependencies.Dependencies(functions=['public.my_function()'])
        op = operator.Operator(
            function='my_function',
            dependencies=deps,
        )
        self.assertIsNotNone(op.dependencies)

    def test_operator_complex_configuration(self):
        """Test creating an operator with all fields."""
        deps = dependencies.Dependencies(
            functions=['public.my_function(integer,integer)']
        )
        op = operator.Operator(
            name='===',
            schema='public',
            owner='app_user',
            function='my_function',
            left_arg='integer',
            right_arg='integer',
            commutator='===',
            negator='!==',
            restrict='eqsel',
            join='eqjoinsel',
            hashes=True,
            merges=True,
            comment='Custom equality',
            dependencies=deps,
        )
        self.assertEqual(op.name, '===')
        self.assertEqual(op.left_arg, 'integer')
        self.assertTrue(op.hashes)

    def test_operator_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            operator.Operator(
                function='my_function',
                invalid_field='value',
            )

    def test_operator_model_dump(self):
        """Test serializing Operator to dict."""
        op = operator.Operator(function='my_function')
        data = op.model_dump(exclude_none=True)
        self.assertIn('function', data)
        self.assertNotIn('comment', data)

    def test_operator_model_dump_json(self):
        """Test serializing Operator to JSON."""
        op = operator.Operator(function='my_function')
        json_str = op.model_dump_json(exclude_none=True)
        self.assertIn('my_function', json_str)


if __name__ == '__main__':
    unittest.main()
