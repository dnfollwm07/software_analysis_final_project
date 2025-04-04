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

# Default target file
TARGET_FILE="examples/src/sample_code.cpp"
BUILD_DIR="build"

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
    -h|--help)
      echo -e "${BOLD}${BLUE}Usage:${NC} $0 [-t|--target <target_file>] [-b|--build-dir <build_directory>]"
      echo -e "${BOLD}Run the LLM-assisted code repair pipeline using CMake${NC}"
      echo ""
      echo -e "${BOLD}${BLUE}Options:${NC}"
      echo -e "  ${CYAN}-t, --target${NC}      Target file to analyze and repair (default: src/sample_code.cpp)"
      echo -e "  ${CYAN}-b, --build-dir${NC}   Build directory (default: build)"
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

# Ensure the target file exists
if [ ! -f "$TARGET_FILE" ]; then
  print_error "Error: Target file '$TARGET_FILE' not found"
  exit 1
fi

print_header "LLM-Assisted Code Repair Pipeline"
print_info "Target file: ${BOLD}$TARGET_FILE${NC}"
print_info "Build directory: ${BOLD}$BUILD_DIR${NC}"

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
if command -v infer &> /dev/null; then
  print_info "Running Infer static analyzer..."
  infer run --skip-analysis-in-path "build/_deps" --skip-analysis-in-path "examples/tests" --reactive --compilation-database "$BUILD_DIR/compile_commands.json"

  print_success "Infer analysis complete. Results in 'infer-out' directory."
else
  print_warning "Infer not found. Static analysis skipped."
  print_info "Please install Infer: https://fbinfer.com/"
fi

# Step 3: Build the project with CMake
print_step "3" "Building the project"
print_info "Compiling code..."
cmake --build "$BUILD_DIR" --config Debug
print_success "Build successful"

# Step 4: Run tests with CTest
print_step "4" "Running tests"
TARGET_BASENAME=$(basename "$TARGET_FILE" .cpp)
# Determine the test name based on the target file
if [[ "$TARGET_BASENAME" == "sample_code" ]]; then
  TEST_FILTER="ConfigStoreTest"
else
  # This assumes test class names follow the pattern ClassNameTest
  TEST_FILTER="${TARGET_BASENAME%.*}Test"
fi

cd "$BUILD_DIR"
if [ -z "$TEST_FILTER" ]; then
  # Run all tests
  print_info "Running all tests..."
  ctest -C Debug --output-on-failure
else
  # Run specific tests related to the target file
  print_info "Running tests with filter: ${BOLD}$TEST_FILTER${NC}"
  ctest -C Debug --output-on-failure -R "$TEST_FILTER"
fi
cd ..

print_success "Test execution complete."

# Step 5: Run code repair with LLM
print_step "5" "Running LLM-assisted code repair"
print_info "This step would use the LLM API to generate repairs."
print_info "To implement this step, run: ${CYAN}python -m src.llm.repair --target=$TARGET_FILE${NC}"

print_success "Pipeline execution complete."
print_header "End of Pipeline" 