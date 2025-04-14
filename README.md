# Nosey-pytest

A tool suite for migrating test suites from nose to pytest.

## Overview

`nosey-pytest` is a comprehensive toolkit designed to help Python projects migrate from the now-unmaintained nose testing framework to pytest. As of Python 3.12, nose is no longer compatible due to its dependency on the removed `imp` module and other deprecated features.

This toolkit provides comprehensive support for migrating nose tests to pytest, covering the vast majority of patterns described in the migration guide. While some complex patterns may still require manual intervention (such as nested yield tests or complex test fixtures), the automated conversions handle most common cases.

## Features

- Automatic scanning for nose tests in Python projects
- Automated migration of nose tests to pytest with transformation patterns
- Integration with nose2pytest for comprehensive assertion conversions
- Verification of migrated tests
- Progress tracking for large migrations
- Detailed migration reports
- Git repository integration

## Installation

```bash
# Install from source
git clone https://github.com/eric-downes/nosey_pytest.git
cd nosey_pytest

# Initialize the nose2pytest submodule
git submodule update --init --recursive

# Install the package
pip install -e .
```

## Usage

### One-step Migration

To migrate a Git repository with a single command:

```bash
nose-to-pytest https://github.com/username/repo.git [target_directory]
```

This will:
1. Clone the repository
2. Scan for nose tests
3. Migrate tests to pytest
4. Verify the migrations
5. Generate a migration report

### Step-by-step Migration

For more control over the migration process:

```bash
# Initialize migration tracking
pytest-migration track init

# Scan for nose tests
pytest-migration auto scan

# Run automated migration on specific files or directories
pytest-migration auto migrate path/to/tests

# Verify migrated tests
pytest-migration auto verify

# Check migration status
pytest-migration track status
```

## Transformation Patterns

The migration tool applies a comprehensive set of transformation patterns to convert nose tests to pytest:

### Import Replacements
- `from nose.tools import raises` → `import pytest`
- `import nose` → `import pytest`
- `from nose import ...` → `import pytest`
- `from nose.tools import ...` → `import pytest`

### Decorator Replacements
- `@raises(Exception)` → `@pytest.mark.xfail(raises=Exception)`
- `@expected_failure` → `@pytest.mark.xfail(reason="Expected to fail")`
- `@istest` → Removed (pytest uses naming conventions)
- `@nottest` → `@pytest.mark.skip(reason="Not a test")`

### Assert Replacements
- `self.assertEqual(a, b)` → `assert a == b`
- `self.assertNotEqual(a, b)` → `assert a != b`
- `self.assertTrue(x)` → `assert x`
- `self.assertFalse(x)` → `assert not x`
- `self.assertRaises(ExcType, func, *args)` → `with pytest.raises(ExcType): func(*args)`
- `self.assertIn(item, container)` → `assert item in container`
- `self.assertNotIn(item, container)` → `assert item not in container`
- `self.assertIs(a, b)` → `assert a is b`
- `self.assertIsNot(a, b)` → `assert a is not b`
- `self.assertIsNone(obj)` → `assert obj is None`
- `self.assertIsNotNone(obj)` → `assert obj is not None`
- `self.assertAlmostEqual(a, b)` → `assert pytest.approx(a) == b`
- `self.assertEqualSet(a, b)` → `assert set(a) == set(b)`

### Class Structure Conversions
- Remove unittest.TestCase inheritance
- `setUp()` → `@pytest.fixture(autouse=True)`
- `tearDown()` → `@pytest.fixture(autouse=True)`
- Renaming methods to follow pytest naming conventions

### Yield Test Conversions
- Simple yield tests to pytest.mark.parametrize
- Multi-parameter yield tests
- Complex test generation patterns

You can view the current patterns and add custom patterns:

```bash
# List transformation patterns
pytest-migration auto patterns

# Add a custom pattern
pytest-migration auto add-pattern
```

## Configuration

Configure the migration tool settings:

```bash
pytest-migration auto config
```

## Documentation

- [Nose to Pytest Migration Guide](nose_to_pytest_guide.md) - Detailed guide for migrating from nose to pytest
- [Nose2pytest Integration](nose2pytest_integration.md) - How to use the nose2pytest integration in our tools

## License

MIT

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Acknowledgments

- [nose2pytest](https://github.com/pytest-dev/nose2pytest) by Oliver Schoenborn, which is integrated into this toolkit
- All contributors to the pytest ecosystem