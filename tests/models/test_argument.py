"""Tests for Argument Pydantic models."""

import unittest

import pydantic

from elephantic.models import argument


class TestArgumentMode(unittest.TestCase):
    """Test ArgumentMode enumeration."""

    def test_argument_mode_values(self):
        """Test ArgumentMode enum values."""
        self.assertEqual(argument.ArgumentMode.IN.value, 'IN')
        self.assertEqual(argument.ArgumentMode.VARIADIC.value, 'VARIADIC')


class TestArgument(unittest.TestCase):
    """Test Argument model."""

    def test_argument_with_data_type_only(self):
        """Test creating an argument with only data_type."""
        arg = argument.Argument(data_type='integer')
        self.assertEqual(arg.data_type, 'integer')
        self.assertEqual(arg.mode, argument.ArgumentMode.IN)
        self.assertIsNone(arg.name)

    def test_argument_with_name(self):
        """Test creating an argument with name."""
        arg = argument.Argument(data_type='text', name='username')
        self.assertEqual(arg.data_type, 'text')
        self.assertEqual(arg.name, 'username')
        self.assertEqual(arg.mode, argument.ArgumentMode.IN)

    def test_argument_with_variadic_mode(self):
        """Test creating a variadic argument."""
        arg = argument.Argument(
            data_type='text',
            name='args',
            mode=argument.ArgumentMode.VARIADIC,
        )
        self.assertEqual(arg.data_type, 'text')
        self.assertEqual(arg.name, 'args')
        self.assertEqual(arg.mode, argument.ArgumentMode.VARIADIC)

    def test_argument_requires_data_type(self):
        """Test that data_type is required."""
        with self.assertRaises(pydantic.ValidationError):
            argument.Argument()

    def test_argument_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            argument.Argument(data_type='integer', invalid_field='value')

    def test_argument_model_dump(self):
        """Test serializing Argument to dict."""
        arg = argument.Argument(
            data_type='integer',
            name='count',
            mode=argument.ArgumentMode.IN,
        )
        data = arg.model_dump(exclude_none=True)
        self.assertIn('data_type', data)
        self.assertIn('name', data)
        self.assertIn('mode', data)
        self.assertEqual(data['data_type'], 'integer')
        self.assertEqual(data['name'], 'count')
        self.assertEqual(data['mode'], 'IN')

    def test_argument_model_dump_json(self):
        """Test serializing Argument to JSON."""
        arg = argument.Argument(data_type='text', name='message')
        json_str = arg.model_dump_json(exclude_none=True)
        self.assertIn('text', json_str)
        self.assertIn('message', json_str)


if __name__ == '__main__':
    unittest.main()
