"""Tests for TextSearch Pydantic models."""

import unittest

import pydantic

from elephantic.models import text_search


class TestConfiguration(unittest.TestCase):
    """Test Configuration model."""

    def test_configuration_with_sql(self):
        """Test creating a configuration with SQL."""
        c = text_search.Configuration(
            name='my_config', sql='CREATE TEXT SEARCH ...'
        )
        self.assertEqual(c.name, 'my_config')
        self.assertIsNotNone(c.sql)

    def test_configuration_with_parser(self):
        """Test creating a configuration with parser."""
        c = text_search.Configuration(name='my_config', parser='my_parser')
        self.assertEqual(c.parser, 'my_parser')

    def test_configuration_with_source(self):
        """Test creating a configuration with source."""
        c = text_search.Configuration(
            name='my_config', source='existing_config'
        )
        self.assertEqual(c.source, 'existing_config')

    def test_configuration_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            text_search.Configuration(sql='CREATE ...')

    def test_configuration_requires_one_of_sql_parser_source(self):
        """Test that one of sql, parser, or source is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            text_search.Configuration(name='my_config')
        self.assertIn('Must specify one of', str(ctx.exception))

    def test_configuration_cannot_have_multiple_methods(self):
        """Test that only one of sql, parser, or source can be specified."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            text_search.Configuration(
                name='my_config',
                sql='CREATE ...',
                parser='my_parser',
            )
        self.assertIn('Cannot specify more than one', str(ctx.exception))


class TestDictionary(unittest.TestCase):
    """Test Dictionary model."""

    def test_dictionary_with_sql(self):
        """Test creating a dictionary with SQL."""
        d = text_search.Dictionary(
            name='my_dict', sql='CREATE TEXT SEARCH DICTIONARY ...'
        )
        self.assertEqual(d.name, 'my_dict')
        self.assertIsNotNone(d.sql)

    def test_dictionary_with_template(self):
        """Test creating a dictionary with template."""
        d = text_search.Dictionary(name='my_dict', template='snowball')
        self.assertEqual(d.template, 'snowball')

    def test_dictionary_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            text_search.Dictionary(template='snowball')

    def test_dictionary_requires_sql_or_template(self):
        """Test that either sql or template is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            text_search.Dictionary(name='my_dict')
        self.assertIn(
            'Must specify either sql or template', str(ctx.exception)
        )

    def test_dictionary_cannot_have_sql_and_template(self):
        """Test that sql and template are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            text_search.Dictionary(
                name='my_dict',
                sql='CREATE ...',
                template='snowball',
            )
        self.assertIn('Cannot specify sql with template', str(ctx.exception))

    def test_dictionary_with_options(self):
        """Test creating a dictionary with options."""
        d = text_search.Dictionary(
            name='my_dict',
            template='snowball',
            options={'language': 'english'},
        )
        self.assertIsNotNone(d.options)

    def test_dictionary_options_validate_names(self):
        """Test that option names are validated."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            text_search.Dictionary(
                name='my_dict',
                template='snowball',
                options={'invalid-name!': 'value'},
            )
        self.assertIn('does not match required pattern', str(ctx.exception))


class TestParser(unittest.TestCase):
    """Test Parser model."""

    def test_parser_with_sql(self):
        """Test creating a parser with SQL."""
        p = text_search.Parser(
            name='my_parser', sql='CREATE TEXT SEARCH PARSER ...'
        )
        self.assertEqual(p.name, 'my_parser')
        self.assertIsNotNone(p.sql)

    def test_parser_with_functions(self):
        """Test creating a parser with required functions."""
        p = text_search.Parser(
            name='my_parser',
            start_function='start_func',
            gettoken_function='gettoken_func',
            end_function='end_func',
            lextypes_function='lextypes_func',
        )
        self.assertEqual(p.start_function, 'start_func')
        self.assertEqual(p.gettoken_function, 'gettoken_func')

    def test_parser_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            text_search.Parser(sql='CREATE ...')

    def test_parser_requires_sql_or_functions(self):
        """Test that either sql or all required functions are needed."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            text_search.Parser(name='my_parser')
        self.assertIn('Must specify either sql or all of', str(ctx.exception))

    def test_parser_requires_all_four_functions(self):
        """Test that all four functions are required when not using SQL."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            text_search.Parser(
                name='my_parser',
                start_function='start_func',
                gettoken_function='gettoken_func',
            )
        self.assertIn('Must specify either sql or all of', str(ctx.exception))

    def test_parser_with_headline_function(self):
        """Test creating a parser with optional headline function."""
        p = text_search.Parser(
            name='my_parser',
            start_function='start_func',
            gettoken_function='gettoken_func',
            end_function='end_func',
            lextypes_function='lextypes_func',
            headline_function='headline_func',
        )
        self.assertEqual(p.headline_function, 'headline_func')


class TestTemplate(unittest.TestCase):
    """Test Template model."""

    def test_template_with_sql(self):
        """Test creating a template with SQL."""
        t = text_search.Template(
            name='my_template', sql='CREATE TEXT SEARCH TEMPLATE ...'
        )
        self.assertEqual(t.name, 'my_template')
        self.assertIsNotNone(t.sql)

    def test_template_with_lexize_function(self):
        """Test creating a template with lexize_function."""
        t = text_search.Template(
            name='my_template', lexize_function='my_lexize'
        )
        self.assertEqual(t.lexize_function, 'my_lexize')

    def test_template_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            text_search.Template(lexize_function='my_lexize')

    def test_template_requires_sql_or_lexize_function(self):
        """Test that either sql or lexize_function is required."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            text_search.Template(name='my_template')
        self.assertIn(
            'Must specify either sql or lexize_function', str(ctx.exception)
        )

    def test_template_cannot_have_sql_and_lexize_function(self):
        """Test that sql and lexize_function are mutually exclusive."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            text_search.Template(
                name='my_template',
                sql='CREATE ...',
                lexize_function='my_lexize',
            )
        self.assertIn(
            'Cannot specify sql with lexize_function', str(ctx.exception)
        )

    def test_template_with_init_function(self):
        """Test creating a template with optional init_function."""
        t = text_search.Template(
            name='my_template',
            lexize_function='my_lexize',
            init_function='my_init',
        )
        self.assertEqual(t.init_function, 'my_init')


class TestTextSearch(unittest.TestCase):
    """Test TextSearch model."""

    def test_text_search_with_schema(self):
        """Test creating text search with schema."""
        ts = text_search.TextSearch(schema='public')
        self.assertEqual(ts.schema, 'public')

    def test_text_search_requires_schema(self):
        """Test that schema is required."""
        with self.assertRaises(pydantic.ValidationError):
            text_search.TextSearch()

    def test_text_search_with_configurations(self):
        """Test creating text search with configurations."""
        c = text_search.Configuration(name='my_config', parser='default')
        ts = text_search.TextSearch(schema='public', configurations=[c])
        self.assertEqual(len(ts.configurations), 1)

    def test_text_search_with_dictionaries(self):
        """Test creating text search with dictionaries."""
        d = text_search.Dictionary(name='my_dict', template='snowball')
        ts = text_search.TextSearch(schema='public', dictionaries=[d])
        self.assertEqual(len(ts.dictionaries), 1)

    def test_text_search_with_parsers(self):
        """Test creating text search with parsers."""
        p = text_search.Parser(name='my_parser', sql='CREATE ...')
        ts = text_search.TextSearch(schema='public', parsers=[p])
        self.assertEqual(len(ts.parsers), 1)

    def test_text_search_with_templates(self):
        """Test creating text search with templates."""
        t = text_search.Template(
            name='my_template', lexize_function='my_lexize'
        )
        ts = text_search.TextSearch(schema='public', templates=[t])
        self.assertEqual(len(ts.templates), 1)

    def test_text_search_with_all_components(self):
        """Test creating text search with all components."""
        c = text_search.Configuration(name='my_config', parser='default')
        d = text_search.Dictionary(name='my_dict', template='snowball')
        p = text_search.Parser(name='my_parser', sql='CREATE ...')
        t = text_search.Template(
            name='my_template', lexize_function='my_lexize'
        )
        ts = text_search.TextSearch(
            schema='public',
            configurations=[c],
            dictionaries=[d],
            parsers=[p],
            templates=[t],
        )
        self.assertEqual(len(ts.configurations), 1)
        self.assertEqual(len(ts.dictionaries), 1)
        self.assertEqual(len(ts.parsers), 1)
        self.assertEqual(len(ts.templates), 1)

    def test_text_search_no_additional_properties(self):
        """Test that additional properties are forbidden."""
        with self.assertRaises(pydantic.ValidationError):
            text_search.TextSearch(schema='public', invalid_field='value')

    def test_text_search_model_dump(self):
        """Test serializing TextSearch to dict."""
        ts = text_search.TextSearch(schema='public')
        data = ts.model_dump(exclude_none=True)
        self.assertIn('schema', data)

    def test_text_search_model_dump_json(self):
        """Test serializing TextSearch to JSON."""
        ts = text_search.TextSearch(schema='public')
        json_str = ts.model_dump_json(exclude_none=True)
        self.assertIn('public', json_str)


if __name__ == '__main__':
    unittest.main()
