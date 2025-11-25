"""Tests for Group Pydantic models."""

import unittest

import pydantic

from elephantic.models import acls, group


class TestEnvironment(unittest.TestCase):
    """Test Environment enumeration."""

    def test_environment_values(self):
        """Test Environment enum values."""
        self.assertEqual(group.Environment.DEVELOPMENT.value, 'DEVELOPMENT')
        self.assertEqual(group.Environment.STAGING.value, 'STAGING')
        self.assertEqual(group.Environment.TESTING.value, 'TESTING')
        self.assertEqual(group.Environment.PRODUCTION.value, 'PRODUCTION')


class TestGroupOptions(unittest.TestCase):
    """Test GroupOptions model."""

    def test_group_options_defaults(self):
        """Test GroupOptions default values."""
        opts = group.GroupOptions()
        self.assertFalse(opts.create_db)
        self.assertFalse(opts.create_role)
        self.assertFalse(opts.inherit)
        self.assertFalse(opts.replication)
        self.assertFalse(opts.superuser)

    def test_group_options_with_values(self):
        """Test GroupOptions with custom values."""
        opts = group.GroupOptions(
            create_db=True,
            inherit=True,
        )
        self.assertTrue(opts.create_db)
        self.assertTrue(opts.inherit)
        self.assertFalse(opts.create_role)

    def test_group_options_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            group.GroupOptions(invalid_field='value')


class TestGroup(unittest.TestCase):
    """Test Group model."""

    def test_group_with_name(self):
        """Test creating a group with name."""
        g = group.Group(name='developers')
        self.assertEqual(g.name, 'developers')
        self.assertIsNone(g.comment)
        self.assertIsNone(g.grants)

    def test_group_without_name(self):
        """Test creating a group without name."""
        g = group.Group()
        self.assertIsNone(g.name)

    def test_group_with_comment(self):
        """Test creating a group with comment."""
        g = group.Group(name='developers', comment='Developer group')
        self.assertEqual(g.comment, 'Developer group')

    def test_group_with_environments(self):
        """Test creating a group with environments."""
        g = group.Group(
            name='developers',
            environments=[
                group.Environment.DEVELOPMENT,
                group.Environment.STAGING,
            ],
        )
        self.assertEqual(len(g.environments), 2)
        self.assertIn(group.Environment.DEVELOPMENT, g.environments)

    def test_group_environments_must_be_unique(self):
        """Test that environments must be unique."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            group.Group(
                name='developers',
                environments=[
                    group.Environment.DEVELOPMENT,
                    group.Environment.DEVELOPMENT,
                ],
            )
        self.assertIn('must be unique', str(ctx.exception))

    def test_group_with_grants(self):
        """Test creating a group with grants."""
        grants = acls.ACLs(
            databases={'mydb': [acls.DatabasePrivilege.CONNECT]}
        )
        g = group.Group(name='developers', grants=grants)
        self.assertIsNotNone(g.grants)
        self.assertIn('mydb', g.grants.databases)

    def test_group_with_revocations(self):
        """Test creating a group with revocations."""
        revocations = acls.ACLs(
            databases={'olddb': [acls.DatabasePrivilege.CONNECT]}
        )
        g = group.Group(name='developers', revocations=revocations)
        self.assertIsNotNone(g.revocations)

    def test_group_with_options(self):
        """Test creating a group with options."""
        opts = group.GroupOptions(create_db=True, inherit=True)
        g = group.Group(name='developers', options=opts)
        self.assertIsNotNone(g.options)
        self.assertTrue(g.options.create_db)
        self.assertTrue(g.options.inherit)

    def test_group_complex_configuration(self):
        """Test creating a group with all fields."""
        grants = acls.ACLs(
            databases={'mydb': [acls.DatabasePrivilege.CONNECT]}
        )
        opts = group.GroupOptions(create_db=True)
        g = group.Group(
            name='developers',
            comment='Developer group',
            environments=[
                group.Environment.DEVELOPMENT,
                group.Environment.STAGING,
            ],
            grants=grants,
            options=opts,
        )
        self.assertEqual(g.name, 'developers')
        self.assertEqual(g.comment, 'Developer group')
        self.assertEqual(len(g.environments), 2)
        self.assertIsNotNone(g.grants)
        self.assertIsNotNone(g.options)

    def test_group_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            group.Group(name='developers', invalid_field='value')

    def test_group_model_dump(self):
        """Test serializing Group to dict."""
        g = group.Group(name='developers')
        data = g.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertNotIn('comment', data)

    def test_group_model_dump_json(self):
        """Test serializing Group to JSON."""
        g = group.Group(name='developers')
        json_str = g.model_dump_json(exclude_none=True)
        self.assertIn('developers', json_str)


if __name__ == '__main__':
    unittest.main()
