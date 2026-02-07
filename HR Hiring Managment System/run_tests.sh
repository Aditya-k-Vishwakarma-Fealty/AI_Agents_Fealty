#!/bin/bash
# Script to run all API tests

# Ensure we are in the project root
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run pytest with PYTHONPATH set to current directory
echo "Running all API tests..."
PYTHONPATH=. pytest tests/ -v

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed successfully!"
else
    echo "❌ Some tests failed."
fi

exit $EXIT_CODE
