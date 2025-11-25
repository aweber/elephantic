# Quick Start

This guide will help you get started with Elephantic.

## Basic Concepts

Elephantic is built around a few core concepts:

- **Models**: Pydantic models that represent your database tables
- **Query Builder**: Fluent API for constructing SQL queries
- **Executor**: Handles query execution and result mapping

## Your First Query

!!! note
    The following examples are illustrative. The actual API is still in development.

### Defining a Model

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    active: bool = True
```

### Building a Query

```python
from elephantic import Query

# Select query example
query = Query(User).select().where(active=True)

# Execute and get results
users = query.execute()
```

### Inserting Data

```python
new_user = User(id=1, name="John Doe", email="john@example.com")
Query(User).insert(new_user).execute()
```

### Updating Data

```python
Query(User).update(active=False).where(id=1).execute()
```

### Deleting Data

```python
Query(User).delete().where(id=1).execute()
```

## Next Steps

- Learn more in the [User Guide](../user-guide/overview.md)
- Explore the [API Reference](../api/index.md)
- Check out [Contributing Guidelines](../development/contributing.md)
