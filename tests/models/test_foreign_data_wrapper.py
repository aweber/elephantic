"""Tests for ForeignDataWrapper Pydantic models."""

import unittest

import pydantic

from elephantic.models import foreign_data_wrapper


class TestForeignDataWrapper(unittest.TestCase):
    """Test ForeignDataWrapper model."""

    def test_foreign_data_wrapper_with_name(self):
        """Test creating a foreign data wrapper with name."""
        fdw = foreign_data_wrapper.ForeignDataWrapper(name='postgres_fdw')
        self.assertEqual(fdw.name, 'postgres_fdw')

    def test_foreign_data_wrapper_without_name(self):
        """Test creating a foreign data wrapper without name."""
        fdw = foreign_data_wrapper.ForeignDataWrapper()
        self.assertIsNone(fdw.name)

    def test_foreign_data_wrapper_with_owner(self):
        """Test creating a foreign data wrapper with owner."""
        fdw = foreign_data_wrapper.ForeignDataWrapper(
            name='postgres_fdw',
            owner='postgres',
        )
        self.assertEqual(fdw.owner, 'postgres')

    def test_foreign_data_wrapper_with_comment(self):
        """Test creating a foreign data wrapper with comment."""
        fdw = foreign_data_wrapper.ForeignDataWrapper(
            name='postgres_fdw',
            comment='PostgreSQL FDW',
        )
        self.assertEqual(fdw.comment, 'PostgreSQL FDW')

    def test_foreign_data_wrapper_with_handler(self):
        """Test creating a foreign data wrapper with handler."""
        fdw = foreign_data_wrapper.ForeignDataWrapper(
            name='postgres_fdw',
            handler='postgres_fdw_handler',
        )
        self.assertEqual(fdw.handler, 'postgres_fdw_handler')

    def test_foreign_data_wrapper_with_validator(self):
        """Test creating a foreign data wrapper with validator."""
        fdw = foreign_data_wrapper.ForeignDataWrapper(
            name='postgres_fdw',
            validator='postgres_fdw_validator',
        )
        self.assertEqual(fdw.validator, 'postgres_fdw_validator')

    def test_foreign_data_wrapper_with_options(self):
        """Test creating a foreign data wrapper with options."""
        fdw = foreign_data_wrapper.ForeignDataWrapper(
            name='postgres_fdw',
            options={'debug': True, 'timeout': 30},
        )
        self.assertEqual(len(fdw.options), 2)
        self.assertTrue(fdw.options['debug'])

    def test_foreign_data_wrapper_options_validate_names(self):
        """Test that option names are validated."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            foreign_data_wrapper.ForeignDataWrapper(
                name='postgres_fdw',
                options={'invalid-name!': 'value'},
            )
        self.assertIn('does not match required pattern', str(ctx.exception))

    def test_foreign_data_wrapper_options_allow_valid_names(self):
        """Test that valid option names are allowed."""
        fdw = foreign_data_wrapper.ForeignDataWrapper(
            name='postgres_fdw',
            options={
                'debug': True,
                'timeout_ms': 30000,
                '_private': 'value',
                'host.name': 'localhost',
            },
        )
        self.assertEqual(len(fdw.options), 4)

    def test_foreign_data_wrapper_complex_configuration(self):
        """Test creating a foreign data wrapper with all fields."""
        fdw = foreign_data_wrapper.ForeignDataWrapper(
            name='postgres_fdw',
            owner='postgres',
            comment='PostgreSQL FDW',
            handler='postgres_fdw_handler',
            validator='postgres_fdw_validator',
            options={'debug': True},
        )
        self.assertEqual(fdw.name, 'postgres_fdw')
        self.assertEqual(fdw.owner, 'postgres')
        self.assertIsNotNone(fdw.handler)
        self.assertIsNotNone(fdw.validator)
        self.assertIsNotNone(fdw.options)

    def test_foreign_data_wrapper_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            foreign_data_wrapper.ForeignDataWrapper(
                name='postgres_fdw',
                invalid_field='value',
            )

    def test_foreign_data_wrapper_model_dump(self):
        """Test serializing ForeignDataWrapper to dict."""
        fdw = foreign_data_wrapper.ForeignDataWrapper(name='postgres_fdw')
        data = fdw.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertNotIn('comment', data)

    def test_foreign_data_wrapper_model_dump_json(self):
        """Test serializing ForeignDataWrapper to JSON."""
        fdw = foreign_data_wrapper.ForeignDataWrapper(name='postgres_fdw')
        json_str = fdw.model_dump_json(exclude_none=True)
        self.assertIn('postgres_fdw', json_str)


if __name__ == '__main__':
    unittest.main()
