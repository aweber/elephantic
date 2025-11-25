# Installation

## Requirements

Elephantic requires Python 3.12 or later.

## Installing from PyPI

Once published, you can install Elephantic using pip:

```bash
pip install elephantic
```

## Installing from Source

To install the latest development version from source:

```bash
git clone https://github.com/aweber/elephantic.git
cd elephantic
pip install -e .
```

## Development Installation

If you want to contribute to Elephantic, install it with development dependencies:

```bash
git clone https://github.com/aweber/elephantic.git
cd elephantic
pip install -e ".[dev]"
pre-commit install
```

This will install:

- All runtime dependencies
- Development tools (ruff, coverage, pre-commit, hatch)
- Set up pre-commit hooks for code quality

## Verifying Installation

You can verify your installation by checking the version:

```python
import elephantic
print(elephantic.version)
```

## Next Steps

Continue to the [Quick Start Guide](quickstart.md) to learn how to use Elephantic.
