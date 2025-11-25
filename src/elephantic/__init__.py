"""
Elephantic
==========

An ORMish library based on Pydantic for building and executing SQL queries.
"""

from importlib import metadata

try:
    version = metadata.version('elephantic')
except metadata.PackageNotFoundError:
    version = '0.0.0-dev'
