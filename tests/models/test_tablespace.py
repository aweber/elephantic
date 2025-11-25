"""Tests for Tablespace Pydantic models."""

import unittest

import pydantic

from elephantic.models import tablespace


class TestTablespace(unittest.TestCase):
    """Test Tablespace model."""

    def test_tablespace_with_name_and_location(self):
        """Test creating a tablespace with name and location."""
        t = tablespace.Tablespace(name='fast_storage', location='/mnt/ssd')
        self.assertEqual(t.name, 'fast_storage')
        self.assertEqual(t.location, '/mnt/ssd')

    def test_tablespace_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            tablespace.Tablespace(location='/mnt/ssd')

    def test_tablespace_requires_location(self):
        """Test that location is required."""
        with self.assertRaises(pydantic.ValidationError):
            tablespace.Tablespace(name='fast_storage')

    def test_tablespace_with_owner(self):
        """Test creating a tablespace with owner."""
        t = tablespace.Tablespace(
            name='fast_storage',
            location='/mnt/ssd',
            owner='postgres',
        )
        self.assertEqual(t.owner, 'postgres')

    def test_tablespace_with_valid_options(self):
        """Test creating a tablespace with valid options."""
        t = tablespace.Tablespace(
            name='fast_storage',
            location='/mnt/ssd',
            options=[
                {'seq_page_cost': 0.1},
                {'random_page_cost': 0.2},
            ],
        )
        self.assertEqual(len(t.options), 2)

    def test_tablespace_with_seq_page_cost(self):
        """Test creating a tablespace with seq_page_cost option."""
        t = tablespace.Tablespace(
            name='fast_storage',
            location='/mnt/ssd',
            options=[{'seq_page_cost': 0.1}],
        )
        self.assertIn('seq_page_cost', t.options[0])

    def test_tablespace_with_random_page_cost(self):
        """Test creating a tablespace with random_page_cost option."""
        t = tablespace.Tablespace(
            name='fast_storage',
            location='/mnt/ssd',
            options=[{'random_page_cost': 0.2}],
        )
        self.assertIn('random_page_cost', t.options[0])

    def test_tablespace_with_effective_io_concurrency(self):
        """Test creating a tablespace with effective_io_concurrency option."""
        t = tablespace.Tablespace(
            name='fast_storage',
            location='/mnt/ssd',
            options=[{'effective_io_concurrency': 200}],
        )
        self.assertIn('effective_io_concurrency', t.options[0])

    def test_tablespace_options_validate_names(self):
        """Test that option names are validated."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            tablespace.Tablespace(
                name='fast_storage',
                location='/mnt/ssd',
                options=[{'invalid_option': 1.0}],
            )
        self.assertIn('does not match required pattern', str(ctx.exception))

    def test_tablespace_with_comment(self):
        """Test creating a tablespace with comment."""
        t = tablespace.Tablespace(
            name='fast_storage',
            location='/mnt/ssd',
            comment='SSD storage for hot data',
        )
        self.assertEqual(t.comment, 'SSD storage for hot data')

    def test_tablespace_complex_configuration(self):
        """Test creating a tablespace with all fields."""
        t = tablespace.Tablespace(
            name='fast_storage',
            location='/mnt/ssd',
            owner='postgres',
            options=[
                {'seq_page_cost': 0.1},
                {'random_page_cost': 0.2},
                {'effective_io_concurrency': 200},
            ],
            comment='SSD storage',
        )
        self.assertEqual(t.name, 'fast_storage')
        self.assertEqual(t.owner, 'postgres')
        self.assertEqual(len(t.options), 3)
        self.assertIsNotNone(t.comment)

    def test_tablespace_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            tablespace.Tablespace(
                name='fast_storage',
                location='/mnt/ssd',
                invalid_field='value',
            )

    def test_tablespace_model_dump(self):
        """Test serializing Tablespace to dict."""
        t = tablespace.Tablespace(name='fast_storage', location='/mnt/ssd')
        data = t.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('location', data)
        self.assertNotIn('comment', data)

    def test_tablespace_model_dump_json(self):
        """Test serializing Tablespace to JSON."""
        t = tablespace.Tablespace(name='fast_storage', location='/mnt/ssd')
        json_str = t.model_dump_json(exclude_none=True)
        self.assertIn('fast_storage', json_str)


if __name__ == '__main__':
    unittest.main()
