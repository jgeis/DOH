# Testing Quick Start Guide

## Installation

Install test dependencies:
```bash
pip install -r requirements-dev.txt
```

## Running Tests

### Quick Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run unit tests only (fast)
pytest -m unit

# Run integration tests
pytest -m integration

# Run regression tests
pytest -m regression

# Run tests in parallel (faster)
pytest -n auto
```

### Using the Test Runner Script

```bash
# Make executable (first time only)
chmod +x run_tests.sh

# Run all tests
./run_tests.sh

# Run specific test types
./run_tests.sh unit
./run_tests.sh integration
./run_tests.sh regression
./run_tests.sh fast        # Excludes slow tests
./run_tests.sh coverage    # With coverage report
./run_tests.sh parallel    # Run in parallel

# Run specific test file
./run_tests.sh specific tests/test_dashboard_utils.py
```

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── test_dashboard_utils.py     # Unit tests for dashboard utilities
├── test_db_utils.py            # Unit tests for database utilities
├── test_multi_dashboard.py     # Integration tests for main app
├── test_pages.py               # Tests for dashboard pages
└── test_regression.py          # Regression tests
```

## What's Tested

### Unit Tests
- ✅ Count suppression logic
- ✅ Filter label standardization
- ✅ Data formatting functions
- ✅ County filtering and aggregation
- ✅ Percentage display with suppression
- ✅ Sorting algorithms
- ✅ Chart dimension calculations

### Integration Tests
- ✅ Dash app initialization
- ✅ Page routing and navigation
- ✅ Tab rendering
- ✅ Callback functionality
- ✅ Page registration

### Regression Tests
- ✅ Critical privacy features (count suppression)
- ✅ Statewide aggregation accuracy
- ✅ Sort order consistency
- ✅ Filter behavior
- ✅ Data integrity workflows
- ✅ Edge cases and boundary conditions

## Viewing Coverage Reports

After running with coverage:
```bash
open htmlcov/index.html
```

## Common Test Commands

```bash
# Run tests with verbose output
pytest -v

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Run specific test
pytest tests/test_dashboard_utils.py::TestCountSuppression::test_format_count_display_above_threshold

# Run tests matching a pattern
pytest -k "suppression"
```

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Install dependencies
  run: pip install -r requirements-dev.txt

- name: Run tests with coverage
  run: pytest --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Documentation

See [tests/README.md](tests/README.md) for detailed testing documentation.
