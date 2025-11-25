"""Tests for Index Pydantic models."""

import unittest

import pydantic

from elephantic.models import dependencies, index


class TestIndexMethod(unittest.TestCase):
    """Test IndexMethod enum."""

    def test_index_method_values(self):
        """Test IndexMethod enum values."""
        self.assertEqual(index.IndexMethod.BRIN, 'brin')
        self.assertEqual(index.IndexMethod.BTREE, 'btree')
        self.assertEqual(index.IndexMethod.GIN, 'gin')
        self.assertEqual(index.IndexMethod.GIST, 'gist')
        self.assertEqual(index.IndexMethod.HASH, 'hash')
        self.assertEqual(index.IndexMethod.SPGIST, 'spgist')


class TestSortDirection(unittest.TestCase):
    """Test SortDirection enum."""

    def test_sort_direction_values(self):
        """Test SortDirection enum values."""
        self.assertEqual(index.SortDirection.ASC, 'ASC')
        self.assertEqual(index.SortDirection.DESC, 'DESC')


class TestNullPlacement(unittest.TestCase):
    """Test NullPlacement enum."""

    def test_null_placement_values(self):
        """Test NullPlacement enum values."""
        self.assertEqual(index.NullPlacement.FIRST, 'FIRST')
        self.assertEqual(index.NullPlacement.LAST, 'LAST')


class TestIndexColumn(unittest.TestCase):
    """Test IndexColumn model."""

    def test_index_column_requires_name_or_expression(self):
        """Test that name or expression is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            index.IndexColumn()
        self.assertIn(
            'Must specify either name or expression', str(ctx.exception)
        )

    def test_index_column_cannot_have_both_name_and_expression(self):
        """Test that name and expression are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            index.IndexColumn(name='col1', expression='lower(col1)')
        self.assertIn(
            'Cannot specify both name and expression', str(ctx.exception)
        )

    def test_index_column_with_name(self):
        """Test creating index column with name."""
        col = index.IndexColumn(name='col1')
        self.assertEqual(col.name, 'col1')

    def test_index_column_with_expression(self):
        """Test creating index column with expression."""
        col = index.IndexColumn(expression='lower(email)')
        self.assertEqual(col.expression, 'lower(email)')

    def test_index_column_with_collation(self):
        """Test creating index column with collation."""
        col = index.IndexColumn(name='col1', collation='en_US')
        self.assertEqual(col.collation, 'en_US')

    def test_index_column_with_opclass(self):
        """Test creating index column with operator class."""
        col = index.IndexColumn(name='col1', opclass='text_ops')
        self.assertEqual(col.opclass, 'text_ops')

    def test_index_column_with_direction(self):
        """Test creating index column with direction."""
        col = index.IndexColumn(
            name='col1', direction=index.SortDirection.DESC
        )
        self.assertEqual(col.direction, index.SortDirection.DESC)

    def test_index_column_with_null_placement(self):
        """Test creating index column with null placement."""
        col = index.IndexColumn(
            name='col1',
            null_placement=index.NullPlacement.FIRST,
        )
        self.assertEqual(col.null_placement, index.NullPlacement.FIRST)

    def test_index_column_complete_definition(self):
        """Test creating index column with all fields."""
        col = index.IndexColumn(
            name='email',
            collation='C',
            opclass='text_ops',
            direction=index.SortDirection.ASC,
            null_placement=index.NullPlacement.LAST,
        )
        self.assertEqual(col.name, 'email')
        self.assertEqual(col.direction, index.SortDirection.ASC)


class TestIndex(unittest.TestCase):
    """Test Index model."""

    def test_index_with_sql(self):
        """Test creating an index with SQL."""
        idx = index.Index(sql='CREATE INDEX ...')
        self.assertIsNotNone(idx.sql)

    def test_index_requires_sql_or_name_and_columns(self):
        """Test that either sql OR (name and columns) is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            index.Index()
        self.assertIn(
            'Must specify either sql OR (name and columns)', str(ctx.exception)
        )

    def test_index_requires_both_name_and_columns(self):
        """Test that both name and columns are required when not using SQL."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            index.Index(name='idx_test')
        self.assertIn(
            'Must specify either sql OR (name and columns)', str(ctx.exception)
        )

    def test_index_cannot_have_sql_with_name(self):
        """Test that sql and name are mutually exclusive."""
        col = index.IndexColumn(name='col1')
        with self.assertRaises(pydantic.ValidationError) as ctx:
            index.Index(
                sql='CREATE INDEX ...',
                name='idx_test',
                columns=[col],
            )
        self.assertIn(
            'Cannot specify sql with name or columns', str(ctx.exception)
        )

    def test_index_cannot_have_sql_with_structured_fields(self):
        """Test that sql and structured fields are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            index.Index(
                sql='CREATE INDEX ...',
                method=index.IndexMethod.BTREE,
            )
        self.assertIn(
            'Cannot specify sql with structured fields', str(ctx.exception)
        )

    def test_index_with_name_and_columns(self):
        """Test creating index with name and columns."""
        col = index.IndexColumn(name='col1')
        idx = index.Index(
            name='idx_test',
            columns=[col],
        )
        self.assertEqual(idx.name, 'idx_test')
        self.assertEqual(len(idx.columns), 1)

    def test_index_with_multiple_columns(self):
        """Test creating index with multiple columns."""
        col1 = index.IndexColumn(name='col1')
        col2 = index.IndexColumn(name='col2')
        idx = index.Index(
            name='idx_composite',
            columns=[col1, col2],
        )
        self.assertEqual(len(idx.columns), 2)

    def test_index_with_expression_column(self):
        """Test creating index with expression column."""
        col = index.IndexColumn(expression='lower(email)')
        idx = index.Index(
            name='idx_email_lower',
            columns=[col],
        )
        self.assertEqual(idx.columns[0].expression, 'lower(email)')

    def test_index_with_unique(self):
        """Test creating unique index."""
        col = index.IndexColumn(name='email')
        idx = index.Index(
            name='idx_unique_email',
            columns=[col],
            unique=True,
        )
        self.assertTrue(idx.unique)

    def test_index_with_recurse(self):
        """Test creating index with recurse."""
        col = index.IndexColumn(name='col1')
        idx = index.Index(
            name='idx_test',
            columns=[col],
            recurse=True,
        )
        self.assertTrue(idx.recurse)

    def test_index_with_method(self):
        """Test creating index with method."""
        col = index.IndexColumn(name='col1')
        idx = index.Index(
            name='idx_test',
            columns=[col],
            method=index.IndexMethod.GIN,
        )
        self.assertEqual(idx.method, index.IndexMethod.GIN)

    def test_index_with_include(self):
        """Test creating index with include columns."""
        col = index.IndexColumn(name='col1')
        idx = index.Index(
            name='idx_test',
            columns=[col],
            include=['col2', 'col3'],
        )
        self.assertEqual(len(idx.include), 2)

    def test_index_with_storage_parameters(self):
        """Test creating index with storage parameters."""
        col = index.IndexColumn(name='col1')
        idx = index.Index(
            name='idx_test',
            columns=[col],
            storage_parameters={'fillfactor': 70},
        )
        self.assertIsNotNone(idx.storage_parameters)

    def test_index_storage_parameters_validate_names(self):
        """Test that storage parameter names are validated."""
        col = index.IndexColumn(name='col1')
        with self.assertRaises(pydantic.ValidationError) as ctx:
            index.Index(
                name='idx_test',
                columns=[col],
                storage_parameters={'invalid-name!': 'value'},
            )
        self.assertIn('does not match required pattern', str(ctx.exception))

    def test_index_with_tablespace(self):
        """Test creating index with tablespace."""
        col = index.IndexColumn(name='col1')
        idx = index.Index(
            name='idx_test',
            columns=[col],
            tablespace='fast_ssd',
        )
        self.assertEqual(idx.tablespace, 'fast_ssd')

    def test_index_with_where(self):
        """Test creating partial index with where clause."""
        col = index.IndexColumn(name='status')
        idx = index.Index(
            name='idx_active',
            columns=[col],
            where="status = 'active'",
        )
        self.assertIsNotNone(idx.where)

    def test_index_with_comment(self):
        """Test creating index with comment."""
        col = index.IndexColumn(name='col1')
        idx = index.Index(
            name='idx_test',
            columns=[col],
            comment='Test index',
        )
        self.assertEqual(idx.comment, 'Test index')

    def test_index_with_dependencies(self):
        """Test creating index with dependencies."""
        deps = dependencies.Dependencies(functions=['public.my_func()'])
        col = index.IndexColumn(name='col1')
        idx = index.Index(
            name='idx_test',
            columns=[col],
            dependencies=deps,
        )
        self.assertIsNotNone(idx.dependencies)

    def test_index_complete_definition(self):
        """Test creating index with all fields."""
        col1 = index.IndexColumn(
            name='email',
            direction=index.SortDirection.DESC,
            null_placement=index.NullPlacement.LAST,
        )
        col2 = index.IndexColumn(name='created_at')
        idx = index.Index(
            name='idx_email_created',
            columns=[col1, col2],
            unique=True,
            method=index.IndexMethod.BTREE,
            include=['status'],
            storage_parameters={'fillfactor': 80},
            tablespace='indexes',
            where='deleted_at IS NULL',
            comment='Index for active users by email',
        )
        self.assertEqual(idx.name, 'idx_email_created')
        self.assertTrue(idx.unique)
        self.assertEqual(idx.method, index.IndexMethod.BTREE)
        self.assertEqual(len(idx.include), 1)

    def test_index_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        col = index.IndexColumn(name='col1')
        with self.assertRaises(pydantic.ValidationError):
            index.Index(
                name='idx_test',
                columns=[col],
                invalid_field='value',
            )

    def test_index_model_dump(self):
        """Test serializing Index to dict."""
        col = index.IndexColumn(name='col1')
        idx = index.Index(
            name='idx_test',
            columns=[col],
        )
        data = idx.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('columns', data)

    def test_index_model_dump_json(self):
        """Test serializing Index to JSON."""
        col = index.IndexColumn(expression='lower(email)')
        idx = index.Index(
            name='idx_email',
            columns=[col],
            unique=True,
        )
        json_str = idx.model_dump_json(exclude_none=True)
        self.assertIn('idx_email', json_str)


if __name__ == '__main__':
    unittest.main()
