"""Tests for Trigger Pydantic models."""

import unittest

import pydantic

from elephantic.models import dependencies, trigger


class TestTriggerWhen(unittest.TestCase):
    """Test TriggerWhen enum."""

    def test_trigger_when_values(self):
        """Test TriggerWhen enum values."""
        self.assertEqual(trigger.TriggerWhen.BEFORE, 'BEFORE')
        self.assertEqual(trigger.TriggerWhen.AFTER, 'AFTER')
        self.assertEqual(trigger.TriggerWhen.INSTEAD_OF, 'INSTEAD OF')


class TestTriggerEvent(unittest.TestCase):
    """Test TriggerEvent enum."""

    def test_trigger_event_values(self):
        """Test TriggerEvent enum values."""
        self.assertEqual(trigger.TriggerEvent.INSERT, 'INSERT')
        self.assertEqual(trigger.TriggerEvent.UPDATE, 'UPDATE')
        self.assertEqual(trigger.TriggerEvent.DELETE, 'DELETE')
        self.assertEqual(trigger.TriggerEvent.TRUNCATE, 'TRUNCATE')


class TestTriggerForEach(unittest.TestCase):
    """Test TriggerForEach enum."""

    def test_trigger_for_each_values(self):
        """Test TriggerForEach enum values."""
        self.assertEqual(trigger.TriggerForEach.ROW, 'ROW')
        self.assertEqual(trigger.TriggerForEach.STATEMENT, 'STATEMENT')


class TestTrigger(unittest.TestCase):
    """Test Trigger model."""

    def test_trigger_with_sql(self):
        """Test creating a trigger with SQL."""
        trg = trigger.Trigger(sql='CREATE TRIGGER ...')
        self.assertIsNotNone(trg.sql)

    def test_trigger_requires_sql_or_structured_fields(self):
        """Test that either sql OR required fields must be provided."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            trigger.Trigger()
        self.assertIn(
            'Must specify either sql OR (name, when, events, and function)',
            str(ctx.exception),
        )

    def test_trigger_requires_all_required_fields(self):
        """Test that all required fields must be provided when not using SQL."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            trigger.Trigger(
                name='trg_test',
                when=trigger.TriggerWhen.BEFORE,
            )
        self.assertIn(
            'Must specify either sql OR (name, when, events, and function)',
            str(ctx.exception),
        )

    def test_trigger_cannot_have_sql_with_structured_fields(self):
        """Test that sql and structured fields are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            trigger.Trigger(
                sql='CREATE TRIGGER ...',
                name='trg_test',
            )
        self.assertIn(
            'Cannot specify sql with structured fields', str(ctx.exception)
        )

    def test_trigger_with_required_fields(self):
        """Test creating trigger with required fields."""
        trg = trigger.Trigger(
            name='trg_test',
            when=trigger.TriggerWhen.BEFORE,
            events=[trigger.TriggerEvent.INSERT],
            function='my_trigger_func',
        )
        self.assertEqual(trg.name, 'trg_test')
        self.assertEqual(trg.when, trigger.TriggerWhen.BEFORE)
        self.assertEqual(len(trg.events), 1)

    def test_trigger_with_multiple_events(self):
        """Test creating trigger with multiple events."""
        trg = trigger.Trigger(
            name='trg_test',
            when=trigger.TriggerWhen.AFTER,
            events=[
                trigger.TriggerEvent.INSERT,
                trigger.TriggerEvent.UPDATE,
                trigger.TriggerEvent.DELETE,
            ],
            function='audit_func',
        )
        self.assertEqual(len(trg.events), 3)

    def test_trigger_with_for_each(self):
        """Test creating trigger with for_each."""
        trg = trigger.Trigger(
            name='trg_test',
            when=trigger.TriggerWhen.BEFORE,
            events=[trigger.TriggerEvent.INSERT],
            function='my_func',
            for_each=trigger.TriggerForEach.ROW,
        )
        self.assertEqual(trg.for_each, trigger.TriggerForEach.ROW)

    def test_trigger_with_condition(self):
        """Test creating trigger with condition."""
        trg = trigger.Trigger(
            name='trg_test',
            when=trigger.TriggerWhen.BEFORE,
            events=[trigger.TriggerEvent.UPDATE],
            function='my_func',
            condition='NEW.status != OLD.status',
        )
        self.assertIsNotNone(trg.condition)

    def test_trigger_with_arguments(self):
        """Test creating trigger with arguments."""
        trg = trigger.Trigger(
            name='trg_test',
            when=trigger.TriggerWhen.AFTER,
            events=[trigger.TriggerEvent.INSERT],
            function='my_func',
            arguments=['arg1', 123, True],
        )
        self.assertEqual(len(trg.arguments), 3)
        self.assertEqual(trg.arguments[1], 123)
        self.assertTrue(trg.arguments[2])

    def test_trigger_with_comment(self):
        """Test creating trigger with comment."""
        trg = trigger.Trigger(
            name='trg_test',
            when=trigger.TriggerWhen.BEFORE,
            events=[trigger.TriggerEvent.INSERT],
            function='my_func',
            comment='Test trigger',
        )
        self.assertEqual(trg.comment, 'Test trigger')

    def test_trigger_with_dependencies(self):
        """Test creating trigger with dependencies."""
        deps = dependencies.Dependencies(
            functions=['public.my_trigger_func()']
        )
        trg = trigger.Trigger(
            name='trg_test',
            when=trigger.TriggerWhen.BEFORE,
            events=[trigger.TriggerEvent.INSERT],
            function='my_trigger_func',
            dependencies=deps,
        )
        self.assertIsNotNone(trg.dependencies)

    def test_trigger_complete_definition(self):
        """Test creating trigger with all fields."""
        deps = dependencies.Dependencies(functions=['public.audit_changes()'])
        trg = trigger.Trigger(
            name='trg_audit',
            when=trigger.TriggerWhen.AFTER,
            events=[
                trigger.TriggerEvent.INSERT,
                trigger.TriggerEvent.UPDATE,
                trigger.TriggerEvent.DELETE,
            ],
            for_each=trigger.TriggerForEach.ROW,
            condition='NEW.important = true',
            function='audit_changes',
            arguments=['audit_table', 'user_id'],
            comment='Audit trigger for important changes',
            dependencies=deps,
        )
        self.assertEqual(trg.name, 'trg_audit')
        self.assertEqual(trg.when, trigger.TriggerWhen.AFTER)
        self.assertEqual(len(trg.events), 3)
        self.assertEqual(trg.for_each, trigger.TriggerForEach.ROW)
        self.assertIsNotNone(trg.condition)
        self.assertEqual(len(trg.arguments), 2)

    def test_trigger_before_insert(self):
        """Test creating BEFORE INSERT trigger."""
        trg = trigger.Trigger(
            name='trg_before_insert',
            when=trigger.TriggerWhen.BEFORE,
            events=[trigger.TriggerEvent.INSERT],
            function='validate_insert',
            for_each=trigger.TriggerForEach.ROW,
        )
        self.assertEqual(trg.when, trigger.TriggerWhen.BEFORE)
        self.assertEqual(trg.events[0], trigger.TriggerEvent.INSERT)

    def test_trigger_after_update(self):
        """Test creating AFTER UPDATE trigger."""
        trg = trigger.Trigger(
            name='trg_after_update',
            when=trigger.TriggerWhen.AFTER,
            events=[trigger.TriggerEvent.UPDATE],
            function='log_update',
            for_each=trigger.TriggerForEach.ROW,
        )
        self.assertEqual(trg.when, trigger.TriggerWhen.AFTER)
        self.assertEqual(trg.events[0], trigger.TriggerEvent.UPDATE)

    def test_trigger_instead_of(self):
        """Test creating INSTEAD OF trigger."""
        trg = trigger.Trigger(
            name='trg_instead_of',
            when=trigger.TriggerWhen.INSTEAD_OF,
            events=[trigger.TriggerEvent.DELETE],
            function='soft_delete',
            for_each=trigger.TriggerForEach.ROW,
        )
        self.assertEqual(trg.when, trigger.TriggerWhen.INSTEAD_OF)

    def test_trigger_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            trigger.Trigger(
                name='trg_test',
                when=trigger.TriggerWhen.BEFORE,
                events=[trigger.TriggerEvent.INSERT],
                function='my_func',
                invalid_field='value',
            )

    def test_trigger_model_dump(self):
        """Test serializing Trigger to dict."""
        trg = trigger.Trigger(
            name='trg_test',
            when=trigger.TriggerWhen.BEFORE,
            events=[trigger.TriggerEvent.INSERT],
            function='my_func',
        )
        data = trg.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('when', data)
        self.assertIn('events', data)

    def test_trigger_model_dump_json(self):
        """Test serializing Trigger to JSON."""
        trg = trigger.Trigger(
            name='trg_audit',
            when=trigger.TriggerWhen.AFTER,
            events=[trigger.TriggerEvent.UPDATE],
            function='audit_func',
            for_each=trigger.TriggerForEach.ROW,
        )
        json_str = trg.model_dump_json(exclude_none=True)
        self.assertIn('trg_audit', json_str)


if __name__ == '__main__':
    unittest.main()
