# LLM-Assisted Code Repair Project

This project implements a framework for automated code repair using Large Language Models (LLMs) combined with static and dynamic analysis tools.

## Project Structure

- `src/`: Source code for the framework
  - `static_analysis/`: Integration with static analysis tools (e.g., Infer)
  - `dynamic_analysis/`: Test generation and dynamic analysis tools
  - `llm/`: LLM integration for code repair
  - `utils/`: Utility functions and helpers
  - `sample_code.cpp`: Sample C++ code with intentional bugs for testing
- `tests/`: Test cases and validation
- `config/`: Configuration files and templates
- `docs/`: Documentation

## Features

The framework combines three key components:

1. **Static Analysis**: Uses tools like Infer to identify potential bugs in code
2. **Dynamic Analysis**: Generates test cases to validate code behavior
3. **LLM Integration**: Uses LLMs to suggest code repairs based on analysis results

## Getting Started

### Prerequisites

- Python 3.8+
- C++ compiler (for sample code)
- Infer static analyzer
- Valgrind (optional, for memory analysis)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure your LLM API key in `config/settings.json`

### Usage

1. Run static analysis on sample code:
   ```
   python -m src.static_analysis.run --target=src/sample_code.cpp
   ```

2. Generate and run tests:
   ```
   python -m src.dynamic_analysis.run --target=src/sample_code.cpp
   ```

3. Generate code repairs:
   ```
   python -m src.llm.repair --target=src/sample_code.cpp
   ```

## Example

The `src/sample_code.cpp` file contains a `ConfigStore` class with intentional bugs:
- Memory leaks
- Null pointer dereferences
- Array bounds violations
- Uninitialized variables

The framework:
1. Identifies these bugs using static analysis
2. Validates the issues using dynamic analysis/testing
3. Generates fixes using LLM suggestions

## License

This project is licensed under the MIT License - see the LICENSE file for details. 