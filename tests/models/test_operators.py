"""Tests for Operators Pydantic models."""

import unittest

import pydantic

from elephantic.models import operator, operators


class TestOperators(unittest.TestCase):
    """Test Operators model."""

    def test_operators_requires_schema(self):
        """Test that schema is required."""
        with self.assertRaises(pydantic.ValidationError):
            operators.Operators(operators=[])

    def test_operators_requires_operators(self):
        """Test that operators is required."""
        with self.assertRaises(pydantic.ValidationError):
            operators.Operators(schema='public')

    def test_operators_requires_non_empty_list(self):
        """Test that operators list cannot be empty."""
        with self.assertRaises(pydantic.ValidationError):
            operators.Operators(schema='public', operators=[])

    def test_operators_with_required_fields(self):
        """Test creating operators with required fields."""
        op = operator.Operator(
            name='===',
            schema='public',
            left_arg='text',
            right_arg='text',
            function='text_equal',
        )
        ops = operators.Operators(
            schema='public',
            operators=[op],
        )
        self.assertEqual(ops.schema, 'public')
        self.assertEqual(len(ops.operators), 1)


if __name__ == '__main__':
    unittest.main()
