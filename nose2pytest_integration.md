# Using nose2pytest with nosey-pytest

This guide explains how nosey-pytest integrates with nose2pytest to provide comprehensive nose-to-pytest migration.

## Overview

[nose2pytest](https://github.com/pytest-dev/nose2pytest) is a tool that focuses specifically on converting nose.tools.assert_* function calls to raw pytest assertions. Our toolkit (nosey-pytest) provides a more comprehensive migration solution that handles class structure, yield tests, fixtures, and more.

By integrating nose2pytest into our toolkit, we get the best of both worlds:

1. nosey-pytest handles high-level migration aspects (class structure, yield tests, fixtures)
2. nose2pytest handles detailed conversion of assert statements 
3. Our integration ensures consistent tracking, verification, and reporting throughout the process

## How the Integration Works

1. **Two-step conversion process**: 
   - First, nosey-pytest applies its own transformations for class structure, fixtures, etc.
   - Then, it passes the transformed code through nose2pytest for assertion conversions
   
2. **Drop-in replacements for unsupported assertions**:
   - Some nose.tools.assert_* functions don't have direct raw assert equivalents
   - We provide a pytest_assert_tools.py module with compatible implementations

## Usage Options

### Command Line Options

Both migrate.py and pytest_migration.py tools support nose2pytest integration:

```bash
# Run with nose2pytest integration (default)
nose-to-pytest https://github.com/username/repo.git [target_directory]

# Disable nose2pytest integration if needed
nose-to-pytest --no-nose2pytest https://github.com/username/repo.git [target_directory]

# Using pytest-migration tool
pytest-migration auto migrate [path]

# Disable nose2pytest integration for pytest-migration
pytest-migration auto migrate --no-nose2pytest [path]
```

### Installing assertion compatibility module

If your tests use nose.tools.assert_* functions that nose2pytest can't convert to raw assertions, you can install our compatibility module:

```bash
pytest-migration auto install-assert-tools
```

This will create a file called `pytest_assert_tools.py` in your current directory. Import it in your test modules:

```python
# In your test modules
from pytest_assert_tools import * 
```

## Supported nose.tools.assert_* functions

### Automatically converted to raw assertions

The following assertion functions from nose.tools are automatically converted to raw assertions:

- assert_true(a[, msg]) → assert a[, msg]
- assert_false(a[, msg]) → assert not a[, msg]
- assert_is_none(a[, msg]) → assert a is None[, msg]
- assert_is_not_none(a[, msg]) → assert a is not None[, msg]
- assert_equal(a,b[, msg]) → assert a == b[, msg]
- assert_not_equal(a,b[, msg]) → assert a != b[, msg]
- assert_list_equal(a,b[, msg]) → assert a == b[, msg]
- assert_dict_equal(a,b[, msg]) → assert a == b[, msg]
- assert_set_equal(a,b[, msg]) → assert a == b[, msg]
- assert_sequence_equal(a,b[, msg]) → assert a == b[, msg]
- assert_tuple_equal(a,b[, msg]) → assert a == b[, msg]
- assert_multi_line_equal(a,b[, msg]) → assert a == b[, msg]
- assert_greater(a,b[, msg]) → assert a > b[, msg]
- assert_greater_equal(a,b[, msg]) → assert a >= b[, msg]
- assert_less(a,b[, msg]) → assert a < b[, msg]
- assert_less_equal(a,b[, msg]) → assert a <= b[, msg]
- assert_in(a,b[, msg]) → assert a in b[, msg]
- assert_not_in(a,b[, msg]) → assert a not in b[, msg]
- assert_is(a,b[, msg]) → assert a is b[, msg]
- assert_is_not(a,b[, msg]) → assert a is not b[, msg]
- assert_is_instance(a,b[, msg]) → assert isinstance(a, b)[, msg]
- assert_count_equal(a,b[, msg]) → assert collections.Counter(a) == collections.Counter(b)[, msg]
- assert_not_regex(a,b[, msg]) → assert not re.search(b, a)[, msg]
- assert_regex(a,b[, msg]) → assert re.search(b, a)[, msg]
- assert_almost_equal(a,b[, msg]) → assert a == pytest.approx(b, abs=1e-7)[, msg]
- assert_almost_equal(a,b, delta[, msg]) → assert a == pytest.approx(b, abs=delta)[, msg]
- assert_almost_equal(a, b, places[, msg]) → assert a == pytest.approx(b, abs=1e-places)[, msg]
- assert_not_almost_equal(a,b[, msg]) → assert a != pytest.approx(b, abs=1e-7)[, msg]
- assert_not_almost_equal(a,b, delta[, msg]) → assert a != pytest.approx(b, abs=delta)[, msg]
- assert_not_almost_equal(a,b, places[, msg]) → assert a != pytest.approx(b, abs=1e-places)[, msg]

### Available in pytest_assert_tools.py

These functions are provided by our compatibility module:

- assert_dict_contains_subset(subset, dictionary, msg=None)
- assert_raises_regex(exception, regex, callable_obj=None, *args, **kwargs)
- assert_raises_regexp (same as assert_raises_regex)
- assert_regexp_matches(text, regex, msg=None)
- assert_warns_regex(warning, regex, callable_obj=None, *args, **kwargs)

## Manual Replacement Needed

Some nose functions need to be replaced manually:

- `assert_raises`: Use `pytest.raises` instead
- `@raises`: Replace with `@pytest.mark.xfail(raises=...)` or (better) use `with pytest.raises(...):` inside the test function
- Nose functions used as context managers: These need manual conversion

## Tips for a Successful Migration

1. Run the migration with nose2pytest integration first, which will handle most cases
2. Install the assert_tools module for the remaining assert functions
3. Manually fix any remaining issues
4. Verify all tests pass

## References

- [nose2pytest GitHub repository](https://github.com/pytest-dev/nose2pytest)
- [pytest documentation](https://docs.pytest.org/)