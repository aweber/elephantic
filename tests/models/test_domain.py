"""Tests for Domain Pydantic models."""

import unittest

import pydantic

from elephantic.models import dependencies, domain


class TestCheckConstraint(unittest.TestCase):
    """Test CheckConstraint model."""

    def test_check_constraint_with_expression(self):
        """Test creating a check constraint with expression."""
        cc = domain.CheckConstraint(expression='VALUE > 0')
        self.assertEqual(cc.expression, 'VALUE > 0')
        self.assertIsNone(cc.nullable)

    def test_check_constraint_with_nullable(self):
        """Test creating a check constraint with nullable."""
        cc = domain.CheckConstraint(nullable=True)
        self.assertTrue(cc.nullable)
        self.assertIsNone(cc.expression)

    def test_check_constraint_with_name(self):
        """Test creating a check constraint with name."""
        cc = domain.CheckConstraint(
            name='positive_check', expression='VALUE > 0'
        )
        self.assertEqual(cc.name, 'positive_check')

    def test_check_constraint_requires_expression_or_nullable(self):
        """Test that either expression or nullable is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            domain.CheckConstraint()
        self.assertIn(
            'Must specify either expression or nullable', str(ctx.exception)
        )

    def test_check_constraint_cannot_have_both(self):
        """Test that expression and nullable are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            domain.CheckConstraint(expression='VALUE > 0', nullable=True)
        self.assertIn('Cannot specify both', str(ctx.exception))

    def test_check_constraint_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            domain.CheckConstraint(
                expression='VALUE > 0', invalid_field='value'
            )


class TestDomain(unittest.TestCase):
    """Test Domain model."""

    def test_domain_with_sql(self):
        """Test creating a domain with SQL."""
        d = domain.Domain(
            name='positive_int',
            schema='public',
            sql='CREATE DOMAIN positive_int AS integer CHECK (VALUE > 0)',
        )
        self.assertEqual(d.name, 'positive_int')
        self.assertEqual(d.schema, 'public')
        self.assertIsNotNone(d.sql)

    def test_domain_with_data_type(self):
        """Test creating a domain with data_type."""
        d = domain.Domain(
            name='positive_int',
            schema='public',
            data_type='integer',
        )
        self.assertEqual(d.data_type, 'integer')

    def test_domain_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            domain.Domain(schema='public', data_type='integer')

    def test_domain_requires_schema(self):
        """Test that schema is required."""
        with self.assertRaises(pydantic.ValidationError):
            domain.Domain(name='positive_int', data_type='integer')

    def test_domain_requires_sql_or_data_type(self):
        """Test that either sql or data_type is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            domain.Domain(name='positive_int', schema='public')
        self.assertIn(
            'Must specify either sql or data_type', str(ctx.exception)
        )

    def test_domain_cannot_have_sql_and_data_type(self):
        """Test that sql and data_type are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            domain.Domain(
                name='positive_int',
                schema='public',
                sql='CREATE DOMAIN ...',
                data_type='integer',
            )
        self.assertIn('Cannot specify sql with data_type', str(ctx.exception))

    def test_domain_cannot_have_sql_and_check_constraints(self):
        """Test that sql and check_constraints are mutually exclusive."""
        cc = domain.CheckConstraint(expression='VALUE > 0')
        with self.assertRaises(pydantic.ValidationError) as ctx:
            domain.Domain(
                name='positive_int',
                schema='public',
                sql='CREATE DOMAIN ...',
                check_constraints=[cc],
            )
        self.assertIn('Cannot specify sql with', str(ctx.exception))

    def test_domain_with_owner(self):
        """Test creating a domain with owner."""
        d = domain.Domain(
            name='positive_int',
            schema='public',
            data_type='integer',
            owner='app_user',
        )
        self.assertEqual(d.owner, 'app_user')

    def test_domain_with_collation(self):
        """Test creating a domain with collation."""
        d = domain.Domain(
            name='my_text',
            schema='public',
            data_type='text',
            collation='en_US',
        )
        self.assertEqual(d.collation, 'en_US')

    def test_domain_with_default_string(self):
        """Test creating a domain with string default."""
        d = domain.Domain(
            name='my_text',
            schema='public',
            data_type='text',
            default='hello',
        )
        self.assertEqual(d.default, 'hello')

    def test_domain_with_default_int(self):
        """Test creating a domain with integer default."""
        d = domain.Domain(
            name='my_int',
            schema='public',
            data_type='integer',
            default=42,
        )
        self.assertEqual(d.default, 42)

    def test_domain_with_default_bool(self):
        """Test creating a domain with boolean default."""
        d = domain.Domain(
            name='my_bool',
            schema='public',
            data_type='boolean',
            default=True,
        )
        self.assertTrue(d.default)

    def test_domain_with_check_constraints(self):
        """Test creating a domain with check constraints."""
        cc1 = domain.CheckConstraint(name='positive', expression='VALUE > 0')
        cc2 = domain.CheckConstraint(
            name='max_value', expression='VALUE < 1000'
        )
        d = domain.Domain(
            name='positive_int',
            schema='public',
            data_type='integer',
            check_constraints=[cc1, cc2],
        )
        self.assertEqual(len(d.check_constraints), 2)

    def test_domain_check_constraints_must_be_unique(self):
        """Test that check constraints must be unique."""
        cc = domain.CheckConstraint(expression='VALUE > 0')
        with self.assertRaises(pydantic.ValidationError) as ctx:
            domain.Domain(
                name='positive_int',
                schema='public',
                data_type='integer',
                check_constraints=[cc, cc],
            )
        self.assertIn('must be unique', str(ctx.exception))

    def test_domain_with_comment(self):
        """Test creating a domain with comment."""
        d = domain.Domain(
            name='positive_int',
            schema='public',
            data_type='integer',
            comment='Positive integer values only',
        )
        self.assertEqual(d.comment, 'Positive integer values only')

    def test_domain_with_dependencies(self):
        """Test creating a domain with dependencies."""
        deps = dependencies.Dependencies(extensions=['postgis'])
        d = domain.Domain(
            name='positive_int',
            schema='public',
            data_type='integer',
            dependencies=deps,
        )
        self.assertIsNotNone(d.dependencies)

    def test_domain_complex_configuration(self):
        """Test creating a domain with all fields."""
        cc = domain.CheckConstraint(name='positive', expression='VALUE > 0')
        d = domain.Domain(
            name='positive_int',
            schema='public',
            owner='app_user',
            data_type='integer',
            default=1,
            check_constraints=[cc],
            comment='Positive integers',
        )
        self.assertEqual(d.name, 'positive_int')
        self.assertEqual(d.data_type, 'integer')
        self.assertEqual(d.default, 1)
        self.assertIsNotNone(d.check_constraints)

    def test_domain_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            domain.Domain(
                name='positive_int',
                schema='public',
                data_type='integer',
                invalid_field='value',
            )

    def test_domain_model_dump(self):
        """Test serializing Domain to dict."""
        d = domain.Domain(
            name='positive_int',
            schema='public',
            data_type='integer',
        )
        data = d.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('schema', data)
        self.assertIn('data_type', data)
        self.assertNotIn('comment', data)

    def test_domain_model_dump_json(self):
        """Test serializing Domain to JSON."""
        d = domain.Domain(
            name='positive_int',
            schema='public',
            data_type='integer',
        )
        json_str = d.model_dump_json(exclude_none=True)
        self.assertIn('positive_int', json_str)


if __name__ == '__main__':
    unittest.main()
