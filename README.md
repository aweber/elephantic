# elephantic

An ORMish library based on Pydantic for building and executing SQL queries.

## Features

- Modern Python (3.12+) with type hints
- Built on Pydantic for robust data validation
- Parse SQL queries into Pydantic models
- SQL query building and execution
- Diff model based SQL objects
- Type-safe database operations

## Installation

```bash
pip install elephantic
```

## Development

This project uses [Hatch](https://hatch.pypa.io/) for project management.

### Setup

```bash
# Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run tests with coverage
coverage run -m unittest discover
coverage report
```

### Code Quality

This project uses:
- **Ruff** for linting and formatting
- **pre-commit** for automated checks

```bash
# Run ruff manually
ruff check .
ruff format .

# Run pre-commit on all files
pre-commit run --all-files
```

## License

BSD-3-Clause
