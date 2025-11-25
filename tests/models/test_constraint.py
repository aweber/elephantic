"""Tests for Constraint Pydantic models."""

import unittest

import pydantic

from elephantic.models import constraint


class TestConstraint(unittest.TestCase):
    """Test Constraint model."""

    def test_constraint_with_name(self):
        """Test creating a constraint with name."""
        c = constraint.Constraint(name='my_constraint')
        self.assertEqual(c.name, 'my_constraint')

    def test_constraint_without_name(self):
        """Test creating a constraint without name."""
        c = constraint.Constraint()
        self.assertIsNone(c.name)

    def test_constraint_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            constraint.Constraint(name='test', invalid_field='value')

    def test_constraint_model_dump(self):
        """Test serializing Constraint to dict."""
        c = constraint.Constraint(name='my_constraint')
        data = c.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertEqual(data['name'], 'my_constraint')

    def test_constraint_model_dump_json(self):
        """Test serializing Constraint to JSON."""
        c = constraint.Constraint(name='my_constraint')
        json_str = c.model_dump_json(exclude_none=True)
        self.assertIn('my_constraint', json_str)


if __name__ == '__main__':
    unittest.main()
