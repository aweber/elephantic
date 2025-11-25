"""Tests for User Pydantic models."""

import datetime
import unittest

import pydantic

from elephantic.models import acls, user


class TestEnvironment(unittest.TestCase):
    """Test Environment enumeration."""

    def test_environment_values(self):
        """Test Environment enum values."""
        self.assertEqual(user.Environment.DEVELOPMENT.value, 'DEVELOPMENT')
        self.assertEqual(user.Environment.STAGING.value, 'STAGING')
        self.assertEqual(user.Environment.TESTING.value, 'TESTING')
        self.assertEqual(user.Environment.PRODUCTION.value, 'PRODUCTION')


class TestUserOptions(unittest.TestCase):
    """Test UserOptions model."""

    def test_user_options_defaults(self):
        """Test UserOptions default values."""
        opts = user.UserOptions()
        self.assertFalse(opts.bypass_rls)
        self.assertEqual(opts.connection_limit, -1)
        self.assertFalse(opts.create_db)
        self.assertFalse(opts.create_role)
        self.assertFalse(opts.inherit)
        self.assertFalse(opts.replication)
        self.assertFalse(opts.superuser)

    def test_user_options_with_values(self):
        """Test UserOptions with custom values."""
        opts = user.UserOptions(
            create_db=True,
            connection_limit=10,
        )
        self.assertTrue(opts.create_db)
        self.assertEqual(opts.connection_limit, 10)

    def test_user_options_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            user.UserOptions(invalid_field='value')


class TestUser(unittest.TestCase):
    """Test User model."""

    def test_user_with_name(self):
        """Test creating a user with name."""
        u = user.User(name='app_user')
        self.assertEqual(u.name, 'app_user')

    def test_user_without_name(self):
        """Test creating a user without name."""
        u = user.User()
        self.assertIsNone(u.name)

    def test_user_with_comment(self):
        """Test creating a user with comment."""
        u = user.User(name='app_user', comment='Application user')
        self.assertEqual(u.comment, 'Application user')

    def test_user_with_environments(self):
        """Test creating a user with environments."""
        u = user.User(
            name='app_user',
            environments=[
                user.Environment.DEVELOPMENT,
                user.Environment.PRODUCTION,
            ],
        )
        self.assertEqual(len(u.environments), 2)

    def test_user_environments_must_be_unique(self):
        """Test that environments must be unique."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            user.User(
                name='app_user',
                environments=[
                    user.Environment.DEVELOPMENT,
                    user.Environment.DEVELOPMENT,
                ],
            )
        self.assertIn('must be unique', str(ctx.exception))

    def test_user_with_password(self):
        """Test creating a user with password."""
        u = user.User(name='app_user', password='secret123')
        self.assertEqual(u.password, 'secret123')

    def test_user_with_valid_until(self):
        """Test creating a user with valid_until."""
        dt = datetime.datetime(2025, 12, 31, 23, 59, 59, tzinfo=datetime.UTC)
        u = user.User(name='app_user', valid_until=dt)
        self.assertEqual(u.valid_until, dt)

    def test_user_with_grants(self):
        """Test creating a user with grants."""
        grants = acls.ACLs(
            databases={'mydb': [acls.DatabasePrivilege.CONNECT]}
        )
        u = user.User(name='app_user', grants=grants)
        self.assertIsNotNone(u.grants)

    def test_user_with_revocations(self):
        """Test creating a user with revocations."""
        revocations = acls.ACLs(
            databases={'olddb': [acls.DatabasePrivilege.CONNECT]}
        )
        u = user.User(name='app_user', revocations=revocations)
        self.assertIsNotNone(u.revocations)

    def test_user_with_options(self):
        """Test creating a user with options."""
        opts = user.UserOptions(create_db=True)
        u = user.User(name='app_user', options=opts)
        self.assertIsNotNone(u.options)
        self.assertTrue(u.options.create_db)

    def test_user_with_settings(self):
        """Test creating a user with settings."""
        u = user.User(
            name='app_user',
            settings=[
                {'work_mem': '64MB'},
                {'statement_timeout': 30000},
            ],
        )
        self.assertEqual(len(u.settings), 2)

    def test_user_settings_validates_names(self):
        """Test that setting names are validated."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            user.User(
                name='app_user',
                settings=[{'invalid-name!': 'value'}],
            )
        self.assertIn('does not match required pattern', str(ctx.exception))

    def test_user_settings_allows_valid_names(self):
        """Test that valid setting names are allowed."""
        u = user.User(
            name='app_user',
            settings=[
                {'work_mem': '64MB'},
                {'search_path': 'public,app'},
                {'_underscore_start': 'value'},
            ],
        )
        self.assertEqual(len(u.settings), 3)

    def test_user_complex_configuration(self):
        """Test creating a user with all fields."""
        grants = acls.ACLs(
            databases={'mydb': [acls.DatabasePrivilege.CONNECT]}
        )
        opts = user.UserOptions(create_db=True)
        dt = datetime.datetime(2025, 12, 31, 23, 59, 59, tzinfo=datetime.UTC)
        u = user.User(
            name='app_user',
            comment='Application user',
            environments=[user.Environment.PRODUCTION],
            password='secret123',
            valid_until=dt,
            grants=grants,
            options=opts,
            settings=[{'work_mem': '64MB'}],
        )
        self.assertEqual(u.name, 'app_user')
        self.assertEqual(u.password, 'secret123')
        self.assertEqual(u.valid_until, dt)
        self.assertIsNotNone(u.grants)
        self.assertIsNotNone(u.options)
        self.assertIsNotNone(u.settings)

    def test_user_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            user.User(name='app_user', invalid_field='value')

    def test_user_model_dump(self):
        """Test serializing User to dict."""
        u = user.User(name='app_user')
        data = u.model_dump(exclude_none=True)
        self.assertIn('name', data)
        self.assertNotIn('comment', data)

    def test_user_model_dump_json(self):
        """Test serializing User to JSON."""
        u = user.User(name='app_user')
        json_str = u.model_dump_json(exclude_none=True)
        self.assertIn('app_user', json_str)


if __name__ == '__main__':
    unittest.main()
