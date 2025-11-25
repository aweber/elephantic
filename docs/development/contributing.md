# Contributing to Elephantic

Thank you for your interest in contributing to Elephantic! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.12 or later
- Git
- A GitHub account

### Setting Up Your Environment

1. Fork the repository on GitHub
2. Clone your fork:

```bash
git clone https://github.com/YOUR-USERNAME/elephantic.git
cd elephantic
```

3. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

4. Install pre-commit hooks:

```bash
pre-commit install
```

## Development Workflow

### Creating a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Making Changes

1. Make your changes to the code
2. Add tests for your changes
3. Ensure all tests pass:

```bash
coverage run -m unittest discover
coverage report
```

4. Check code quality:

```bash
ruff check .
ruff format .
# or run all pre-commit hooks
pre-commit run --all-files
```

### Writing Tests

We use Python's built-in `unittest` framework:

```python
import unittest
from elephantic import Query

class TestQuery(unittest.TestCase):
    def test_basic_select(self):
        query = Query(User).select()
        self.assertIsNotNone(query)

    def test_where_clause(self):
        query = Query(User).select().where(active=True)
        # Add assertions

if __name__ == '__main__':
    unittest.main()
```

### Documentation

- Add docstrings to all public APIs using Google style
- Update relevant documentation in the `docs/` directory
- Build and preview documentation:

```bash
mkdocs serve
```

### Committing Changes

Pre-commit hooks will automatically:

- Format code with Ruff
- Check for common issues
- Validate YAML and TOML files

Commit messages should be clear and descriptive:

```bash
git commit -m "Add support for JOIN operations"
```

## Submitting a Pull Request

1. Push your branch to your fork:

```bash
git push origin feature/your-feature-name
```

2. Open a pull request on GitHub
3. Describe your changes and reference any related issues
4. Wait for review and address any feedback

## Code Style

- Follow PEP 8 guidelines (enforced by Ruff)
- Use type hints for all function signatures
- Write clear, concise docstrings
- Keep functions focused and small
- Add comments for complex logic

## Testing Guidelines

- Write tests for all new features
- Maintain or improve code coverage
- Test edge cases and error conditions
- Use descriptive test names

## Getting Help

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Ask questions in discussions

## Code Review Process

All contributions go through code review. Reviewers will check:

- Code quality and style
- Test coverage
- Documentation
- Design and architecture

## License

By contributing, you agree that your contributions will be licensed under the BSD-3-Clause license.
