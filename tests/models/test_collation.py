"""Tests for Collation Pydantic models."""

import unittest

import pydantic

from elephantic.models import collation, dependencies


class TestLocaleProvider(unittest.TestCase):
    """Test LocaleProvider enumeration."""

    def test_locale_provider_values(self):
        """Test LocaleProvider enum values."""
        self.assertEqual(collation.LocaleProvider.ICU.value, 'icu')
        self.assertEqual(collation.LocaleProvider.LIBC.value, 'libc')


class TestCollation(unittest.TestCase):
    """Test Collation model."""

    def test_collation_with_sql(self):
        """Test creating a collation with raw SQL."""
        coll = collation.Collation(
            name='my_collation',
            schema='public',
            owner='postgres',
            sql='CREATE COLLATION...',
        )
        self.assertEqual(coll.name, 'my_collation')
        self.assertEqual(coll.schema, 'public')
        self.assertEqual(coll.owner, 'postgres')
        self.assertIsNotNone(coll.sql)

    def test_collation_with_copy_from(self):
        """Test creating a collation by copying."""
        coll = collation.Collation(
            name='my_collation',
            schema='public',
            owner='postgres',
            copy_from='pg_catalog.C',
        )
        self.assertEqual(coll.copy_from, 'pg_catalog.C')
        self.assertIsNone(coll.sql)

    def test_collation_with_locale(self):
        """Test creating a collation with locale shortcut."""
        coll = collation.Collation(
            name='my_collation',
            schema='public',
            owner='postgres',
            locale='en_US.UTF-8',
        )
        self.assertEqual(coll.locale, 'en_US.UTF-8')

    def test_collation_with_lc_collate_and_lc_ctype(self):
        """Test creating a collation with lc_collate and lc_ctype."""
        coll = collation.Collation(
            name='my_collation',
            schema='public',
            owner='postgres',
            lc_collate='en_US.UTF-8',
            lc_ctype='en_US.UTF-8',
        )
        self.assertEqual(coll.lc_collate, 'en_US.UTF-8')
        self.assertEqual(coll.lc_ctype, 'en_US.UTF-8')

    def test_collation_with_provider(self):
        """Test creating a collation with provider."""
        coll = collation.Collation(
            name='my_collation',
            schema='public',
            owner='postgres',
            locale='en_US.UTF-8',
            provider=collation.LocaleProvider.ICU,
        )
        self.assertEqual(coll.provider, collation.LocaleProvider.ICU)

    def test_collation_deterministic_default(self):
        """Test that deterministic defaults to True."""
        coll = collation.Collation(
            name='my_collation',
            schema='public',
            owner='postgres',
            locale='en_US.UTF-8',
        )
        self.assertTrue(coll.deterministic)

    def test_collation_with_deterministic_false(self):
        """Test creating a non-deterministic collation."""
        coll = collation.Collation(
            name='my_collation',
            schema='public',
            owner='postgres',
            locale='en_US.UTF-8',
            deterministic=False,
        )
        self.assertFalse(coll.deterministic)

    def test_collation_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            collation.Collation(
                schema='public',
                owner='postgres',
                sql='CREATE COLLATION...',
            )

    def test_collation_requires_schema(self):
        """Test that schema is required."""
        with self.assertRaises(pydantic.ValidationError):
            collation.Collation(
                name='my_collation',
                owner='postgres',
                sql='CREATE COLLATION...',
            )

    def test_collation_requires_owner(self):
        """Test that owner is required."""
        with self.assertRaises(pydantic.ValidationError):
            collation.Collation(
                name='my_collation',
                schema='public',
                sql='CREATE COLLATION...',
            )

    def test_collation_sql_excludes_copy_from(self):
        """Test that sql cannot be used with copy_from."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            collation.Collation(
                name='my_collation',
                schema='public',
                owner='postgres',
                sql='CREATE COLLATION...',
                copy_from='pg_catalog.C',
            )
        self.assertIn(
            'Cannot specify both sql and copy_from', str(ctx.exception)
        )

    def test_collation_sql_excludes_locale_params(self):
        """Test that sql cannot be used with locale parameters."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            collation.Collation(
                name='my_collation',
                schema='public',
                owner='postgres',
                sql='CREATE COLLATION...',
                locale='en_US.UTF-8',
            )
        self.assertIn(
            'Cannot specify locale parameters when using sql',
            str(ctx.exception),
        )

    def test_collation_copy_from_excludes_locale_params(self):
        """Test that copy_from cannot be used with locale parameters."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            collation.Collation(
                name='my_collation',
                schema='public',
                owner='postgres',
                copy_from='pg_catalog.C',
                locale='en_US.UTF-8',
            )
        self.assertIn(
            'Cannot specify locale parameters when using copy_from',
            str(ctx.exception),
        )

    def test_collation_locale_excludes_lc_collate(self):
        """Test that locale cannot be used with lc_collate."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            collation.Collation(
                name='my_collation',
                schema='public',
                owner='postgres',
                locale='en_US.UTF-8',
                lc_collate='en_US.UTF-8',
            )
        self.assertIn(
            'Cannot specify lc_collate or lc_ctype when using locale',
            str(ctx.exception),
        )

    def test_collation_locale_excludes_lc_ctype(self):
        """Test that locale cannot be used with lc_ctype."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            collation.Collation(
                name='my_collation',
                schema='public',
                owner='postgres',
                locale='en_US.UTF-8',
                lc_ctype='en_US.UTF-8',
            )
        self.assertIn(
            'Cannot specify lc_collate or lc_ctype when using locale',
            str(ctx.exception),
        )

    def test_collation_requires_definition_method(self):
        """Test that at least one definition method is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            collation.Collation(
                name='my_collation',
                schema='public',
                owner='postgres',
            )
        self.assertIn(
            'Must specify either sql, copy_from, or at least one locale parameter',
            str(ctx.exception),
        )

    def test_collation_with_comment(self):
        """Test collation with comment."""
        coll = collation.Collation(
            name='my_collation',
            schema='public',
            owner='postgres',
            locale='en_US.UTF-8',
            comment='Test collation',
        )
        self.assertEqual(coll.comment, 'Test collation')

    def test_collation_with_dependencies(self):
        """Test collation with dependencies."""
        deps = dependencies.Dependencies(extensions=['icu-extension'])
        coll = collation.Collation(
            name='my_collation',
            schema='public',
            owner='postgres',
            locale='en_US.UTF-8',
            dependencies=deps,
        )
        self.assertIsNotNone(coll.dependencies)
        self.assertEqual(len(coll.dependencies.extensions), 1)

    def test_collation_with_provider_only(self):
        """Test collation with only provider specified."""
        coll = collation.Collation(
            name='my_collation',
            schema='public',
            owner='postgres',
            provider=collation.LocaleProvider.LIBC,
        )
        self.assertEqual(coll.provider, collation.LocaleProvider.LIBC)

    def test_collation_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            collation.Collation(
                name='my_collation',
                schema='public',
                owner='postgres',
                locale='en_US.UTF-8',
                invalid_field='value',
            )

    def test_collation_model_dump(self):
        """Test serializing Collation to dict."""
        coll = collation.Collation(
            name='my_collation',
            schema='public',
            owner='postgres',
            locale='en_US.UTF-8',
        )
        data = coll.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('schema', data)
        self.assertIn('owner', data)
        self.assertIn('locale', data)
        self.assertNotIn('sql', data)

    def test_collation_model_dump_json(self):
        """Test serializing Collation to JSON."""
        coll = collation.Collation(
            name='my_collation',
            schema='public',
            owner='postgres',
            locale='en_US.UTF-8',
        )
        json_str = coll.model_dump_json(exclude_none=True)
        self.assertIn('my_collation', json_str)
        self.assertIn('en_US.UTF-8', json_str)


if __name__ == '__main__':
    unittest.main()
