"""Tests for Role Pydantic models."""

import unittest

import pydantic

from elephantic.models import acls, role


class TestEnvironment(unittest.TestCase):
    """Test Environment enumeration."""

    def test_environment_values(self):
        """Test Environment enum values."""
        self.assertEqual(role.Environment.DEVELOPMENT.value, 'DEVELOPMENT')
        self.assertEqual(role.Environment.STAGING.value, 'STAGING')
        self.assertEqual(role.Environment.TESTING.value, 'TESTING')
        self.assertEqual(role.Environment.PRODUCTION.value, 'PRODUCTION')


class TestRoleOptions(unittest.TestCase):
    """Test RoleOptions model."""

    def test_role_options_defaults(self):
        """Test RoleOptions default values."""
        opts = role.RoleOptions()
        self.assertFalse(opts.bypass_rls)
        self.assertEqual(opts.connection_limit, -1)
        self.assertFalse(opts.create_db)
        self.assertFalse(opts.create_role)
        self.assertFalse(opts.inherit)
        self.assertFalse(opts.login)
        self.assertFalse(opts.replication)
        self.assertFalse(opts.superuser)

    def test_role_options_with_values(self):
        """Test RoleOptions with custom values."""
        opts = role.RoleOptions(
            login=True,
            create_db=True,
            connection_limit=10,
        )
        self.assertTrue(opts.login)
        self.assertTrue(opts.create_db)
        self.assertEqual(opts.connection_limit, 10)

    def test_role_options_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            role.RoleOptions(invalid_field='value')


class TestRole(unittest.TestCase):
    """Test Role model."""

    def test_role_with_name(self):
        """Test creating a role with name."""
        r = role.Role(name='app_role')
        self.assertEqual(r.name, 'app_role')
        self.assertTrue(r.create)

    def test_role_without_name(self):
        """Test creating a role without name."""
        r = role.Role()
        self.assertIsNone(r.name)

    def test_role_create_defaults_to_true(self):
        """Test that create defaults to True."""
        r = role.Role(name='app_role')
        self.assertTrue(r.create)

    def test_role_with_create_false(self):
        """Test creating a role with create=False."""
        r = role.Role(name='PUBLIC', create=False)
        self.assertFalse(r.create)

    def test_role_with_comment(self):
        """Test creating a role with comment."""
        r = role.Role(name='app_role', comment='Application role')
        self.assertEqual(r.comment, 'Application role')

    def test_role_with_environments(self):
        """Test creating a role with environments."""
        r = role.Role(
            name='app_role',
            environments=[
                role.Environment.DEVELOPMENT,
                role.Environment.PRODUCTION,
            ],
        )
        self.assertEqual(len(r.environments), 2)

    def test_role_environments_must_be_unique(self):
        """Test that environments must be unique."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            role.Role(
                name='app_role',
                environments=[
                    role.Environment.DEVELOPMENT,
                    role.Environment.DEVELOPMENT,
                ],
            )
        self.assertIn('must be unique', str(ctx.exception))

    def test_role_with_grants(self):
        """Test creating a role with grants."""
        grants = acls.ACLs(
            databases={'mydb': [acls.DatabasePrivilege.CONNECT]}
        )
        r = role.Role(name='app_role', grants=grants)
        self.assertIsNotNone(r.grants)

    def test_role_with_revocations(self):
        """Test creating a role with revocations."""
        revocations = acls.ACLs(
            databases={'olddb': [acls.DatabasePrivilege.CONNECT]}
        )
        r = role.Role(name='app_role', revocations=revocations)
        self.assertIsNotNone(r.revocations)

    def test_role_with_options(self):
        """Test creating a role with options."""
        opts = role.RoleOptions(login=True, create_db=True)
        r = role.Role(name='app_role', options=opts)
        self.assertIsNotNone(r.options)
        self.assertTrue(r.options.login)

    def test_role_with_settings(self):
        """Test creating a role with settings."""
        r = role.Role(
            name='app_role',
            settings=[
                {'work_mem': '64MB'},
                {'statement_timeout': 30000},
            ],
        )
        self.assertEqual(len(r.settings), 2)

    def test_role_settings_validates_names(self):
        """Test that setting names are validated."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            role.Role(
                name='app_role',
                settings=[{'invalid-name!': 'value'}],
            )
        self.assertIn('does not match required pattern', str(ctx.exception))

    def test_role_settings_allows_valid_names(self):
        """Test that valid setting names are allowed."""
        r = role.Role(
            name='app_role',
            settings=[
                {'work_mem': '64MB'},
                {'search_path': 'public,app'},
                {'_underscore_start': 'value'},
            ],
        )
        self.assertEqual(len(r.settings), 3)

    def test_role_complex_configuration(self):
        """Test creating a role with all fields."""
        grants = acls.ACLs(
            databases={'mydb': [acls.DatabasePrivilege.CONNECT]}
        )
        opts = role.RoleOptions(login=True)
        r = role.Role(
            name='app_role',
            comment='Application role',
            environments=[role.Environment.PRODUCTION],
            grants=grants,
            options=opts,
            settings=[{'work_mem': '64MB'}],
        )
        self.assertEqual(r.name, 'app_role')
        self.assertTrue(r.create)
        self.assertIsNotNone(r.grants)
        self.assertIsNotNone(r.options)
        self.assertIsNotNone(r.settings)

    def test_role_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            role.Role(name='app_role', invalid_field='value')

    def test_role_model_dump(self):
        """Test serializing Role to dict."""
        r = role.Role(name='app_role')
        data = r.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertIn('create', data)
        self.assertNotIn('comment', data)

    def test_role_model_dump_json(self):
        """Test serializing Role to JSON."""
        r = role.Role(name='app_role')
        json_str = r.model_dump_json(exclude_none=True)
        self.assertIn('app_role', json_str)


if __name__ == '__main__':
    unittest.main()
