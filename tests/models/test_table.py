"""Tests for Table Pydantic models."""

import unittest

import pydantic

from elephantic.models import column, table


class TestTable(unittest.TestCase):
    """Test Table model."""

    def test_table_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            table.Table(schema='public', sql='CREATE TABLE ...')

    def test_table_requires_schema(self):
        """Test that schema is required."""
        with self.assertRaises(pydantic.ValidationError):
            table.Table(name='users', sql='CREATE TABLE ...')

    def test_table_with_sql(self):
        """Test creating table with SQL."""
        t = table.Table(
            name='users',
            schema='public',
            sql='CREATE TABLE ...',
        )
        self.assertEqual(t.name, 'users')
        self.assertIsNotNone(t.sql)

    def test_table_with_columns(self):
        """Test creating table with columns."""
        col = column.Column(name='id', data_type='integer')
        t = table.Table(
            name='users',
            schema='public',
            columns=[col],
        )
        self.assertEqual(len(t.columns), 1)

    def test_table_requires_definition(self):
        """Test that a definition method is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            table.Table(name='users', schema='public')
        self.assertIn('Must specify one of', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
