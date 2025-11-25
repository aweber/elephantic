"""Tests for View Pydantic models."""

import unittest

import pydantic

from elephantic.models import dependencies, view


class TestCheckOption(unittest.TestCase):
    """Test CheckOption enum."""

    def test_check_option_values(self):
        """Test CheckOption enum values."""
        self.assertEqual(view.CheckOption.LOCAL, 'LOCAL')
        self.assertEqual(view.CheckOption.CASCADED, 'CASCADED')


class TestViewColumn(unittest.TestCase):
    """Test ViewColumn model."""

    def test_view_column_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            view.ViewColumn()

    def test_view_column_with_name(self):
        """Test creating view column with name."""
        col = view.ViewColumn(name='col1')
        self.assertEqual(col.name, 'col1')

    def test_view_column_with_comment(self):
        """Test creating view column with comment."""
        col = view.ViewColumn(name='col1', comment='Test column')
        self.assertEqual(col.comment, 'Test column')


class TestView(unittest.TestCase):
    """Test View model."""

    def test_view_requires_schema(self):
        """Test that schema is required."""
        with self.assertRaises(pydantic.ValidationError):
            view.View(name='v_test', query='SELECT 1')

    def test_view_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            view.View(schema='public', query='SELECT 1')

    def test_view_with_sql(self):
        """Test creating a view with SQL."""
        v = view.View(
            schema='public',
            name='v_test',
            sql='CREATE VIEW ...',
        )
        self.assertIsNotNone(v.sql)

    def test_view_requires_sql_or_query(self):
        """Test that either sql or query is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            view.View(
                schema='public',
                name='v_test',
            )
        self.assertIn('Must specify either sql or query', str(ctx.exception))

    def test_view_cannot_have_both_sql_and_query(self):
        """Test that sql and query are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            view.View(
                schema='public',
                name='v_test',
                sql='CREATE VIEW ...',
                query='SELECT 1',
            )
        self.assertIn('Cannot specify both sql and query', str(ctx.exception))

    def test_view_cannot_have_sql_with_structured_fields(self):
        """Test that sql and structured fields are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            view.View(
                schema='public',
                name='v_test',
                sql='CREATE VIEW ...',
                recursive=True,
            )
        self.assertIn(
            'Cannot specify sql with structured fields', str(ctx.exception)
        )

    def test_view_with_query(self):
        """Test creating view with query."""
        v = view.View(
            schema='public',
            name='v_users',
            query='SELECT id, name FROM users',
        )
        self.assertEqual(v.name, 'v_users')
        self.assertIsNotNone(v.query)

    def test_view_with_owner(self):
        """Test creating view with owner."""
        v = view.View(
            schema='public',
            name='v_test',
            query='SELECT 1',
            owner='app_user',
        )
        self.assertEqual(v.owner, 'app_user')

    def test_view_with_recursive(self):
        """Test creating recursive view."""
        v = view.View(
            schema='public',
            name='v_recursive',
            query='SELECT 1',
            recursive=True,
        )
        self.assertTrue(v.recursive)

    def test_view_with_columns_as_strings(self):
        """Test creating view with columns as strings."""
        v = view.View(
            schema='public',
            name='v_test',
            query='SELECT 1',
            columns=['col1', 'col2'],
        )
        self.assertEqual(len(v.columns), 2)
        self.assertEqual(v.columns[0], 'col1')

    def test_view_with_columns_as_objects(self):
        """Test creating view with columns as ViewColumn objects."""
        col1 = view.ViewColumn(name='col1', comment='First column')
        col2 = view.ViewColumn(name='col2')
        v = view.View(
            schema='public',
            name='v_test',
            query='SELECT 1',
            columns=[col1, col2],
        )
        self.assertEqual(len(v.columns), 2)
        self.assertEqual(v.columns[0].name, 'col1')

    def test_view_with_mixed_columns(self):
        """Test creating view with mixed string and object columns."""
        col1 = view.ViewColumn(name='col1', comment='First column')
        v = view.View(
            schema='public',
            name='v_test',
            query='SELECT 1',
            columns=[col1, 'col2'],
        )
        self.assertEqual(len(v.columns), 2)

    def test_view_with_check_option(self):
        """Test creating view with check_option."""
        v = view.View(
            schema='public',
            name='v_test',
            query='SELECT 1',
            check_option=view.CheckOption.LOCAL,
        )
        self.assertEqual(v.check_option, view.CheckOption.LOCAL)

    def test_view_with_security_barrier(self):
        """Test creating view with security_barrier."""
        v = view.View(
            schema='public',
            name='v_secure',
            query='SELECT 1',
            security_barrier=True,
        )
        self.assertTrue(v.security_barrier)

    def test_view_with_comment(self):
        """Test creating view with comment."""
        v = view.View(
            schema='public',
            name='v_test',
            query='SELECT 1',
            comment='Test view',
        )
        self.assertEqual(v.comment, 'Test view')

    def test_view_with_dependencies(self):
        """Test creating view with dependencies."""
        deps = dependencies.Dependencies(functions=['public.my_func()'])
        v = view.View(
            schema='public',
            name='v_test',
            query='SELECT my_func()',
            dependencies=deps,
        )
        self.assertIsNotNone(v.dependencies)

    def test_view_complete_definition(self):
        """Test creating view with all fields."""
        col1 = view.ViewColumn(name='user_id')
        col2 = view.ViewColumn(name='email', comment='User email')
        deps = dependencies.Dependencies(functions=['public.active_users()'])
        v = view.View(
            schema='public',
            name='v_active_users',
            owner='app_user',
            query='SELECT * FROM active_users()',
            columns=[col1, col2],
            check_option=view.CheckOption.CASCADED,
            security_barrier=True,
            comment='View of active users only',
            dependencies=deps,
        )
        self.assertEqual(v.name, 'v_active_users')
        self.assertEqual(len(v.columns), 2)
        self.assertTrue(v.security_barrier)

    def test_view_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            view.View(
                schema='public',
                name='v_test',
                query='SELECT 1',
                invalid_field='value',
            )

    def test_view_model_dump(self):
        """Test serializing View to dict."""
        v = view.View(
            schema='public',
            name='v_test',
            query='SELECT 1',
        )
        data = v.model_dump(exclude_none=True)
        self.assertIn('schema', data)
        self.assertIn('name', data)
        self.assertIn('query', data)

    def test_view_model_dump_json(self):
        """Test serializing View to JSON."""
        v = view.View(
            schema='public',
            name='v_users',
            query='SELECT * FROM users',
        )
        json_str = v.model_dump_json(exclude_none=True)
        self.assertIn('v_users', json_str)


if __name__ == '__main__':
    unittest.main()
