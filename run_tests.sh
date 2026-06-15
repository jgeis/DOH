#!/bin/bash
# Run tests with various configurations

set -e  # Exit on error

echo "DOH Dashboard Test Runner"
echo "========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest not found. Installing dependencies..."
    pip install -r requirements-dev.txt
fi

# Parse command line arguments
TEST_TYPE="${1:-all}"

case $TEST_TYPE in
    "unit")
        print_info "Running unit tests only..."
        pytest -m unit -v
        ;;
    
    "integration")
        print_info "Running integration tests only..."
        pytest -m integration -v
        ;;
    
    "regression")
        print_info "Running regression tests only..."
        pytest -m regression -v
        ;;
    
    "fast")
        print_info "Running fast tests (excluding slow tests)..."
        pytest -m "not slow" -v
        ;;
    
    "coverage")
        print_info "Running tests with coverage report..."
        pytest --cov=. --cov-report=html --cov-report=term-missing
        print_status "Coverage report generated in htmlcov/"
        ;;
    
    "parallel")
        print_info "Running tests in parallel..."
        pytest -n auto -v
        ;;
    
    "specific")
        if [ -z "$2" ]; then
            print_error "Please specify a test file or test name"
            echo "Usage: ./run_tests.sh specific tests/test_dashboard_utils.py"
            exit 1
        fi
        print_info "Running specific test: $2"
        pytest "$2" -v
        ;;
    
    "all"|*)
        print_info "Running all tests..."
        pytest -v
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    print_status "All tests passed!"
    exit 0
else
    print_error "Some tests failed!"
    exit 1
fi
