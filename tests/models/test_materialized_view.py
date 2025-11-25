"""Tests for MaterializedView Pydantic models."""

import unittest

import pydantic

from elephantic.models import dependencies, materialized_view


class TestMaterializedViewColumn(unittest.TestCase):
    """Test MaterializedViewColumn model."""

    def test_materialized_view_column_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            materialized_view.MaterializedViewColumn()

    def test_materialized_view_column_with_name(self):
        """Test creating materialized view column with name."""
        col = materialized_view.MaterializedViewColumn(name='col1')
        self.assertEqual(col.name, 'col1')

    def test_materialized_view_column_with_comment(self):
        """Test creating materialized view column with comment."""
        col = materialized_view.MaterializedViewColumn(
            name='col1', comment='Test column'
        )
        self.assertEqual(col.comment, 'Test column')


class TestMaterializedView(unittest.TestCase):
    """Test MaterializedView model."""

    def test_materialized_view_requires_schema(self):
        """Test that schema is required."""
        with self.assertRaises(pydantic.ValidationError):
            materialized_view.MaterializedView(
                name='mv_test', query='SELECT 1'
            )

    def test_materialized_view_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            materialized_view.MaterializedView(
                schema='public', query='SELECT 1'
            )

    def test_materialized_view_with_sql(self):
        """Test creating a materialized view with SQL."""
        mv = materialized_view.MaterializedView(
            schema='public',
            name='mv_test',
            sql='CREATE MATERIALIZED VIEW ...',
        )
        self.assertIsNotNone(mv.sql)

    def test_materialized_view_requires_sql_or_query(self):
        """Test that either sql or query is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            materialized_view.MaterializedView(
                schema='public',
                name='mv_test',
            )
        self.assertIn('Must specify either sql or query', str(ctx.exception))

    def test_materialized_view_cannot_have_both_sql_and_query(self):
        """Test that sql and query are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            materialized_view.MaterializedView(
                schema='public',
                name='mv_test',
                sql='CREATE MATERIALIZED VIEW ...',
                query='SELECT 1',
            )
        self.assertIn('Cannot specify both sql and query', str(ctx.exception))

    def test_materialized_view_cannot_have_sql_with_structured_fields(self):
        """Test that sql and structured fields are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            materialized_view.MaterializedView(
                schema='public',
                name='mv_test',
                sql='CREATE MATERIALIZED VIEW ...',
                tablespace='fast_ssd',
            )
        self.assertIn(
            'Cannot specify sql with structured fields', str(ctx.exception)
        )

    def test_materialized_view_with_query(self):
        """Test creating materialized view with query."""
        mv = materialized_view.MaterializedView(
            schema='public',
            name='mv_users',
            query='SELECT id, name FROM users',
        )
        self.assertEqual(mv.name, 'mv_users')
        self.assertIsNotNone(mv.query)

    def test_materialized_view_with_owner(self):
        """Test creating materialized view with owner."""
        mv = materialized_view.MaterializedView(
            schema='public',
            name='mv_test',
            query='SELECT 1',
            owner='app_user',
        )
        self.assertEqual(mv.owner, 'app_user')

    def test_materialized_view_with_columns_as_strings(self):
        """Test creating materialized view with columns as strings."""
        mv = materialized_view.MaterializedView(
            schema='public',
            name='mv_test',
            query='SELECT 1',
            columns=['col1', 'col2'],
        )
        self.assertEqual(len(mv.columns), 2)
        self.assertEqual(mv.columns[0], 'col1')

    def test_materialized_view_with_columns_as_objects(self):
        """Test creating materialized view with columns as objects."""
        col1 = materialized_view.MaterializedViewColumn(
            name='col1', comment='First column'
        )
        col2 = materialized_view.MaterializedViewColumn(name='col2')
        mv = materialized_view.MaterializedView(
            schema='public',
            name='mv_test',
            query='SELECT 1',
            columns=[col1, col2],
        )
        self.assertEqual(len(mv.columns), 2)
        self.assertEqual(mv.columns[0].name, 'col1')

    def test_materialized_view_with_table_access_method(self):
        """Test creating materialized view with table_access_method."""
        mv = materialized_view.MaterializedView(
            schema='public',
            name='mv_test',
            query='SELECT 1',
            table_access_method='heap',
        )
        self.assertEqual(mv.table_access_method, 'heap')

    def test_materialized_view_with_storage_parameters(self):
        """Test creating materialized view with storage_parameters."""
        mv = materialized_view.MaterializedView(
            schema='public',
            name='mv_test',
            query='SELECT 1',
            storage_parameters={'fillfactor': 70},
        )
        self.assertIsNotNone(mv.storage_parameters)

    def test_materialized_view_storage_parameters_validate_names(self):
        """Test that storage parameter names are validated."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            materialized_view.MaterializedView(
                schema='public',
                name='mv_test',
                query='SELECT 1',
                storage_parameters={'invalid-name!': 'value'},
            )
        self.assertIn('does not match required pattern', str(ctx.exception))

    def test_materialized_view_with_tablespace(self):
        """Test creating materialized view with tablespace."""
        mv = materialized_view.MaterializedView(
            schema='public',
            name='mv_test',
            query='SELECT 1',
            tablespace='fast_ssd',
        )
        self.assertEqual(mv.tablespace, 'fast_ssd')

    def test_materialized_view_with_comment(self):
        """Test creating materialized view with comment."""
        mv = materialized_view.MaterializedView(
            schema='public',
            name='mv_test',
            query='SELECT 1',
            comment='Test materialized view',
        )
        self.assertEqual(mv.comment, 'Test materialized view')

    def test_materialized_view_with_dependencies(self):
        """Test creating materialized view with dependencies."""
        deps = dependencies.Dependencies(functions=['public.my_func()'])
        mv = materialized_view.MaterializedView(
            schema='public',
            name='mv_test',
            query='SELECT my_func()',
            dependencies=deps,
        )
        self.assertIsNotNone(mv.dependencies)

    def test_materialized_view_complete_definition(self):
        """Test creating materialized view with all fields."""
        col1 = materialized_view.MaterializedViewColumn(name='user_id')
        col2 = materialized_view.MaterializedViewColumn(
            name='email', comment='User email'
        )
        deps = dependencies.Dependencies(functions=['public.active_users()'])
        mv = materialized_view.MaterializedView(
            schema='public',
            name='mv_active_users',
            owner='app_user',
            query='SELECT * FROM active_users()',
            columns=[col1, col2],
            table_access_method='heap',
            storage_parameters={'fillfactor': 80},
            tablespace='indexes',
            comment='Materialized view of active users',
            dependencies=deps,
        )
        self.assertEqual(mv.name, 'mv_active_users')
        self.assertEqual(len(mv.columns), 2)
        self.assertEqual(mv.tablespace, 'indexes')

    def test_materialized_view_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            materialized_view.MaterializedView(
                schema='public',
                name='mv_test',
                query='SELECT 1',
                invalid_field='value',
            )

    def test_materialized_view_model_dump(self):
        """Test serializing MaterializedView to dict."""
        mv = materialized_view.MaterializedView(
            schema='public',
            name='mv_test',
            query='SELECT 1',
        )
        data = mv.model_dump(exclude_none=True)
        self.assertIn('schema', data)
        self.assertIn('name', data)
        self.assertIn('query', data)

    def test_materialized_view_model_dump_json(self):
        """Test serializing MaterializedView to JSON."""
        mv = materialized_view.MaterializedView(
            schema='public',
            name='mv_users',
            query='SELECT * FROM users',
        )
        json_str = mv.model_dump_json(exclude_none=True)
        self.assertIn('mv_users', json_str)


if __name__ == '__main__':
    unittest.main()
