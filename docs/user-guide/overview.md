# User Guide Overview

Welcome to the PyDanSQL user guide. This section provides detailed information about using PyDanSQL in your projects.

## What is PyDanSQL?

PyDanSQL is a Python library that bridges the gap between Pydantic models and SQL databases. It provides:

- **Type Safety**: Leverages Python's type system and Pydantic validation
- **Query Building**: Intuitive, Pythonic API for SQL query construction
- **Data Validation**: Automatic validation of inputs and outputs using Pydantic
- **Flexibility**: Works with your existing database schemas

## Design Philosophy

PyDanSQL is designed with several key principles:

1. **Explicit over Implicit**: Query construction should be clear and obvious
2. **Type Safety**: Maximum use of Python's type system to catch errors early
3. **Pythonic**: Feels natural to Python developers
4. **Composable**: Build complex queries from simple building blocks
5. **Performance**: Minimal overhead while maintaining safety

## Core Components

### Models

Models are Pydantic classes that define your data structure. They provide:

- Data validation
- Type coercion
- Serialization/deserialization
- Documentation through type hints

### Query Builder

The query builder provides a fluent API for constructing SQL queries:

- Method chaining for readability
- Type-safe parameter handling
- Support for complex conditions
- Join operations

### Executor

The executor handles:

- Database connection management
- Query execution
- Result mapping to Pydantic models
- Transaction management

## Topics

Continue reading to learn more about specific topics:

- [Query Building](query-building.md) - Learn how to construct queries
- [Executing Queries](executing-queries.md) - Learn about query execution and results
