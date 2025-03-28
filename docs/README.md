# Documentation for LLM-Assisted Code Repair Project

## Overview

This project creates a framework that combines static analysis, dynamic analysis, and large language models (LLMs) to automatically repair bugs in C/C++ code.

## Architecture

The system follows a pipeline architecture:

1. **Static Analysis Phase**
   - Uses Infer to detect potential bugs in source code
   - Categorizes issues by type (memory leaks, null dereferences, etc.)
   - Filters false positives

2. **Dynamic Analysis Phase**
   - Generates test cases based on static analysis results
   - Executes tests to validate issues
   - Collects runtime information

3. **LLM-based Repair Phase**
   - Constructs prompts from analysis results
   - Sends prompts to LLM API
   - Processes repair suggestions

4. **Validation Phase**
   - Applies suggested repairs
   - Runs tests on repaired code
   - Verifies that issues are fixed

## API Documentation

### Static Analysis Module

The `static_analysis` module provides tools for detecting bugs using static analysis.

Key components:
- `InferAnalyzer`: Interface to the Infer static analyzer

### Dynamic Analysis Module

The `dynamic_analysis` module provides tools for test generation and execution.

Key components:
- `TestGenerator`: Generates test cases for specific error conditions

### LLM Module

The `llm` module handles integration with large language models for code repair.

Key components:
- `CodeRepairPrompt`: Generates prompts for LLM
- `CodeRepairManager`: Manages the repair workflow

## Configuration

Configuration is stored in JSON files in the `config` directory:

- `settings.json`: Main configuration file
- `prompt_templates/`: Directory containing templates for LLM prompts

## Error Categories

The system handles these common error types:

1. **Memory Leaks**
   - Missing deallocation
   - Resource leaks

2. **Null Pointer Dereferences**
   - Missing null checks
   - Uninitialized pointers

3. **Array Bounds Violations**
   - Off-by-one errors
   - Missing bounds checks

4. **Uninitialized Variables**
   - Using variables before assignment

## Future Work

Planned enhancements:
- Support for additional languages
- Integration with more static analyzers
- Improved test generation techniques
- Enhanced prompt engineering for better repairs 