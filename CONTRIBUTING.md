# Contributing to nosey-pytest

Thank you for your interest in contributing to nosey-pytest! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pytest
- fissix (required for nose2pytest)
- gitpython (for Git repository operations)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/eric-downes/nosey_pytest.git
   cd nosey_pytest
   ```

2. Initialize the nose2pytest submodule:
   ```bash
   git submodule update --init --recursive
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Install development dependencies:
   ```bash
   pip install pytest fissix
   ```

## Running Tests

Run the test suite with pytest:

```bash
pytest
```

## Making Changes

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes:
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed

3. Run the tests to ensure your changes don't break existing functionality:
   ```bash
   pytest
   ```

4. Commit your changes with a descriptive commit message:
   ```bash
   git commit -am "Add new feature: your feature description"
   ```

## Project Structure

- `src/` - Core library modules
  - `automigrate.py` - Contains automated migration logic
  - `tracking.py` - Migration progress tracking
  - `assert_tools.py` - Compatibility module for unsupported nose assertions

- `example/` - Example test files for demonstration
- `tests/` - Test suite
- `nose2pytest/` - Submodule containing nose2pytest tool

## Adding New Transformation Patterns

To add a new transformation pattern:

1. Open `src/automigrate.py`
2. Find the `COMMON_TRANSFORMATIONS` list
3. Add a new pattern dictionary with:
   - `id`: Unique identifier for the pattern
   - `pattern`: Regular expression to match
   - `replacement`: String or function to replace matches
   - `description`: Description of what the pattern transforms
   - `priority`: Order in which to apply (lower numbers go first)
   - `enabled`: Boolean to enable/disable the pattern

Example:
```python
{
    "id": "custom_pattern",
    "pattern": r'my_pattern\(([^)]+)\)',
    "replacement": r'new_pattern(\1)',
    "description": 'Convert my_pattern() to new_pattern()',
    "priority": 50,
    "enabled": True
}
```

## Integration with nose2pytest

When adding features that interact with nose2pytest, remember:

1. Always check for the presence of the nose2pytest module
2. Handle dependencies properly (fissix is required)
3. Maintain consistent tracking and reporting of conversions

## Documentation

Please update relevant documentation when making changes:

- README.md for user-facing information
- nose_to_pytest_guide.md for migration guidance
- nose2pytest_integration.md for details about nose2pytest integration
- Code comments for implementation details

## Pull Request Process

1. Push your changes to your forked repository
2. Submit a pull request to the main repository
3. Describe your changes and their purpose
4. Address any feedback or requested changes

Thank you for contributing to nosey-pytest!