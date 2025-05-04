#!/bin/bash

# LLM-Assisted Code Repair Pipeline
# This script runs the full code repair pipeline on a target file

set -e

# 定义颜色常量
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 定义输出函数
print_header() {
  echo -e "\n${BOLD}${BLUE}===== $1 =====${NC}\n"
}

print_step() {
  echo -e "\n${BOLD}${CYAN}Step $1: $2${NC}"
  echo -e "${CYAN}$(printf '=%.0s' {1..50})${NC}"
}

print_success() {
  echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
  echo -e "${RED}✗ $1${NC}"
}

print_info() {
  echo -e "${MAGENTA}ℹ $1${NC}"
}

# Function to reset examples directory
reset_examples() {
  print_info "Resetting examples directory..."
  rm -rf run-examples
  cp -r examples run-examples
  print_success "Examples directory reset complete"
}

BUILD_DIR="build"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$PROJECT_ROOT/output"
mkdir -p $OUTPUT_DIR

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -t|--target)
      TARGET_FILE="$2"
      shift
      shift
      ;;
    -b|--build-dir)
      BUILD_DIR="$2"
      shift
      shift
      ;;
    -r|--reset)
      reset_examples
      shift
      ;;
    --use-infer)
      USE_INFER=true
      shift
      ;;
    --include-infer-in-prompt)
      INCLUDE_INFER_IN_PROMPT=true
      shift
      ;;
    -h|--help)
      echo -e "${BOLD}${BLUE}Usage:${NC} $0 [-t|--target <target_file>] [-b|--build-dir <build_directory>] [-r|--reset] [--use-infer] [--include-infer-in-prompt]"
      echo -e "${BOLD}Run the LLM-assisted code repair pipeline using CMake${NC}"
      echo ""
      echo -e "${BOLD}${BLUE}Options:${NC}"
      echo -e "  ${CYAN}-t, --target${NC}      Target file to analyze and repair (default: src/sample_code.cpp)"
      echo -e "  ${CYAN}-b, --build-dir${NC}   Build directory (default: build)"
      echo -e "  ${CYAN}-r, --reset${NC}       Reset examples directory (delete and recreate from run-examples)"
      echo -e "  ${CYAN}--use-infer${NC}       Enable Infer static analysis (default: false)"
      echo -e "  ${CYAN}--include-infer-in-prompt${NC}  Include Infer results in LLM prompt (default: false)"
      echo -e "  ${CYAN}-h, --help${NC}        Show this help message"
      exit 0
      ;;
    *)
      print_error "Unknown option: $1"
      echo -e "Use ${CYAN}--help${NC} to see available options"
      exit 1
      ;;
  esac
done

# Set default values for new options
USE_INFER=${USE_INFER:-false}
INCLUDE_INFER_IN_PROMPT=${INCLUDE_INFER_IN_PROMPT:-false}

print_header "LLM-Assisted Code Repair Pipeline"
print_info "Build directory: ${BOLD}$BUILD_DIR${NC}"
print_info "Use Infer: ${BOLD}$USE_INFER${NC}"
print_info "Include Infer in prompt: ${BOLD}$INCLUDE_INFER_IN_PROMPT${NC}"

# Create necessary directories
mkdir -p results logs

# Create build directory if it doesn't exist
mkdir -p "$BUILD_DIR"

# Step 1: CMake Configure
print_step "1" "CMake Configure"
print_info "Generating build system and compilation database..."
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=1 -B "$BUILD_DIR" -S .
print_success "CMake configuration complete"


# Step 2: Static Analysis
print_step "2" "Running static analysis"
if [[ "$USE_INFER" == "true" ]]; then
  if command -v infer &> /dev/null; then
    print_info "Running Infer static analyzer..."
    infer run --skip-analysis-in-path "build/_deps" \
      --reactive \
      --compilation-database "$BUILD_DIR/compile_commands.json" \
      -o "$OUTPUT_DIR/infer-out"

    print_success "Infer analysis complete. Results in 'infer-out' directory."
    
    # Process Infer output to make it LLM-friendly
    print_info "Processing Infer output to make it more LLM-friendly..."
  else
    print_warning "Infer not found. Static analysis skipped."
    print_info "Please install Infer: https://fbinfer.com/"
  fi
else
  print_info "Skipping Infer static analysis as requested"
fi

# Step 3: Build the project with CMake
print_step "3" "Building the project"
print_info "Compiling code..."
cmake --build "$BUILD_DIR" --config Debug
print_success "Build successful"

# Step 4: Run tests with CTest
print_step "4" "Running tests"

cd "$BUILD_DIR"
# Run all tests
print_info "Running all tests..."
ctest -C Debug --output-on-failure --output-junit "$OUTPUT_DIR/test-results.xml" || true

# Check if all tests passed
if grep -q "failures=\"0\"" "$OUTPUT_DIR/test-results.xml"; then
    print_success "All tests passed! No need for code repair."
    print_header "End of Pipeline"
    exit 0
else
    print_warning "Some tests failed. Proceeding to code repair..."
    # Extract failed test information for LLM
    failed_tests=$(grep -A 1 "failure" "$OUTPUT_DIR/test-results.xml" | grep "testcase" | sed 's/.*name="\([^"]*\).*/\1/')
    echo "$failed_tests" > "$OUTPUT_DIR/failed_tests.txt"
fi

cd ..

# Step 5: Run code repair with LLM
print_step "5" "Running LLM-assisted code repair"
if [[ "$USE_INFER" == "true" && "$INCLUDE_INFER_IN_PROMPT" == "true" ]]; then
    python3 -m src.llm.repair output/infer-out/report.json --failed-tests "$OUTPUT_DIR/failed_tests.txt" --use-infer --include-infer-in-prompt
else
    python3 -m src.llm.repair --failed-tests "$OUTPUT_DIR/failed_tests.txt"
fi

# Step 6: Verify fixes with tests
print_step "6" "Verifying fixes with tests"

cd "$BUILD_DIR"
print_info "Running tests again to verify fixes..."
ctest -C Debug --output-on-failure --output-junit "$OUTPUT_DIR/test-results-after-fix.xml" || true

# Check if all tests passed after fixes
if grep -q "failures=\"0\"" "$OUTPUT_DIR/test-results-after-fix.xml"; then
    print_success "All tests passed after LLM fixes!"
else
    print_warning "Some tests still failed after LLM fixes."
    print_info "Please review the test results in $OUTPUT_DIR/test-results-after-fix.xml"
fi

cd ..

print_success "Pipeline execution complete."
print_header "End of Pipeline" 