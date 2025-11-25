"""Tests for ACLs Pydantic models."""

import unittest

import pydantic

from elephantic.models import acls


class TestPrivilegeEnums(unittest.TestCase):
    """Test privilege enumeration types."""

    def test_column_privilege_values(self):
        """Test ColumnPrivilege enum values."""
        self.assertEqual(acls.ColumnPrivilege.SELECT.value, 'SELECT')
        self.assertEqual(acls.ColumnPrivilege.INSERT.value, 'INSERT')
        self.assertEqual(acls.ColumnPrivilege.UPDATE.value, 'UPDATE')
        self.assertEqual(acls.ColumnPrivilege.DELETE.value, 'DELETE')
        self.assertEqual(acls.ColumnPrivilege.ALL.value, 'ALL')

    def test_database_privilege_values(self):
        """Test DatabasePrivilege enum values."""
        self.assertEqual(acls.DatabasePrivilege.CREATE.value, 'CREATE')
        self.assertEqual(acls.DatabasePrivilege.CONNECT.value, 'CONNECT')
        self.assertEqual(acls.DatabasePrivilege.TEMP.value, 'TEMP')
        self.assertEqual(acls.DatabasePrivilege.TEMPORARY.value, 'TEMPORARY')
        self.assertEqual(acls.DatabasePrivilege.ALL.value, 'ALL')

    def test_usage_privilege_values(self):
        """Test UsagePrivilege enum values."""
        self.assertEqual(acls.UsagePrivilege.USAGE.value, 'USAGE')
        self.assertEqual(acls.UsagePrivilege.ALL.value, 'ALL')

    def test_execute_privilege_values(self):
        """Test ExecutePrivilege enum values."""
        self.assertEqual(acls.ExecutePrivilege.EXECUTE.value, 'EXECUTE')
        self.assertEqual(acls.ExecutePrivilege.ALL.value, 'ALL')

    def test_schema_privilege_values(self):
        """Test SchemaPrivilege enum values."""
        self.assertEqual(acls.SchemaPrivilege.CREATE.value, 'CREATE')
        self.assertEqual(acls.SchemaPrivilege.USAGE.value, 'USAGE')
        self.assertEqual(acls.SchemaPrivilege.ALL.value, 'ALL')

    def test_sequence_privilege_values(self):
        """Test SequencePrivilege enum values."""
        self.assertEqual(acls.SequencePrivilege.SELECT.value, 'SELECT')
        self.assertEqual(acls.SequencePrivilege.UPDATE.value, 'UPDATE')
        self.assertEqual(acls.SequencePrivilege.USAGE.value, 'USAGE')
        self.assertEqual(acls.SequencePrivilege.ALL.value, 'ALL')

    def test_table_privilege_values(self):
        """Test TablePrivilege enum values."""
        self.assertEqual(acls.TablePrivilege.SELECT.value, 'SELECT')
        self.assertEqual(acls.TablePrivilege.INSERT.value, 'INSERT')
        self.assertEqual(acls.TablePrivilege.UPDATE.value, 'UPDATE')
        self.assertEqual(acls.TablePrivilege.DELETE.value, 'DELETE')
        self.assertEqual(acls.TablePrivilege.ALL.value, 'ALL')

    def test_view_privilege_values(self):
        """Test ViewPrivilege enum values."""
        self.assertEqual(acls.ViewPrivilege.SELECT.value, 'SELECT')
        self.assertEqual(acls.ViewPrivilege.ALL.value, 'ALL')

    def test_large_object_privilege_values(self):
        """Test LargeObjectPrivilege enum values."""
        self.assertEqual(acls.LargeObjectPrivilege.SELECT.value, 'SELECT')
        self.assertEqual(acls.LargeObjectPrivilege.UPDATE.value, 'UPDATE')
        self.assertEqual(acls.LargeObjectPrivilege.ALL.value, 'ALL')


class TestACLsModel(unittest.TestCase):
    """Test ACLs Pydantic model."""

    def test_empty_acls(self):
        """Test creating an empty ACLs object."""
        result = acls.ACLs()
        self.assertIsNone(result.columns)
        self.assertIsNone(result.databases)
        self.assertIsNone(result.tables)

    def test_column_acls_valid(self):
        """Test valid column ACLs."""
        result = acls.ACLs(
            columns={
                'public.users.email': [acls.ColumnPrivilege.SELECT],
                'app.orders.total': [
                    acls.ColumnPrivilege.SELECT,
                    acls.ColumnPrivilege.UPDATE,
                ],
            }
        )
        self.assertIsNotNone(result.columns)
        self.assertEqual(len(result.columns), 2)

    def test_column_acls_invalid_pattern(self):
        """Test invalid column pattern raises error."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            acls.ACLs(columns={'invalid': [acls.ColumnPrivilege.SELECT]})
        self.assertIn('schema.table.column', str(ctx.exception))

    def test_column_acls_missing_component(self):
        """Test column pattern with missing component."""
        with self.assertRaises(pydantic.ValidationError):
            acls.ACLs(columns={'public.users': [acls.ColumnPrivilege.SELECT]})

    def test_database_acls_valid(self):
        """Test valid database ACLs."""
        result = acls.ACLs(
            databases={
                'mydb': [
                    acls.DatabasePrivilege.CONNECT,
                    acls.DatabasePrivilege.CREATE,
                ]
            }
        )
        self.assertIsNotNone(result.databases)
        self.assertEqual(len(result.databases), 1)

    def test_domain_acls_valid(self):
        """Test valid domain ACLs."""
        result = acls.ACLs(
            domains={'public.email_domain': [acls.UsagePrivilege.USAGE]}
        )
        self.assertIsNotNone(result.domains)
        self.assertEqual(len(result.domains), 1)

    def test_domain_acls_invalid_pattern(self):
        """Test invalid domain pattern raises error."""
        with self.assertRaises(pydantic.ValidationError):
            acls.ACLs(domains={'invalid': [acls.UsagePrivilege.USAGE]})

    def test_foreign_data_wrapper_acls_valid(self):
        """Test valid foreign data wrapper ACLs."""
        result = acls.ACLs(
            foreign_data_wrappers={'postgres_fdw': [acls.UsagePrivilege.USAGE]}
        )
        self.assertIsNotNone(result.foreign_data_wrappers)

    def test_foreign_server_acls_valid(self):
        """Test valid foreign server ACLs."""
        result = acls.ACLs(
            foreign_servers={'remote_db': [acls.UsagePrivilege.USAGE]}
        )
        self.assertIsNotNone(result.foreign_servers)

    def test_function_acls_valid(self):
        """Test valid function ACLs."""
        result = acls.ACLs(
            functions={
                'public.my_func()': [acls.ExecutePrivilege.EXECUTE],
                'app.calc(integer, text)': [acls.ExecutePrivilege.ALL],
            }
        )
        self.assertIsNotNone(result.functions)
        self.assertEqual(len(result.functions), 2)

    def test_function_acls_invalid_pattern(self):
        """Test invalid function pattern raises error."""
        with self.assertRaises(pydantic.ValidationError):
            acls.ACLs(
                functions={'public.my_func': [acls.ExecutePrivilege.EXECUTE]}
            )

    def test_groups_valid(self):
        """Test valid groups list."""
        result = acls.ACLs(groups=['developers', 'admins', 'readers'])
        self.assertEqual(len(result.groups), 3)

    def test_groups_must_be_unique(self):
        """Test groups must contain unique items."""
        with self.assertRaises(pydantic.ValidationError):
            acls.ACLs(groups=['developers', 'admins', 'developers'])

    def test_roles_valid(self):
        """Test valid roles list."""
        result = acls.ACLs(roles=['app_user', 'app_admin'])
        self.assertEqual(len(result.roles), 2)

    def test_roles_must_be_unique(self):
        """Test roles must contain unique items."""
        with self.assertRaises(pydantic.ValidationError):
            acls.ACLs(roles=['app_user', 'app_user'])

    def test_language_acls_valid(self):
        """Test valid language ACLs."""
        result = acls.ACLs(languages={'plpgsql': [acls.UsagePrivilege.USAGE]})
        self.assertIsNotNone(result.languages)

    def test_large_object_acls_valid(self):
        """Test valid large object ACLs."""
        result = acls.ACLs(
            large_objects={
                '12345': [acls.LargeObjectPrivilege.SELECT],
                '67890': [acls.LargeObjectPrivilege.UPDATE],
            }
        )
        self.assertIsNotNone(result.large_objects)

    def test_large_object_acls_invalid_oid(self):
        """Test invalid large object OID raises error."""
        with self.assertRaises(pydantic.ValidationError):
            acls.ACLs(
                large_objects={
                    'not_numeric': [acls.LargeObjectPrivilege.SELECT]
                }
            )

    def test_schema_acls_valid(self):
        """Test valid schema ACLs."""
        result = acls.ACLs(
            schemata={
                'public': [acls.SchemaPrivilege.USAGE],
                'app': [
                    acls.SchemaPrivilege.CREATE,
                    acls.SchemaPrivilege.USAGE,
                ],
            }
        )
        self.assertIsNotNone(result.schemata)

    def test_sequence_acls_valid(self):
        """Test valid sequence ACLs."""
        result = acls.ACLs(
            sequences={
                'public.users_id_seq': [
                    acls.SequencePrivilege.SELECT,
                    acls.SequencePrivilege.USAGE,
                ]
            }
        )
        self.assertIsNotNone(result.sequences)

    def test_sequence_acls_invalid_pattern(self):
        """Test invalid sequence pattern raises error."""
        with self.assertRaises(pydantic.ValidationError):
            acls.ACLs(sequences={'invalid': [acls.SequencePrivilege.USAGE]})

    def test_table_acls_valid(self):
        """Test valid table ACLs."""
        result = acls.ACLs(
            tables={
                'public.users': [
                    acls.TablePrivilege.SELECT,
                    acls.TablePrivilege.INSERT,
                ],
                'app.orders': [acls.TablePrivilege.ALL],
            }
        )
        self.assertIsNotNone(result.tables)

    def test_table_acls_invalid_pattern(self):
        """Test invalid table pattern raises error."""
        with self.assertRaises(pydantic.ValidationError):
            acls.ACLs(tables={'invalid': [acls.TablePrivilege.SELECT]})

    def test_tablespace_acls_valid(self):
        """Test valid tablespace ACLs."""
        result = acls.ACLs(
            tablespaces={'fast_storage': [acls.SchemaPrivilege.CREATE]}
        )
        self.assertIsNotNone(result.tablespaces)

    def test_type_acls_valid(self):
        """Test valid type ACLs."""
        result = acls.ACLs(
            types={'public.custom_type': [acls.UsagePrivilege.USAGE]}
        )
        self.assertIsNotNone(result.types)

    def test_type_acls_invalid_pattern(self):
        """Test invalid type pattern raises error."""
        with self.assertRaises(pydantic.ValidationError):
            acls.ACLs(types={'invalid': [acls.UsagePrivilege.USAGE]})

    def test_view_acls_valid(self):
        """Test valid view ACLs."""
        result = acls.ACLs(
            views={
                'public.user_summary': [acls.ViewPrivilege.SELECT],
                'app.report_view': [acls.ViewPrivilege.ALL],
            }
        )
        self.assertIsNotNone(result.views)

    def test_view_acls_invalid_pattern(self):
        """Test invalid view pattern raises error."""
        with self.assertRaises(pydantic.ValidationError):
            acls.ACLs(views={'invalid': [acls.ViewPrivilege.SELECT]})

    def test_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            acls.ACLs(invalid_field='value')

    def test_complex_acls_configuration(self):
        """Test creating ACLs with multiple configurations."""
        result = acls.ACLs(
            groups=['developers', 'admins'],
            roles=['app_user', 'app_admin'],
            databases={'mydb': [acls.DatabasePrivilege.CONNECT]},
            schemata={'public': [acls.SchemaPrivilege.USAGE]},
            tables={
                'public.users': [acls.TablePrivilege.SELECT],
                'public.orders': [acls.TablePrivilege.ALL],
            },
            sequences={'public.users_id_seq': [acls.SequencePrivilege.USAGE]},
            functions={'public.calc()': [acls.ExecutePrivilege.EXECUTE]},
        )
        self.assertEqual(len(result.groups), 2)
        self.assertEqual(len(result.roles), 2)
        self.assertEqual(len(result.tables), 2)

    def test_model_dump(self):
        """Test serializing ACLs to dict."""
        result = acls.ACLs(
            roles=['app_user'],
            tables={'public.users': [acls.TablePrivilege.SELECT]},
        )
        data = result.model_dump(exclude_none=True)
        self.assertIn('roles', data)
        self.assertIn('tables', data)
        self.assertNotIn('columns', data)

    def test_model_dump_json(self):
        """Test serializing ACLs to JSON."""
        result = acls.ACLs(roles=['app_user'])
        json_str = result.model_dump_json(exclude_none=True)
        self.assertIn('app_user', json_str)
        self.assertIn('roles', json_str)


if __name__ == '__main__':
    unittest.main()
