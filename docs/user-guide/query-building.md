# Query Building

This guide covers how to build SQL queries using Elephantic.

!!! note
    The API shown here is illustrative and subject to change during alpha development.

## Basic Queries

### SELECT Queries

```python
from elephantic import Query

# Select all columns
query = Query(User).select()

# Select specific columns
query = Query(User).select('id', 'name')

# With conditions
query = Query(User).select().where(active=True)
```

### INSERT Queries

```python
# Insert single record
user = User(id=1, name="John", email="john@example.com")
Query(User).insert(user)

# Insert multiple records
users = [user1, user2, user3]
Query(User).insert_many(users)
```

### UPDATE Queries

```python
# Update with conditions
Query(User).update(active=False).where(id=1)

# Update multiple fields
Query(User).update(name="Jane", email="jane@example.com").where(id=1)
```

### DELETE Queries

```python
# Delete with conditions
Query(User).delete().where(active=False)
```

## Advanced Queries

### Filtering

```python
# Simple conditions
query = Query(User).select().where(active=True, role="admin")

# Complex conditions
query = (Query(User)
    .select()
    .where(active=True)
    .where_in('role', ['admin', 'moderator']))
```

### Ordering

```python
# Order by single column
query = Query(User).select().order_by('name')

# Order by multiple columns
query = Query(User).select().order_by('name', '-created_at')  # descending
```

### Limiting

```python
# Limit results
query = Query(User).select().limit(10)

# Limit with offset
query = Query(User).select().limit(10).offset(20)
```

### Joins

```python
# Join tables
query = (Query(User)
    .select()
    .join(Post, User.id == Post.user_id)
    .where(Post.published == True))
```

## Query Composition

Queries can be built incrementally:

```python
query = Query(User).select()

if include_inactive:
    query = query.where(active=False)

if sort_by_name:
    query = query.order_by('name')

results = query.execute()
```

## Next Steps

Learn about [Executing Queries](executing-queries.md) to see how to run your queries and handle results.
