"""Tests for UserMapping Pydantic models."""

import unittest

import pydantic

from elephantic.models import user_mapping


class TestServerMapping(unittest.TestCase):
    """Test ServerMapping model."""

    def test_server_mapping_with_name(self):
        """Test creating a server mapping with name."""
        sm = user_mapping.ServerMapping(name='my_server')
        self.assertEqual(sm.name, 'my_server')
        self.assertIsNone(sm.options)

    def test_server_mapping_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            user_mapping.ServerMapping()

    def test_server_mapping_with_options(self):
        """Test creating a server mapping with options."""
        sm = user_mapping.ServerMapping(
            name='my_server',
            options={'user': 'postgres', 'password': 'secret'},
        )
        self.assertEqual(len(sm.options), 2)
        self.assertEqual(sm.options['user'], 'postgres')

    def test_server_mapping_options_validate_names(self):
        """Test that option names are validated."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            user_mapping.ServerMapping(
                name='my_server',
                options={'invalid-name!': 'value'},
            )
        self.assertIn('does not match required pattern', str(ctx.exception))

    def test_server_mapping_options_allow_valid_names(self):
        """Test that valid option names are allowed."""
        sm = user_mapping.ServerMapping(
            name='my_server',
            options={
                'user': 'postgres',
                'password_hash': 'secret',
                '_private': 'value',
                'option.name': 'value',
            },
        )
        self.assertEqual(len(sm.options), 4)

    def test_server_mapping_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            user_mapping.ServerMapping(
                name='my_server',
                invalid_field='value',
            )


class TestUserMapping(unittest.TestCase):
    """Test UserMapping model."""

    def test_user_mapping_with_name_and_servers(self):
        """Test creating a user mapping with name and servers."""
        sm = user_mapping.ServerMapping(name='my_server')
        um = user_mapping.UserMapping(
            name='app_user',
            servers=[sm],
        )
        self.assertEqual(um.name, 'app_user')
        self.assertEqual(len(um.servers), 1)

    def test_user_mapping_requires_name(self):
        """Test that name is required."""
        sm = user_mapping.ServerMapping(name='my_server')
        with self.assertRaises(pydantic.ValidationError):
            user_mapping.UserMapping(servers=[sm])

    def test_user_mapping_requires_servers(self):
        """Test that servers is required."""
        with self.assertRaises(pydantic.ValidationError):
            user_mapping.UserMapping(name='app_user')

    def test_user_mapping_requires_at_least_one_server(self):
        """Test that at least one server is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            user_mapping.UserMapping(
                name='app_user',
                servers=[],
            )
        self.assertIn('at least 1 item', str(ctx.exception))

    def test_user_mapping_with_multiple_servers(self):
        """Test creating a user mapping with multiple servers."""
        sm1 = user_mapping.ServerMapping(name='server1')
        sm2 = user_mapping.ServerMapping(name='server2')
        um = user_mapping.UserMapping(
            name='app_user',
            servers=[sm1, sm2],
        )
        self.assertEqual(len(um.servers), 2)

    def test_user_mapping_with_server_options(self):
        """Test creating a user mapping with server options."""
        sm = user_mapping.ServerMapping(
            name='my_server',
            options={'user': 'postgres', 'password': 'secret'},
        )
        um = user_mapping.UserMapping(
            name='app_user',
            servers=[sm],
        )
        self.assertEqual(um.servers[0].options['user'], 'postgres')

    def test_user_mapping_complex_configuration(self):
        """Test creating a user mapping with multiple servers and options."""
        sm1 = user_mapping.ServerMapping(
            name='server1',
            options={'user': 'user1', 'password': 'pass1'},
        )
        sm2 = user_mapping.ServerMapping(
            name='server2',
            options={'user': 'user2', 'password': 'pass2'},
        )
        um = user_mapping.UserMapping(
            name='app_user',
            servers=[sm1, sm2],
        )
        self.assertEqual(um.name, 'app_user')
        self.assertEqual(len(um.servers), 2)
        self.assertEqual(um.servers[0].name, 'server1')
        self.assertEqual(um.servers[1].name, 'server2')

    def test_user_mapping_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        sm = user_mapping.ServerMapping(name='my_server')
        with self.assertRaises(pydantic.ValidationError):
            user_mapping.UserMapping(
                name='app_user',
                servers=[sm],
                invalid_field='value',
            )

    def test_user_mapping_model_dump(self):
        """Test serializing UserMapping to dict."""
        sm = user_mapping.ServerMapping(name='my_server')
        um = user_mapping.UserMapping(
            name='app_user',
            servers=[sm],
        )
        data = um.model_dump()
        self.assertIn('name', data)
        self.assertIn('servers', data)

    def test_user_mapping_model_dump_json(self):
        """Test serializing UserMapping to JSON."""
        sm = user_mapping.ServerMapping(name='my_server')
        um = user_mapping.UserMapping(
            name='app_user',
            servers=[sm],
        )
        json_str = um.model_dump_json()
        self.assertIn('app_user', json_str)


if __name__ == '__main__':
    unittest.main()
