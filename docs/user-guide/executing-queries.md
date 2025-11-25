# Executing Queries

This guide covers how to execute queries and work with results.

!!! note
    The API shown here is illustrative and subject to change during alpha development.

## Basic Execution

### Executing SELECT Queries

```python
# Execute and get all results
users = Query(User).select().execute()

# Iterate over results
for user in Query(User).select().where(active=True):
    print(user.name)

# Get single result
user = Query(User).select().where(id=1).first()

# Get single result or raise exception
user = Query(User).select().where(id=1).one()
```

### Executing Write Queries

```python
# INSERT
result = Query(User).insert(user).execute()

# UPDATE
affected = Query(User).update(active=False).where(id=1).execute()

# DELETE
affected = Query(User).delete().where(id=1).execute()
```

## Connection Management

### Using Connection Strings

```python
from elephantic import connect

# Create connection
conn = connect("postgresql://user:pass@localhost/db")

# Use with queries
users = Query(User).select().execute(conn)
```

### Context Managers

```python
with connect("postgresql://user:pass@localhost/db") as conn:
    users = Query(User).select().execute(conn)
```

## Transactions

### Basic Transactions

```python
with conn.transaction():
    Query(User).insert(user1).execute(conn)
    Query(User).insert(user2).execute(conn)
    # Automatically commits or rolls back on error
```

### Manual Transaction Control

```python
trans = conn.begin()
try:
    Query(User).insert(user1).execute(conn)
    Query(User).insert(user2).execute(conn)
    trans.commit()
except Exception:
    trans.rollback()
    raise
```

## Result Handling

### Working with Results

```python
# Results are Pydantic models
users = Query(User).select().execute()
for user in users:
    print(user.model_dump())  # Convert to dict
    print(user.model_dump_json())  # Convert to JSON
```

### Counting Results

```python
# Get count
count = Query(User).select().where(active=True).count()
```

### Checking Existence

```python
# Check if any results exist
exists = Query(User).select().where(email="test@example.com").exists()
```

## Error Handling

```python
from elephantic.exceptions import NoResultFound, MultipleResultsFound

try:
    user = Query(User).select().where(id=1).one()
except NoResultFound:
    print("User not found")
except MultipleResultsFound:
    print("Multiple users found")
```

## Async Support

```python
# Async execution
async with connect_async("postgresql://...") as conn:
    users = await Query(User).select().execute_async(conn)

    async for user in Query(User).select().stream():
        print(user.name)
```

## Next Steps

- Explore the [API Reference](../api/index.md) for detailed API documentation
- Read about [Contributing](../development/contributing.md) to help improve Elephantic
