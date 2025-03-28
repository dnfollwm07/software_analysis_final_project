#!/usr/bin/env python3
"""
LLM-Assisted Code Repair Framework

This script automates the process of:
1. Running tests on potentially buggy code
2. Using static analysis (Infer) to identify issues
3. Sending results to an LLM to generate fixes
4. Testing the fixed code
"""

import os
import sys
import argparse
import subprocess
import tempfile
import json
import shutil
import re
from pathlib import Path

# Set to True to enable verbose output
DEBUG = False

def log(message):
    """Print message if DEBUG is True."""
    if DEBUG:
        print(f"[DEBUG] {message}")

def compile_and_run_tests(code_file, test_file, is_correct=False):
    """
    Compile and run the test file against the specified code file.
    
    Args:
        code_file: Path to the C++ code file
        test_file: Path to the test file
        is_correct: Whether we're testing the correct implementation
    
    Returns:
        (success, output): Boolean indicating if all tests passed and the test output
    """
    log(f"Compiling and running tests: {test_file} against {code_file}")
    
    # Create bin directory if it doesn't exist
    bin_dir = Path("tests/bin")
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine the test binary name
    test_basename = os.path.basename(test_file).replace(".cpp", "")
    binary_path = bin_dir / test_basename
    
    # Compile the test file with the appropriate flag
    compile_cmd = ["g++", "-std=c++11"]
    if is_correct:
        compile_cmd.extend(["-DTEST_CORRECT"])
    compile_cmd.extend([test_file, "-o", str(binary_path)])
    
    log(f"Compile command: {' '.join(compile_cmd)}")
    
    try:
        compile_result = subprocess.run(
            compile_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        log(f"Compilation succeeded: {compile_result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed: {e.stderr}")
        return False, e.stderr
    
    # Run the tests
    try:
        test_result = subprocess.run(
            [str(binary_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Check if all tests passed by looking for "All tests passed" in the output
        success = "All tests passed" in test_result.stdout
        log(f"Tests {'passed' if success else 'failed'}: {test_result.stdout}")
        
        return success, test_result.stdout + test_result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Test execution failed: {e}")
        return False, str(e)

def run_static_analysis(code_file):
    """
    Run static analysis on the code file.
    
    Args:
        code_file: Path to the C++ code file
        
    Returns:
        (success, output): Boolean indicating if analysis ran and the analysis output
    """
    log(f"Running static analysis on: {code_file}")
    
    # Check if Infer is available
    try:
        subprocess.run(
            ["infer", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        has_infer = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        has_infer = False
        log("Infer not found, falling back to compiler warnings")
    
    if has_infer:
        # Run Infer
        try:
            infer_result = subprocess.run(
                [
                    "infer", "run", "--keep-going",
                    "--enable-issue-type", "NULL_DEREFERENCE,MEMORY_LEAK,BUFFER_OVERRUN,UNINITIALIZED_VALUE",
                    "--", "g++", "-std=c++11", code_file, "-c"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Parse Infer results
            if os.path.exists("infer-out/report.json"):
                with open("infer-out/report.json", "r") as f:
                    infer_report = json.load(f)
                
                # Format the report nicely
                formatted_report = json.dumps(infer_report, indent=2)
                return True, formatted_report
            else:
                return False, "Infer ran but didn't produce a report"
                
        except subprocess.CalledProcessError as e:
            print(f"Infer analysis failed: {e}")
            return False, str(e)
    else:
        # Use compiler warnings
        try:
            compile_result = subprocess.run(
                ["g++", "-Wall", "-Wextra", "-std=c++11", "-c", code_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return True, compile_result.stderr
        except subprocess.CalledProcessError as e:
            return True, e.stderr  # Still return True as we got warnings

def send_to_llm(code, test_results, analysis_results, api_key=None):
    """
    Send the code and analysis results to an LLM for fixes.
    
    Args:
        code: The source code with bugs
        test_results: Output from the test runs
        analysis_results: Output from static analysis
        api_key: Optional API key for the LLM service
        
    Returns:
        fixed_code: The repaired code from the LLM
    """
    log("Sending to LLM for repair")
    
    # Determine if we have the openai package
    try:
        import openai
        has_openai = True
    except ImportError:
        has_openai = False
        log("OpenAI package not found, using placeholder LLM function")
    
    # Prepare the prompt
    prompt = f"""
You are an expert C++ programmer. Your task is to fix bugs in the following code.

Here is the code with problems:

```cpp
{code}
```

The code has failed the following tests:

```
{test_results}
```

Static analysis has identified these issues:

```
{analysis_results}
```

Please provide a corrected version of the code that:
1. Fixes all memory leaks
2. Prevents null pointer dereferences
3. Adds proper bounds checking
4. Initializes all variables before use
5. Ensures proper resource cleanup in all cases

For each change you make, add a brief comment explaining the issue and your fix.

IMPORTANT: Return ONLY the fixed code without any explanation outside the code.
"""

    # If we have OpenAI, use it
    if has_openai and api_key:
        try:
            openai.api_key = api_key
            
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Or another appropriate model
                messages=[
                    {"role": "system", "content": "You are an expert C++ programmer that fixes bugs in code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            # Extract the code from the response
            fixed_code = response.choices[0].message.content
            
            # Clean up any markdown code blocks
            fixed_code = re.sub(r"```cpp\n", "", fixed_code)
            fixed_code = re.sub(r"```\n?", "", fixed_code)
            
            return fixed_code
        except Exception as e:
            print(f"Error using OpenAI API: {e}")
            print("Falling back to placeholder LLM function")
    
    # Placeholder for actual LLM API call
    # In a real implementation, this would call an LLM API
    print("\n==== LLM would receive this prompt: ====")
    print(prompt)
    print("========================================\n")
    
    print("Since no real LLM is configured, we'll apply some basic fixes as a demonstration.")
    
    # Apply some simple fixes to the code as a demonstration
    fixed_code = code
    
    # Fix 1: Initialize buffer values
    fixed_code = fixed_code.replace(
        "buffer = new int[buffer_size];",
        "buffer = new int[buffer_size];\n        // Initialize buffer values\n        for (int i = 0; i < buffer_size; i++) {\n            buffer[i] = 0;\n        }"
    )
    
    # Fix 2: Add bounds check to processBuffer
    fixed_code = fixed_code.replace(
        "if (index >= 0) {",
        "if (index >= 0 && index < buffer_size) {"
    )
    
    # Fix 3: Fix loop bounds in sumBuffer
    fixed_code = fixed_code.replace(
        "for (int i = 0; i <= buffer_size; i++) {",
        "for (int i = 0; i < buffer_size; i++) {"
    )
    
    # Fix 4: Initialize default_value in getFloat
    fixed_code = fixed_code.replace(
        "float default_value;",
        "float default_value = 0.0f;"
    )
    
    # Fix 5: Add null check in processData
    fixed_code = fixed_code.replace(
        "void processData(int* data, int size) {",
        "void processData(int* data, int size) {\n    // Add null check\n    if (data == nullptr) {\n        throw std::invalid_argument(\"Data pointer is null\");\n    }"
    )
    
    return fixed_code

def main():
    global DEBUG
    
    parser = argparse.ArgumentParser(description="LLM-Assisted Code Repair")
    parser.add_argument("--code", required=True, help="Path to the buggy code file")
    parser.add_argument("--test", required=True, help="Path to the test file")
    parser.add_argument("--correct", help="Path to the correct code file (for validation)")
    parser.add_argument("--output", help="Path to save the repaired code")
    parser.add_argument("--api-key", help="API key for the LLM service")
    parser.add_argument("--skip-infer", action="store_true", help="Skip running Infer static analysis")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    args = parser.parse_args()
    
    if args.debug:
        DEBUG = True
    
    # Check if files exist
    if not os.path.exists(args.code):
        print(f"Error: Code file {args.code} not found")
        return 1
    
    if not os.path.exists(args.test):
        print(f"Error: Test file {args.test} not found")
        return 1
    
    if args.correct and not os.path.exists(args.correct):
        print(f"Error: Correct code file {args.correct} not found")
        return 1
    
    # Determine output path
    output_path = args.output
    if not output_path:
        code_basename = os.path.basename(args.code)
        output_path = f"{os.path.splitext(code_basename)[0]}_fixed.cpp"
    
    # Step 1: Ensure correct code passes tests if provided
    if args.correct:
        print(f"Validating correct code: {args.correct}")
        correct_success, correct_output = compile_and_run_tests(args.correct, args.test, is_correct=True)
        if not correct_success:
            print("ERROR: The 'correct' code does not pass all tests!")
            print(correct_output)
            return 1
        print("Correct code passes all tests.")
    
    # Step 2: Run tests on the buggy code
    print(f"Testing buggy code: {args.code}")
    buggy_success, buggy_output = compile_and_run_tests(args.code, args.test)
    
    if buggy_success:
        print("All tests passed on the buggy code! No repair needed.")
        return 0
    
    print("Tests failed on buggy code as expected.")
    
    # Step 3: Run static analysis if not skipped
    analysis_output = "Static analysis skipped."
    if not args.skip_infer:
        print("Running static analysis...")
        analysis_success, analysis_output = run_static_analysis(args.code)
        if not analysis_success:
            print("WARNING: Static analysis had issues, but continuing with repair process")
    else:
        print("Static analysis skipped as requested.")
    
    # Step 4: Read the code file
    with open(args.code, "r") as f:
        code_content = f.read()
    
    # Step 5: Send to LLM for repair
    print("Sending to LLM for code repair...")
    fixed_code = send_to_llm(code_content, buggy_output, analysis_output, args.api_key)
    
    # Step 6: Save the repaired code
    with open(output_path, "w") as f:
        f.write(fixed_code)
    
    print(f"Repaired code saved to {output_path}")
    
    # Step 7: Test the repaired code
    print("Testing repaired code...")
    fixed_success, fixed_output = compile_and_run_tests(output_path, args.test)
    
    if fixed_success:
        print("SUCCESS: All tests pass on the repaired code!")
        return 0
    else:
        print("FAILURE: The repaired code still has issues.")
        print(fixed_output)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 