"""Tests for ForeignKey Pydantic models."""

import unittest

import pydantic

from elephantic.models import foreign_key


class TestMatchType(unittest.TestCase):
    """Test MatchType enum."""

    def test_match_type_values(self):
        """Test MatchType enum values."""
        self.assertEqual(foreign_key.MatchType.FULL, 'FULL')
        self.assertEqual(foreign_key.MatchType.PARTIAL, 'PARTIAL')
        self.assertEqual(foreign_key.MatchType.SIMPLE, 'SIMPLE')


class TestReferentialAction(unittest.TestCase):
    """Test ReferentialAction enum."""

    def test_referential_action_values(self):
        """Test ReferentialAction enum values."""
        self.assertEqual(foreign_key.ReferentialAction.NO_ACTION, 'NO ACTION')
        self.assertEqual(foreign_key.ReferentialAction.RESTRICT, 'RESTRICT')
        self.assertEqual(foreign_key.ReferentialAction.CASCADE, 'CASCADE')
        self.assertEqual(foreign_key.ReferentialAction.SET_NULL, 'SET NULL')
        self.assertEqual(
            foreign_key.ReferentialAction.SET_DEFAULT, 'SET DEFAULT'
        )


class TestForeignKeyReference(unittest.TestCase):
    """Test ForeignKeyReference model."""

    def test_foreign_key_reference_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            foreign_key.ForeignKeyReference(columns=['id'])

    def test_foreign_key_reference_requires_columns(self):
        """Test that columns is required."""
        with self.assertRaises(pydantic.ValidationError):
            foreign_key.ForeignKeyReference(name='users')

    def test_foreign_key_reference_with_name_and_columns(self):
        """Test creating reference with name and columns."""
        ref = foreign_key.ForeignKeyReference(
            name='users',
            columns=['id'],
        )
        self.assertEqual(ref.name, 'users')
        self.assertEqual(len(ref.columns), 1)

    def test_foreign_key_reference_with_multiple_columns(self):
        """Test creating reference with multiple columns."""
        ref = foreign_key.ForeignKeyReference(
            name='composite_table',
            columns=['col1', 'col2', 'col3'],
        )
        self.assertEqual(len(ref.columns), 3)


class TestForeignKey(unittest.TestCase):
    """Test ForeignKey model."""

    def test_foreign_key_with_sql(self):
        """Test creating a foreign key with SQL."""
        fk = foreign_key.ForeignKey(sql='ALTER TABLE ...')
        self.assertIsNotNone(fk.sql)

    def test_foreign_key_requires_sql_or_columns(self):
        """Test that either sql or columns is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            foreign_key.ForeignKey(name='fk_test')
        self.assertIn('Must specify either sql or columns', str(ctx.exception))

    def test_foreign_key_cannot_have_both_sql_and_columns(self):
        """Test that sql and columns are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            foreign_key.ForeignKey(
                sql='ALTER TABLE ...',
                columns=['user_id'],
            )
        self.assertIn(
            'Cannot specify both sql and columns', str(ctx.exception)
        )

    def test_foreign_key_cannot_have_sql_with_structured_fields(self):
        """Test that sql and structured fields are mutually exclusive."""
        ref = foreign_key.ForeignKeyReference(name='users', columns=['id'])
        with self.assertRaises(pydantic.ValidationError) as ctx:
            foreign_key.ForeignKey(
                sql='ALTER TABLE ...',
                references=ref,
            )
        self.assertIn(
            'Cannot specify sql with structured fields', str(ctx.exception)
        )

    def test_foreign_key_with_columns(self):
        """Test creating foreign key with columns."""
        fk = foreign_key.ForeignKey(
            name='fk_user',
            columns=['user_id'],
        )
        self.assertEqual(fk.name, 'fk_user')
        self.assertEqual(len(fk.columns), 1)

    def test_foreign_key_with_references(self):
        """Test creating foreign key with references."""
        ref = foreign_key.ForeignKeyReference(name='users', columns=['id'])
        fk = foreign_key.ForeignKey(
            name='fk_user',
            columns=['user_id'],
            references=ref,
        )
        self.assertEqual(fk.references.name, 'users')
        self.assertEqual(len(fk.references.columns), 1)

    def test_foreign_key_with_match_type(self):
        """Test creating foreign key with match_type."""
        fk = foreign_key.ForeignKey(
            columns=['user_id'],
            match_type=foreign_key.MatchType.FULL,
        )
        self.assertEqual(fk.match_type, foreign_key.MatchType.FULL)

    def test_foreign_key_with_on_delete(self):
        """Test creating foreign key with on_delete."""
        fk = foreign_key.ForeignKey(
            columns=['user_id'],
            on_delete=foreign_key.ReferentialAction.CASCADE,
        )
        self.assertEqual(fk.on_delete, foreign_key.ReferentialAction.CASCADE)

    def test_foreign_key_with_on_update(self):
        """Test creating foreign key with on_update."""
        fk = foreign_key.ForeignKey(
            columns=['user_id'],
            on_update=foreign_key.ReferentialAction.SET_NULL,
        )
        self.assertEqual(fk.on_update, foreign_key.ReferentialAction.SET_NULL)

    def test_foreign_key_with_deferrable(self):
        """Test creating foreign key with deferrable."""
        fk = foreign_key.ForeignKey(
            columns=['user_id'],
            deferrable=True,
        )
        self.assertTrue(fk.deferrable)

    def test_foreign_key_with_initially_deferred(self):
        """Test creating foreign key with initially_deferred."""
        fk = foreign_key.ForeignKey(
            columns=['user_id'],
            initially_deferred=True,
        )
        self.assertTrue(fk.initially_deferred)

    def test_foreign_key_complete_definition(self):
        """Test creating foreign key with all fields."""
        ref = foreign_key.ForeignKeyReference(name='users', columns=['id'])
        fk = foreign_key.ForeignKey(
            name='fk_order_user',
            columns=['user_id'],
            references=ref,
            match_type=foreign_key.MatchType.SIMPLE,
            on_delete=foreign_key.ReferentialAction.CASCADE,
            on_update=foreign_key.ReferentialAction.RESTRICT,
            deferrable=True,
            initially_deferred=False,
        )
        self.assertEqual(fk.name, 'fk_order_user')
        self.assertEqual(fk.match_type, foreign_key.MatchType.SIMPLE)
        self.assertTrue(fk.deferrable)
        self.assertFalse(fk.initially_deferred)

    def test_foreign_key_with_composite_key(self):
        """Test creating foreign key with composite columns."""
        ref = foreign_key.ForeignKeyReference(
            name='composite_table',
            columns=['col1', 'col2'],
        )
        fk = foreign_key.ForeignKey(
            name='fk_composite',
            columns=['ref_col1', 'ref_col2'],
            references=ref,
        )
        self.assertEqual(len(fk.columns), 2)
        self.assertEqual(len(fk.references.columns), 2)

    def test_foreign_key_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            foreign_key.ForeignKey(
                columns=['user_id'],
                invalid_field='value',
            )

    def test_foreign_key_model_dump(self):
        """Test serializing ForeignKey to dict."""
        fk = foreign_key.ForeignKey(
            name='fk_test',
            columns=['user_id'],
        )
        data = fk.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('columns', data)

    def test_foreign_key_model_dump_json(self):
        """Test serializing ForeignKey to JSON."""
        ref = foreign_key.ForeignKeyReference(name='users', columns=['id'])
        fk = foreign_key.ForeignKey(
            name='fk_user',
            columns=['user_id'],
            references=ref,
        )
        json_str = fk.model_dump_json(exclude_none=True)
        self.assertIn('fk_user', json_str)


if __name__ == '__main__':
    unittest.main()
