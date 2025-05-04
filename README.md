# LLM-Assisted Code Repair Pipeline

This project provides an automated pipeline for code repair using Large Language Models (LLMs). The pipeline combines static analysis, testing, and LLM-assisted code repair to automatically fix bugs in C++ code.

## Prerequisites

- CMake (version 3.10 or higher)
- C++ compiler with C++17 support
- Python 3.x
- (Optional) Infer static analyzer
- OpenAI API access

### Environment Configuration

Before running the pipeline, you need to configure the OpenAI API settings:

1. Create a `.env.local` file in the project root directory
2. Add the following content to the file:
   ```
   # OpenAI API Configuration
   OPENAI_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
   OPENAI_MODEL=qwen-plus
   OPENAI_API_KEY=your_api_key_here
   ```
3. Replace `your_api_key_here` with your actual OpenAI API key

Note: The `.env.local` file should not be committed to version control for security reasons.

## Usage

The main script `run_repair.sh` provides a complete pipeline for code repair. Here's how to use it:

```bash
./run_repair.sh [options]
```

### Available Options

| Option | Description |
|--------|-------------|
| `-b, --build-dir <build_directory>` | Specify the build directory (default: build) |
| `-r, --reset` | Reset the examples directory by deleting and recreating from run-examples |
| `--use-infer` | Enable Infer static analysis (default: false) |
| `--include-infer-in-prompt` | Include Infer results in LLM prompt (default: false) |
| `--sync` | Synchronize examples directory and exit |
| `-h, --help` | Show help message |

### Pipeline Steps

The script executes the following steps in sequence:

1. **CMake Configure**
   - Generates build system and compilation database

2. **Static Analysis** (Optional)
   - Runs Infer static analyzer if enabled
   - Processes Infer output for LLM consumption

3. **Build Project**
   - Compiles the code using CMake

4. **Run Tests**
   - Executes all tests using CTest
   - Generates test results in XML format

5. **LLM-Assisted Code Repair**
   - Uses LLM to analyze and fix code issues in the following files:
     - `run-examples/src/config_store_memory_leak.cpp`
     - `run-examples/src/config_store_null_ptr.cpp`
     - `run-examples/src/config_store_uninit_var.cpp`
   - Incorporates static analysis results if enabled

6. **Verify Fixes**
   - Rebuilds and retests the code
   - Validates that fixes resolved the issues

### Example Usage

Basic usage:
```bash
# Reset the examples directory
./run_repair.sh -r
# Using current examples directory
./run_repair.sh

```

With Infer static analysis:
```bash
./run_repair.sh --use-infer --include-infer-in-prompt
```

Specify build directory:
```bash
./run_repair.sh -b my_build
```

## Output

The pipeline generates output in the following locations:

- `output/` - Contains test results and analysis reports
- `logs/` - Contains detailed logs of the pipeline execution
- `build/` - Contains build artifacts and compilation database

## Notes

- The script requires proper permissions to execute
- Make sure all dependencies are installed before running
- For best results with Infer, ensure it's properly installed and configured
- The script will automatically create necessary directories if they don't exist
- The script processes a fixed set of example files in the `run-examples/src/` directory
