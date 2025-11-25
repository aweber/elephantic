"""Tests for Project Pydantic models."""

import unittest

import pydantic

from elephantic.models import project


class TestExtension(unittest.TestCase):
    """Test Extension model."""

    def test_extension_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            project.Extension(schema='public')

    def test_extension_with_name_only(self):
        """Test creating extension with just name."""
        ext = project.Extension(name='pg_stat_statements')
        self.assertEqual(ext.name, 'pg_stat_statements')
        self.assertIsNone(ext.schema)

    def test_extension_with_all_fields(self):
        """Test creating extension with all fields."""
        ext = project.Extension(
            name='postgis',
            schema='public',
            version='3.0.0',
            cascade=True,
            comment='PostGIS extension',
        )
        self.assertEqual(ext.name, 'postgis')
        self.assertEqual(ext.version, '3.0.0')
        self.assertTrue(ext.cascade)


class TestLanguage(unittest.TestCase):
    """Test Language model."""

    def test_language_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            project.Language(trusted=True)

    def test_language_with_name_only(self):
        """Test creating language with just name."""
        lang = project.Language(name='plpython3u')
        self.assertEqual(lang.name, 'plpython3u')
        self.assertIsNone(lang.trusted)

    def test_language_with_all_fields(self):
        """Test creating language with all fields."""
        lang = project.Language(
            name='plpgsql',
            comment='PL/pgSQL procedural language',
            trusted=True,
            replace=True,
            handler='plpgsql_call_handler',
            inline_handler='plpgsql_inline_handler',
            validator='plpgsql_validator',
        )
        self.assertEqual(lang.name, 'plpgsql')
        self.assertTrue(lang.trusted)
        self.assertEqual(lang.handler, 'plpgsql_call_handler')


class TestProject(unittest.TestCase):
    """Test Project model."""

    def test_project_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            project.Project(encoding='UTF8')

    def test_project_with_name_only(self):
        """Test creating project with just name."""
        proj = project.Project(name='mydb')
        self.assertEqual(proj.name, 'mydb')
        self.assertIsNone(proj.encoding)

    def test_project_with_extensions(self):
        """Test creating project with extensions."""
        ext = project.Extension(name='pg_stat_statements')
        proj = project.Project(
            name='mydb',
            extensions=[ext],
        )
        self.assertEqual(len(proj.extensions), 1)

    def test_project_with_languages(self):
        """Test creating project with languages."""
        lang = project.Language(name='plpython3u')
        proj = project.Project(
            name='mydb',
            languages=[lang],
        )
        self.assertEqual(len(proj.languages), 1)

    def test_project_with_all_fields(self):
        """Test creating project with all fields."""
        ext = project.Extension(name='postgis')
        lang = project.Language(name='plpgsql')
        proj = project.Project(
            name='mydb',
            encoding='UTF8',
            stdstrings=True,
            superuser='postgres',
            extensions=[ext],
            languages=[lang],
        )
        self.assertEqual(proj.name, 'mydb')
        self.assertEqual(proj.encoding, 'UTF8')
        self.assertTrue(proj.stdstrings)
        self.assertEqual(proj.superuser, 'postgres')


if __name__ == '__main__':
    unittest.main()
