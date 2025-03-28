#!/bin/bash

# LLM-Assisted Code Repair Pipeline
# This script runs the full code repair pipeline on a target file

set -e

# Default target file
TARGET_FILE="src/sample_code.cpp"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -t|--target)
      TARGET_FILE="$2"
      shift
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [-t|--target <target_file>]"
      echo "Run the LLM-assisted code repair pipeline"
      echo ""
      echo "Options:"
      echo "  -t, --target    Target file to analyze and repair (default: src/sample_code.cpp)"
      echo "  -h, --help      Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help to see available options"
      exit 1
      ;;
  esac
done

# Ensure the target file exists
if [ ! -f "$TARGET_FILE" ]; then
  echo "Error: Target file '$TARGET_FILE' not found"
  exit 1
fi

echo "==== LLM-Assisted Code Repair Pipeline ===="
echo "Target file: $TARGET_FILE"
echo ""

# Create necessary directories
mkdir -p results logs

# Step 1: Static Analysis
echo "Step 1: Running static analysis..."
if command -v infer &> /dev/null; then
  infer run --enable-issue-type NULL_DEREFERENCE,MEMORY_LEAK,BUFFER_OVERRUN,UNINITIALIZED_VALUE -- g++ -std=c++11 "$TARGET_FILE" -o "${TARGET_FILE%.cpp}"
  echo "Infer analysis complete. Results in 'infer-out' directory."
else
  echo "Warning: Infer not found. Static analysis skipped."
  echo "Please install Infer: https://fbinfer.com/"
fi

# Step 2: Generate and run tests
echo ""
echo "Step 2: Running tests..."
TARGET_BASENAME=$(basename "$TARGET_FILE" .cpp)
TEST_FILE="tests/test_${TARGET_BASENAME}.cpp"

if [ -f "$TEST_FILE" ]; then
  echo "Compiling test file: $TEST_FILE"
  g++ -std=c++11 "$TEST_FILE" -o "tests/test_${TARGET_BASENAME}"
  
  echo "Running tests..."
  "./tests/test_${TARGET_BASENAME}"
  
  echo "Test execution complete."
else
  echo "Warning: Test file '$TEST_FILE' not found. Test step skipped."
fi

# Step 3: Run code repair with LLM
echo ""
echo "Step 3: Running LLM-assisted code repair..."
echo "This step would use the LLM API to generate repairs."
echo "To implement this step, run: python -m src.llm.repair --target=$TARGET_FILE"

echo ""
echo "Pipeline execution complete."
echo "==== End of Pipeline ====" 