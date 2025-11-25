"""Tests for EventTrigger Pydantic models."""

import unittest

import pydantic

from elephantic.models import dependencies, event_trigger


class TestEvent(unittest.TestCase):
    """Test Event enumeration."""

    def test_event_values(self):
        """Test Event enum values."""
        self.assertEqual(
            event_trigger.Event.DDL_COMMAND_START.value, 'ddl_command_start'
        )
        self.assertEqual(
            event_trigger.Event.DDL_COMMAND_END.value, 'ddl_command_end'
        )
        self.assertEqual(
            event_trigger.Event.TABLE_REWRITE.value, 'table_rewrite'
        )
        self.assertEqual(event_trigger.Event.SQL_DROP.value, 'sql_drop')


class TestFilter(unittest.TestCase):
    """Test Filter model."""

    def test_filter_with_tags(self):
        """Test creating a filter with tags."""
        f = event_trigger.Filter(tags=['DROP FUNCTION', 'DROP TABLE'])
        self.assertEqual(len(f.tags), 2)

    def test_filter_requires_tags(self):
        """Test that tags is required."""
        with self.assertRaises(pydantic.ValidationError):
            event_trigger.Filter()

    def test_filter_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            event_trigger.Filter(tags=['DROP FUNCTION'], invalid_field='value')


class TestEventTrigger(unittest.TestCase):
    """Test EventTrigger model."""

    def test_event_trigger_with_sql(self):
        """Test creating an event trigger with SQL."""
        et = event_trigger.EventTrigger(sql='CREATE EVENT TRIGGER ...')
        self.assertIsNotNone(et.sql)

    def test_event_trigger_with_structured_fields(self):
        """Test creating an event trigger with structured fields."""
        et = event_trigger.EventTrigger(
            name='audit_ddl',
            event=event_trigger.Event.DDL_COMMAND_END,
            function='audit_function',
        )
        self.assertEqual(et.name, 'audit_ddl')
        self.assertEqual(et.event, event_trigger.Event.DDL_COMMAND_END)
        self.assertEqual(et.function, 'audit_function')

    def test_event_trigger_requires_sql_or_structured(self):
        """Test that either sql or structured fields are required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            event_trigger.EventTrigger()
        self.assertIn('Must specify either sql or all of', str(ctx.exception))

    def test_event_trigger_cannot_have_sql_and_structured(self):
        """Test that sql and structured fields are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            event_trigger.EventTrigger(
                sql='CREATE EVENT TRIGGER ...',
                name='audit_ddl',
            )
        self.assertIn(
            'Cannot specify sql with structured fields', str(ctx.exception)
        )

    def test_event_trigger_structured_requires_name(self):
        """Test that structured mode requires name."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            event_trigger.EventTrigger(
                event=event_trigger.Event.DDL_COMMAND_END,
                function='audit_function',
            )
        self.assertIn(
            'Must specify either sql or all of: name, event, and function',
            str(ctx.exception),
        )

    def test_event_trigger_structured_requires_event(self):
        """Test that structured mode requires event."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            event_trigger.EventTrigger(
                name='audit_ddl',
                function='audit_function',
            )
        self.assertIn(
            'Must specify either sql or all of: name, event, and function',
            str(ctx.exception),
        )

    def test_event_trigger_structured_requires_function(self):
        """Test that structured mode requires function."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            event_trigger.EventTrigger(
                name='audit_ddl',
                event=event_trigger.Event.DDL_COMMAND_END,
            )
        self.assertIn(
            'Must specify either sql or all of: name, event, and function',
            str(ctx.exception),
        )

    def test_event_trigger_with_filter(self):
        """Test creating an event trigger with filter."""
        f = event_trigger.Filter(tags=['DROP FUNCTION'])
        et = event_trigger.EventTrigger(
            name='audit_ddl',
            event=event_trigger.Event.DDL_COMMAND_END,
            function='audit_function',
            filter=f,
        )
        self.assertIsNotNone(et.filter)
        self.assertEqual(len(et.filter.tags), 1)

    def test_event_trigger_with_comment(self):
        """Test creating an event trigger with comment."""
        et = event_trigger.EventTrigger(
            name='audit_ddl',
            event=event_trigger.Event.DDL_COMMAND_END,
            function='audit_function',
            comment='Audit DDL changes',
        )
        self.assertEqual(et.comment, 'Audit DDL changes')

    def test_event_trigger_with_dependencies(self):
        """Test creating an event trigger with dependencies."""
        deps = dependencies.Dependencies(functions=['audit.log_changes()'])
        et = event_trigger.EventTrigger(
            name='audit_ddl',
            event=event_trigger.Event.DDL_COMMAND_END,
            function='audit_function',
            dependencies=deps,
        )
        self.assertIsNotNone(et.dependencies)

    def test_event_trigger_complex_configuration(self):
        """Test creating an event trigger with all fields."""
        f = event_trigger.Filter(tags=['DROP FUNCTION', 'DROP TABLE'])
        deps = dependencies.Dependencies(functions=['audit.log_changes()'])
        et = event_trigger.EventTrigger(
            name='audit_ddl',
            event=event_trigger.Event.DDL_COMMAND_END,
            filter=f,
            function='audit_function',
            comment='Audit DDL changes',
            dependencies=deps,
        )
        self.assertEqual(et.name, 'audit_ddl')
        self.assertEqual(et.event, event_trigger.Event.DDL_COMMAND_END)
        self.assertIsNotNone(et.filter)
        self.assertIsNotNone(et.dependencies)

    def test_event_trigger_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            event_trigger.EventTrigger(
                name='audit_ddl',
                event=event_trigger.Event.DDL_COMMAND_END,
                function='audit_function',
                invalid_field='value',
            )

    def test_event_trigger_model_dump(self):
        """Test serializing EventTrigger to dict."""
        et = event_trigger.EventTrigger(
            name='audit_ddl',
            event=event_trigger.Event.DDL_COMMAND_END,
            function='audit_function',
        )
        data = et.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('event', data)
        self.assertIn('function', data)
        self.assertNotIn('comment', data)

    def test_event_trigger_model_dump_json(self):
        """Test serializing EventTrigger to JSON."""
        et = event_trigger.EventTrigger(
            name='audit_ddl',
            event=event_trigger.Event.DDL_COMMAND_END,
            function='audit_function',
        )
        json_str = et.model_dump_json(exclude_none=True)
        self.assertIn('audit_ddl', json_str)


if __name__ == '__main__':
    unittest.main()
