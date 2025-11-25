"""Tests for Function Pydantic models."""

import unittest

import pydantic

from elephantic.models import dependencies, function


class TestParameterMode(unittest.TestCase):
    """Test ParameterMode enumeration."""

    def test_parameter_mode_values(self):
        """Test ParameterMode enum values."""
        self.assertEqual(function.ParameterMode.IN.value, 'IN')
        self.assertEqual(function.ParameterMode.OUT.value, 'OUT')
        self.assertEqual(function.ParameterMode.BOTH.value, 'BOTH')
        self.assertEqual(function.ParameterMode.VARIADIC.value, 'VARIADIC')
        self.assertEqual(function.ParameterMode.TABLE.value, 'TABLE')


class TestSecurity(unittest.TestCase):
    """Test Security enumeration."""

    def test_security_values(self):
        """Test Security enum values."""
        self.assertEqual(function.Security.INVOKER.value, 'INVOKER')
        self.assertEqual(function.Security.DEFINER.value, 'DEFINER')


class TestParallel(unittest.TestCase):
    """Test Parallel enumeration."""

    def test_parallel_values(self):
        """Test Parallel enum values."""
        self.assertEqual(function.Parallel.SAFE.value, 'SAFE')
        self.assertEqual(function.Parallel.UNSAFE.value, 'UNSAFE')
        self.assertEqual(function.Parallel.RESTRICTED.value, 'RESTRICTED')


class TestParameter(unittest.TestCase):
    """Test Parameter model."""

    def test_parameter_with_mode_and_data_type(self):
        """Test creating a parameter with mode and data_type."""
        p = function.Parameter(
            mode=function.ParameterMode.IN, data_type='integer'
        )
        self.assertEqual(p.mode, function.ParameterMode.IN)
        self.assertEqual(p.data_type, 'integer')

    def test_parameter_requires_mode(self):
        """Test that mode is required."""
        with self.assertRaises(pydantic.ValidationError):
            function.Parameter(data_type='integer')

    def test_parameter_requires_data_type(self):
        """Test that data_type is required."""
        with self.assertRaises(pydantic.ValidationError):
            function.Parameter(mode=function.ParameterMode.IN)

    def test_parameter_with_name(self):
        """Test creating a parameter with name."""
        p = function.Parameter(
            mode=function.ParameterMode.IN,
            name='x',
            data_type='integer',
        )
        self.assertEqual(p.name, 'x')

    def test_parameter_with_default(self):
        """Test creating a parameter with default value."""
        p = function.Parameter(
            mode=function.ParameterMode.IN,
            data_type='integer',
            default=42,
        )
        self.assertEqual(p.default, 42)


class TestFunction(unittest.TestCase):
    """Test Function model."""

    def test_function_with_sql(self):
        """Test creating a function with SQL."""
        f = function.Function(
            schema='public',
            name='my_func',
            sql='CREATE FUNCTION ...',
        )
        self.assertEqual(f.schema, 'public')
        self.assertEqual(f.name, 'my_func')
        self.assertIsNotNone(f.sql)

    def test_function_with_structured_fields(self):
        """Test creating a function with structured fields."""
        f = function.Function(
            schema='public',
            name='my_func',
            language='plpgsql',
            returns='integer',
            definition='BEGIN RETURN 42; END;',
        )
        self.assertEqual(f.language, 'plpgsql')
        self.assertEqual(f.returns, 'integer')

    def test_function_requires_schema(self):
        """Test that schema is required."""
        with self.assertRaises(pydantic.ValidationError):
            function.Function(
                name='my_func',
                language='plpgsql',
                returns='integer',
                definition='...',
            )

    def test_function_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            function.Function(
                schema='public',
                language='plpgsql',
                returns='integer',
                definition='...',
            )

    def test_function_requires_language_returns_definition(self):
        """Test that structured mode requires language, returns, and definition."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            function.Function(
                schema='public',
                name='my_func',
            )
        self.assertIn('Must specify either sql or all of', str(ctx.exception))

    def test_function_cannot_have_sql_and_structured(self):
        """Test that sql and structured fields are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            function.Function(
                schema='public',
                name='my_func',
                sql='CREATE FUNCTION ...',
                returns='integer',
            )
        self.assertIn(
            'Cannot specify sql with structured fields', str(ctx.exception)
        )

    def test_function_with_parameters(self):
        """Test creating a function with parameters."""
        p = function.Parameter(
            mode=function.ParameterMode.IN, data_type='integer'
        )
        f = function.Function(
            schema='public',
            name='my_func',
            language='plpgsql',
            returns='integer',
            definition='...',
            parameters=[p],
        )
        self.assertEqual(len(f.parameters), 1)

    def test_function_with_owner(self):
        """Test creating a function with owner."""
        f = function.Function(
            schema='public',
            name='my_func',
            language='plpgsql',
            returns='integer',
            definition='...',
            owner='app_user',
        )
        self.assertEqual(f.owner, 'app_user')

    def test_function_with_transform_types(self):
        """Test creating a function with transform_types."""
        f = function.Function(
            schema='public',
            name='my_func',
            language='plpgsql',
            returns='integer',
            definition='...',
            transform_types=['type1', 'type2'],
        )
        self.assertEqual(len(f.transform_types), 2)

    def test_function_with_window(self):
        """Test creating a function with window flag."""
        f = function.Function(
            schema='public',
            name='my_func',
            language='c',
            returns='integer',
            definition='...',
            window=True,
        )
        self.assertTrue(f.window)

    def test_function_with_immutable(self):
        """Test creating a function with immutable flag."""
        f = function.Function(
            schema='public',
            name='my_func',
            language='plpgsql',
            returns='integer',
            definition='...',
            immutable=True,
        )
        self.assertTrue(f.immutable)

    def test_function_with_security(self):
        """Test creating a function with security mode."""
        f = function.Function(
            schema='public',
            name='my_func',
            language='plpgsql',
            returns='integer',
            definition='...',
            security=function.Security.DEFINER,
        )
        self.assertEqual(f.security, function.Security.DEFINER)

    def test_function_with_parallel(self):
        """Test creating a function with parallel mode."""
        f = function.Function(
            schema='public',
            name='my_func',
            language='plpgsql',
            returns='integer',
            definition='...',
            parallel=function.Parallel.SAFE,
        )
        self.assertEqual(f.parallel, function.Parallel.SAFE)

    def test_function_with_cost(self):
        """Test creating a function with cost."""
        f = function.Function(
            schema='public',
            name='my_func',
            language='plpgsql',
            returns='integer',
            definition='...',
            cost=100,
        )
        self.assertEqual(f.cost, 100)

    def test_function_with_configuration(self):
        """Test creating a function with configuration."""
        f = function.Function(
            schema='public',
            name='my_func',
            language='plpgsql',
            returns='integer',
            definition='...',
            configuration={'work_mem': '64MB'},
        )
        self.assertIsNotNone(f.configuration)

    def test_function_configuration_validates_names(self):
        """Test that configuration parameter names are validated."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            function.Function(
                schema='public',
                name='my_func',
                language='plpgsql',
                returns='integer',
                definition='...',
                configuration={'invalid-name!': 'value'},
            )
        self.assertIn('does not match required pattern', str(ctx.exception))

    def test_function_defaults(self):
        """Test Function default values."""
        f = function.Function(
            schema='public',
            name='my_func',
            language='plpgsql',
            returns='integer',
            definition='...',
        )
        self.assertTrue(f.called_on_null_input)
        self.assertFalse(f.strict)

    def test_function_with_dependencies(self):
        """Test creating a function with dependencies."""
        deps = dependencies.Dependencies(types=['public.my_type'])
        f = function.Function(
            schema='public',
            name='my_func',
            language='plpgsql',
            returns='integer',
            definition='...',
            dependencies=deps,
        )
        self.assertIsNotNone(f.dependencies)

    def test_function_complex_configuration(self):
        """Test creating a function with many fields."""
        p = function.Parameter(
            mode=function.ParameterMode.IN,
            name='x',
            data_type='integer',
        )
        f = function.Function(
            schema='public',
            name='my_func',
            owner='app_user',
            language='plpgsql',
            returns='integer',
            definition='BEGIN RETURN x * 2; END;',
            parameters=[p],
            immutable=True,
            security=function.Security.INVOKER,
            parallel=function.Parallel.SAFE,
            cost=50,
            comment='Doubles the input',
        )
        self.assertEqual(f.name, 'my_func')
        self.assertTrue(f.immutable)
        self.assertEqual(f.cost, 50)

    def test_function_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            function.Function(
                schema='public',
                name='my_func',
                language='plpgsql',
                returns='integer',
                definition='...',
                invalid_field='value',
            )


if __name__ == '__main__':
    unittest.main()
