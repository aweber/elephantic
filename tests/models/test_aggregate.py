"""Tests for Aggregate Pydantic models."""

import unittest

import pydantic

from elephantic.models import aggregate, argument, dependencies


class TestFinalFuncModify(unittest.TestCase):
    """Test FinalFuncModify enumeration."""

    def test_final_func_modify_values(self):
        """Test FinalFuncModify enum values."""
        self.assertEqual(
            aggregate.FinalFuncModify.READ_ONLY.value, 'READ_ONLY'
        )
        self.assertEqual(
            aggregate.FinalFuncModify.SHAREABLE.value, 'SHAREABLE'
        )
        self.assertEqual(
            aggregate.FinalFuncModify.READ_WRITE.value, 'READ_WRITE'
        )


class TestParallelSafety(unittest.TestCase):
    """Test ParallelSafety enumeration."""

    def test_parallel_safety_values(self):
        """Test ParallelSafety enum values."""
        self.assertEqual(aggregate.ParallelSafety.SAFE.value, 'SAFE')
        self.assertEqual(
            aggregate.ParallelSafety.RESTRICTED.value, 'RESTRICTED'
        )
        self.assertEqual(aggregate.ParallelSafety.UNSAFE.value, 'UNSAFE')


class TestAggregate(unittest.TestCase):
    """Test Aggregate model."""

    def test_aggregate_with_sql(self):
        """Test creating an aggregate with raw SQL."""
        agg = aggregate.Aggregate(
            name='my_agg',
            schema='public',
            sql='CREATE AGGREGATE public.my_agg(...)',
        )
        self.assertEqual(agg.name, 'my_agg')
        self.assertEqual(agg.schema, 'public')
        self.assertIsNotNone(agg.sql)
        self.assertIsNone(agg.arguments)
        self.assertIsNone(agg.sfunc)

    def test_aggregate_with_components(self):
        """Test creating an aggregate with component functions."""
        agg = aggregate.Aggregate(
            name='my_agg',
            schema='public',
            arguments=[argument.Argument(data_type='integer')],
            sfunc='my_state_func',
            state_data_type='integer',
        )
        self.assertEqual(agg.name, 'my_agg')
        self.assertEqual(agg.schema, 'public')
        self.assertEqual(len(agg.arguments), 1)
        self.assertEqual(agg.sfunc, 'my_state_func')
        self.assertEqual(agg.state_data_type, 'integer')

    def test_aggregate_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            aggregate.Aggregate(schema='public')

    def test_aggregate_requires_schema(self):
        """Test that schema is required."""
        with self.assertRaises(pydantic.ValidationError):
            aggregate.Aggregate(name='my_agg')

    def test_aggregate_sql_excludes_components(self):
        """Test that sql cannot be used with component fields."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            aggregate.Aggregate(
                name='my_agg',
                schema='public',
                sql='CREATE AGGREGATE...',
                arguments=[argument.Argument(data_type='integer')],
            )
        self.assertIn(
            'Cannot specify both sql and component', str(ctx.exception)
        )

    def test_aggregate_requires_essential_components(self):
        """Test that essential components are required when not using sql."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            aggregate.Aggregate(
                name='my_agg',
                schema='public',
                arguments=[argument.Argument(data_type='integer')],
            )
        self.assertIn(
            'must specify arguments, sfunc, and state_data_type',
            str(ctx.exception),
        )

    def test_aggregate_with_owner(self):
        """Test aggregate with owner."""
        agg = aggregate.Aggregate(
            name='my_agg',
            schema='public',
            owner='postgres',
            sql='CREATE AGGREGATE...',
        )
        self.assertEqual(agg.owner, 'postgres')

    def test_aggregate_with_comment(self):
        """Test aggregate with comment."""
        agg = aggregate.Aggregate(
            name='my_agg',
            schema='public',
            sql='CREATE AGGREGATE...',
            comment='Test aggregate',
        )
        self.assertEqual(agg.comment, 'Test aggregate')

    def test_aggregate_with_dependencies(self):
        """Test aggregate with dependencies."""
        deps = dependencies.Dependencies(functions=['public.my_func()'])
        agg = aggregate.Aggregate(
            name='my_agg',
            schema='public',
            sql='CREATE AGGREGATE...',
            dependencies=deps,
        )
        self.assertIsNotNone(agg.dependencies)
        self.assertEqual(len(agg.dependencies.functions), 1)

    def test_aggregate_with_final_function(self):
        """Test aggregate with final function."""
        agg = aggregate.Aggregate(
            name='my_agg',
            schema='public',
            arguments=[argument.Argument(data_type='integer')],
            sfunc='my_state_func',
            state_data_type='integer',
            ffunc='my_final_func',
        )
        self.assertEqual(agg.ffunc, 'my_final_func')

    def test_aggregate_with_finalfunc_modify(self):
        """Test aggregate with finalfunc_modify."""
        agg = aggregate.Aggregate(
            name='my_agg',
            schema='public',
            arguments=[argument.Argument(data_type='integer')],
            sfunc='my_state_func',
            state_data_type='integer',
            finalfunc_modify=aggregate.FinalFuncModify.READ_ONLY,
        )
        self.assertEqual(
            agg.finalfunc_modify,
            aggregate.FinalFuncModify.READ_ONLY,
        )

    def test_aggregate_with_parallel_safety(self):
        """Test aggregate with parallel safety."""
        agg = aggregate.Aggregate(
            name='my_agg',
            schema='public',
            arguments=[argument.Argument(data_type='integer')],
            sfunc='my_state_func',
            state_data_type='integer',
            parallel=aggregate.ParallelSafety.SAFE,
        )
        self.assertEqual(agg.parallel, aggregate.ParallelSafety.SAFE)

    def test_aggregate_with_moving_aggregate_mode(self):
        """Test aggregate with moving-aggregate mode fields."""
        agg = aggregate.Aggregate(
            name='my_agg',
            schema='public',
            arguments=[argument.Argument(data_type='integer')],
            sfunc='my_state_func',
            state_data_type='integer',
            msfunc='my_moving_state_func',
            mstate_data_type='integer',
        )
        self.assertEqual(agg.msfunc, 'my_moving_state_func')
        self.assertEqual(agg.mstate_data_type, 'integer')

    def test_aggregate_with_ordered_set_arguments(self):
        """Test aggregate with ordered-set arguments."""
        agg = aggregate.Aggregate(
            name='my_agg',
            schema='public',
            arguments=[argument.Argument(data_type='integer')],
            order_by=[argument.Argument(data_type='integer')],
            sfunc='my_state_func',
            state_data_type='integer',
        )
        self.assertEqual(len(agg.order_by), 1)

    def test_aggregate_with_hypothetical(self):
        """Test aggregate with hypothetical flag."""
        agg = aggregate.Aggregate(
            name='my_agg',
            schema='public',
            arguments=[argument.Argument(data_type='integer')],
            sfunc='my_state_func',
            state_data_type='integer',
            hypothetical=True,
        )
        self.assertTrue(agg.hypothetical)

    def test_aggregate_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            aggregate.Aggregate(
                name='my_agg',
                schema='public',
                sql='CREATE AGGREGATE...',
                invalid_field='value',
            )

    def test_aggregate_model_dump(self):
        """Test serializing Aggregate to dict."""
        agg = aggregate.Aggregate(
            name='my_agg',
            schema='public',
            sql='CREATE AGGREGATE...',
        )
        data = agg.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('schema', data)
        self.assertIn('sql', data)
        self.assertNotIn('arguments', data)

    def test_aggregate_model_dump_json(self):
        """Test serializing Aggregate to JSON."""
        agg = aggregate.Aggregate(
            name='my_agg',
            schema='public',
            sql='CREATE AGGREGATE...',
        )
        json_str = agg.model_dump_json(exclude_none=True)
        self.assertIn('my_agg', json_str)
        self.assertIn('public', json_str)


if __name__ == '__main__':
    unittest.main()
