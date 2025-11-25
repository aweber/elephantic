"""Tests for Publication Pydantic models."""

import unittest

import pydantic

from elephantic.models import publication


class TestPublication(unittest.TestCase):
    """Test Publication model."""

    def test_publication_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            publication.Publication(tables=['users'])

    def test_publication_requires_tables_or_all_tables(self):
        """Test that either tables or all_tables is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            publication.Publication(name='pub_test')
        self.assertIn(
            'Must specify either tables or all_tables', str(ctx.exception)
        )

    def test_publication_cannot_have_both(self):
        """Test that tables and all_tables are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            publication.Publication(
                name='pub_test',
                tables=['users'],
                all_tables=True,
            )
        self.assertIn(
            'Cannot specify both tables and all_tables', str(ctx.exception)
        )

    def test_publication_with_tables(self):
        """Test creating publication with tables."""
        pub = publication.Publication(
            name='pub_users',
            tables=['users', 'orders'],
        )
        self.assertEqual(pub.name, 'pub_users')
        self.assertEqual(len(pub.tables), 2)

    def test_publication_with_all_tables(self):
        """Test creating publication with all_tables."""
        pub = publication.Publication(
            name='pub_all',
            all_tables=True,
        )
        self.assertTrue(pub.all_tables)


if __name__ == '__main__':
    unittest.main()
