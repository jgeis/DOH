# Testing Documentation

## Overview

This directory contains comprehensive unit, integration, and regression tests for the DOH Plotly Dashboard system.

## Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Pytest configuration and shared fixtures
├── test_dashboard_utils.py        # Unit tests for dashboard utilities
├── test_db_utils.py               # Unit tests for database utilities
├── test_multi_dashboard.py        # Integration tests for main app
├── test_pages.py                  # Tests for individual dashboard pages
└── test_regression.py             # Regression tests for critical functionality
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Regression tests only
pytest -m regression

# Run tests in a specific file
pytest tests/test_dashboard_utils.py

# Run a specific test
pytest tests/test_dashboard_utils.py::TestCountSuppression::test_format_count_display_above_threshold
```

### Run Tests with Coverage

```bash
# Generate coverage report
pytest --cov=. --cov-report=html

# View the report
open htmlcov/index.html
```

### Run Tests in Parallel (faster)

```bash
pytest -n auto
```

### Run Tests with Verbose Output

```bash
pytest -v
```

## Test Categories

### Unit Tests (`-m unit`)

Test individual functions and methods in isolation. These tests:
- Run very fast
- Don't require database connections
- Use mocking for external dependencies
- Cover edge cases and boundary conditions

Files:
- `test_dashboard_utils.py` - Dashboard utility functions
- `test_db_utils.py` - Database connection and query utilities

### Integration Tests (`-m integration`)

Test how components work together. These tests:
- May take longer to run
- Test actual Dash app functionality
- Use Selenium for browser testing
- Verify page rendering and navigation

Files:
- `test_multi_dashboard.py` - Main application
- `test_pages.py` - Individual page loading

### Regression Tests (`-m regression`)

Test critical functionality to prevent regressions. These tests:
- Document known behavior patterns
- Cover historical bugs
- Test complete user workflows
- Verify edge cases that previously caused issues

Files:
- `test_regression.py` - All regression tests

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `sample_dataframe` - Sample data for testing
- `sample_dataframe_with_suppression` - Data with values below threshold
- `sample_filter_values` - Filter values for testing
- `mock_db_connection` - Mock database connection
- `dash_app` - Dash application instance
- `dash_duo` - Selenium-based Dash testing

## Writing New Tests

### Basic Test Structure

```python
import pytest

class TestFeatureName:
    """Test suite for feature."""
    
    def test_specific_behavior(self):
        """Test that specific behavior works correctly."""
        # Arrange
        input_data = create_test_data()
        
        # Act
        result = function_to_test(input_data)
        
        # Assert
        assert result == expected_value
```

### Using Fixtures

```python
def test_with_fixture(sample_dataframe):
    """Test using a fixture."""
    result = process_data(sample_dataframe)
    assert len(result) > 0
```

### Marking Tests

```python
@pytest.mark.unit
def test_unit_example():
    """Unit test example."""
    pass

@pytest.mark.integration
def test_integration_example():
    """Integration test example."""
    pass

@pytest.mark.slow
def test_slow_example():
    """Test that takes a long time."""
    pass
```

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements-dev.txt
    pytest --cov=. --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Code Coverage

Current coverage goals:
- **Utility functions**: >90% coverage
- **Database operations**: >85% coverage
- **Dashboard components**: >80% coverage
- **Overall**: >80% coverage

View coverage report:
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## Common Issues

### Selenium/WebDriver Issues

If browser tests fail:
```bash
# Update webdriver
pip install --upgrade webdriver-manager selenium
```

### Import Errors

Ensure project root is in Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Database Connection Errors

Tests use SQLite in-memory databases by default. Ensure:
- `USE_MSSQL` environment variable is set to `false`
- SQLite database file exists for integration tests

## Best Practices

1. **Test Independence**: Each test should be independent and not rely on other tests
2. **Fast Tests**: Keep unit tests fast (<1 second each)
3. **Clear Names**: Use descriptive test and fixture names
4. **Documentation**: Add docstrings explaining what each test verifies
5. **Arrange-Act-Assert**: Follow the AAA pattern for clarity
6. **Mock External Dependencies**: Use mocks for databases, APIs, etc.
7. **Test Edge Cases**: Include tests for boundary conditions and error cases

## Debugging Tests

### Run with debugging

```bash
# Run with verbose output and stop on first failure
pytest -vx

# Run specific test with print statements visible
pytest -s tests/test_dashboard_utils.py::test_name

# Drop into debugger on failure
pytest --pdb
```

### Using iPython debugger

```python
def test_example():
    import ipdb; ipdb.set_trace()
    # Test code here
```

## Performance Testing

Mark slow tests to skip during development:

```bash
# Skip slow tests
pytest -m "not slow"

# Run only slow tests
pytest -m slow
```

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Add regression tests for bug fixes
4. Update this README if adding new test categories
5. Maintain or improve code coverage

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Dash Testing Documentation](https://dash.plotly.com/testing)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
