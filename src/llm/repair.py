import os
import argparse
import time
import logging
import difflib
import json
import re
from pathlib import Path
from typing import Dict, Optional, List, Set, Tuple
import subprocess

from .test_results_parser import TestResultsParser
from .logger import logger
from .infer_report_processor import process_infer_report
from .llm import get_code_from_result, request_llm

NO_REQUEST_LLM = os.getenv("NO_REQUEST_LLM", "0").lower() == "1"
USE_INFER = False

def load_config(config_path: str = "config.json") -> Dict:
    """
    Load configuration from JSON file
    
    Args:
        config_path: Path to the config JSON file
        
    Returns:
        Dictionary containing the configuration
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.warning(f"Failed to load configuration from {config_path}: {e}")
        return {"rules": []}

def repair_file(file_path: str, modified_content: Dict) -> Optional[str]:
    """
    Use LLM to repair a file based on the Infer issues and failed tests.
    
    Args:
        file_path: Path to the file to repair
        modified_content: Content of the file with Infer issue comments
        
    Returns:
        Fixed content if successful, None otherwise
    """
    language = "C++"
    
    # Extract bug types from the modified content
    bug_types = modified_content.get('lintList', [])
    
    # Load custom fix prompts from config
    config_rules = load_config().get("rules", [])
    custom_fix_prompts = ""
    
    # Match bug types with configured lintTypes and collect fix prompts
    for bug_type in bug_types:
        bug_type_hum = bug_type['bug_type_hum']
        for rule in config_rules:
            if rule.get("lintType") == bug_type_hum:
                custom_fix_prompts += f"- For '{bug_type_hum}' issues: {rule.get('fixPrompt')}\n"
    logger.info(f"Custom fix prompts:\n{custom_fix_prompts}")
    
    # Add custom fix prompts to the main prompt if any were found
    custom_prompts_section = ""
    if custom_fix_prompts:
        custom_prompts_section = "Custom fix guidelines:\n" + custom_fix_prompts + "\n\n"
    
    # Add failed tests information if available
    failed_tests_section = ""
    if len(modified_content.get('failed_tests', [])) > 0:
        filtered_output_str = "\n".join([f"- {test['name']}\n{test['filtered_output']}\n" for test in modified_content['failed_tests']])
        failed_tests_section = f"""
Failed Tests:
{filtered_output_str}

Please ensure your fixes address these test failures while maintaining the original functionality.
"""
    
    # Add Infer warnings section if there are any warnings
    infer_warnings_section = "" if bug_types else "Each warning is marked with an end-of-line comment containing '//[INFER_WARNING] <bug_type_hum>:<Mqualifier>'."
    summary_section = "" if modified_content.get('summary') is None else f"Infer warnings summary:\n{modified_content['summary']}"
    code = modified_content['content']

    prompt = f"""
As a senior code quality engineer, carefully inspect the following code file.{infer_warnings_section}

Requirements:
1. Resolve all issues while strictly preserving original functionality
2. Maintain existing code style and formatting
3. Prioritize safe fixes that prevent potential runtime errors
4. Use minimal code changes to address each issue
5. Validate solutions against the original code's intent
6. You should only fix marked warnings, do not change other parts of the code
7. Ensure fixes address any failed tests

{custom_prompts_section}
{failed_tests_section}

Language: {language}

# File content with warnings
```cpp
{code}
```

{summary_section}

**Important:**
- Only output the complete fixed code
- Never add explanations or comments
- Keep original comments unless they reference warnings
- Ensure exact syntax validation for {language}
"""
    if os.getenv("USE_DEBUG_MODE", "false") == "true":
        new_path = file_path.replace("run-examples", "debug/test-infer" if USE_INFER else "debug/test")
        if os.path.exists(new_path):
            with open(new_path, "r") as f:
                return f.read()

    if NO_REQUEST_LLM:
        logger.info(f"Skipping LLM request for {file_path}, because NO_REQUEST_LLM is set to 1")
        return modified_content['content']
        
    
    # Request fix from LLM
    logger.info(f"Requesting LLM to fix issues in {file_path}")
    fixed_content = request_llm(prompt)
    
    if not fixed_content:
        logger.error(f"Failed to get repair suggestions for {file_path}")
        return None
    
    fixed_content = get_code_from_result(fixed_content)

    is_fixed, code = fix_cpp_syntax_with_llm(fixed_content)
    if not is_fixed or not code:
        logger.error(f"Failed to fix syntax errors for {file_path}")
        return modified_content['content']
        
    return code


def fix_cpp_syntax_with_llm(cpp_code: str, max_retry_times: int = 3, retry_times: int = 0)->Tuple[bool, str]:
    """
    Fix C++ syntax errors using g++ compiler.
    
    Args:
        cpp_code: C++ source code as string
    """
    if retry_times >= max_retry_times:
        return False, cpp_code

    error_msg = check_cpp_syntax(cpp_code)
    if error_msg:
        logger.info(f"Fixing syntax errors with LLM, retry times: {retry_times + 1}, error message: {error_msg}")
        prompt = f"""Act as a C++ expert to fix syntax errors by:
1. Analyzing compilation error messages
2. Locating exact problematic code lines
3. Applying minimal necessary corrections
4. Preserving original code logic

Input code:
```cpp
{cpp_code}
```

Compiler errors:
{error_msg}

Output only:Corrected working code"""
        fixed_code = get_code_from_result(request_llm(prompt))
        if not fixed_code:
            return False, cpp_code
        return fix_cpp_syntax_with_llm(fixed_code, max_retry_times, retry_times + 1)
    else:
        return True, cpp_code



def check_cpp_syntax(cpp_code: str)->str:
    """
    Check if C++ code string has valid syntax using g++ compiler.
    
    Args:
        cpp_code: C++ source code as string
        
    """
    result = subprocess.run(
        ["g++", "-fsyntax-only", "-x", "c++", "-I./run-examples/src", "-"],
        input=cpp_code.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode == 0:
        return ""
    else:
        return result.stderr.decode()


def print_colored_diff(diff_content: str, file_path: str) -> None:
    """
    Print a colored diff to the log.
    
    Args:
        diff_content: The diff content as a string
        file_path: Path to the file being diffed
    """
    if not diff_content:
        logger.warning(f"No significant changes detected for {file_path}")
        return
        
    logger.info(f"Changes for {file_path}:")
    new_result = ""
    for line in diff_content.splitlines():
        if line.startswith('+'):
            new_result += f"\033[32m{line}\033[0m"  # Green for additions
        elif line.startswith('-'):
            new_result += f"\033[31m{line}\033[0m"  # Red for deletions
        elif line.startswith('^'):
            new_result += f"\033[36m{line}\033[0m"  # Cyan for change markers
        elif line.startswith('@@'):
            new_result += f"\033[35m{line}\033[0m"  # Magenta for chunk headers
        else:
            new_result += line
        new_result += "\n"
    logger.info("\n" + new_result)

def repair_files(modified_files: Dict[str, str], output_dir: Optional[str] = None) -> Dict[str, str]:
    """
    Repair all files with Infer issues using LLM.
    
    Args:
        modified_files: Dictionary mapping file paths to content with Infer comments
        output_dir: Directory to write fixed files to (if None, overwrite original)
        
    Returns:
        Dictionary mapping file paths to fixed content
    """
    # Load failed tests if provided
    
    fixed_files = {}
    total_files = len(modified_files)
    
    logger.info(f"Starting repair of {total_files} files")
    
    for idx, (file_path, modified_content) in enumerate(modified_files.items(), 1):
        start_time = time.time()
        logger.info(f"[{idx}/{total_files}] Repairing {file_path}...")
        
        # Read original content (without INFER_WARNING comments)
        original_content = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            logger.warning(f"Could not read original file for diff: {e}")
        
        fixed_content = repair_file(file_path, modified_content)
        
        repair_time = time.time() - start_time
        
        if fixed_content:
            fixed_files[file_path] = fixed_content
            
            # Generate and log diff between original and fixed content
            if original_content:
                try:
                    diff = generate_diff(file_path, original_content, fixed_content)
                    print_colored_diff(diff, file_path)
                except Exception as e:
                    logger.error(f"Error generating diff: {e}")
            
            # Write fixed content
            if output_dir:
                # Create output directory with same structure as original
                rel_path = os.path.relpath(file_path, os.getcwd())
                output_path = os.path.join(output_dir, rel_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                logger.info(f"[{idx}/{total_files}] Fixed file written to {output_path} (took {repair_time:.2f}s)")
            else:
                # Overwrite original file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                logger.info(f"[{idx}/{total_files}] Original file {file_path} overwritten with fixes (took {repair_time:.2f}s)")
        else:
            logger.warning(f"[{idx}/{total_files}] Failed to repair {file_path} (took {repair_time:.2f}s)")
    
    return fixed_files

def generate_diff(file_path: str, original_content: str, fixed_content: str) -> str:
    """
    Generate a unified diff between original and fixed content.
    
    Args:
        file_path: Path to the file
        original_content: Original file content
        fixed_content: Fixed file content
        
    Returns:
        String containing the unified diff
    """
    original_lines = original_content.splitlines(keepends=True)
    fixed_lines = fixed_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines, fixed_lines, 
        fromfile=f"{file_path} (original)",
        tofile=f"{file_path} (fixed)",
        n=3  # Context lines
    )
    
    return ''.join(diff)

def main():
    parser = argparse.ArgumentParser(description='Repair code based on Infer report')
    parser.add_argument('--infer-report-path', help='Path to Infer report.json file (optional if not using Infer)')
    parser.add_argument('--output-dir', help='Directory to write fixed files to (if not provided, will overwrite original files)')
    parser.add_argument('--failed-tests', help='Path to file containing failed test names')
    parser.add_argument('--use-infer', action='store_true', help='Whether to use Infer results in the repair process')
    parser.add_argument('--include-infer-in-prompt', action='store_true', help='Whether to include Infer results in the prompt')
    
    args = parser.parse_args()
    
    global USE_INFER
    USE_INFER = args.use_infer
    
    target_test_map = {}

    src_dir = "run-examples/src"
    cpp_files = []
    try:
        for file in os.listdir(src_dir):
            if file.endswith(".cpp"):
                cpp_path = os.path.join(src_dir, file)
                # Convert to relative path
                rel_path = os.path.relpath(cpp_path)
                cpp_files.append(rel_path)
        logger.info(f"Found {len(cpp_files)} .cpp files in {src_dir}")
    except Exception as e:
        logger.error(f"Error reading directory {src_dir}: {e}")
        return
    
    # Map each cpp file to its test class name
    for cpp_file in cpp_files:
        base_name = os.path.splitext(os.path.basename(cpp_file))[0]
        # Convert snake_case to PascalCase and append "Test"
        test_class = ''.join(word.title() for word in base_name.split('_')) + 'Test'
        target_test_map[cpp_file] = test_class

    
    logger.info(f"Target test map: {target_test_map}")
    
    total_start_time = time.time()
    
    # Process files based on whether we're using Infer
    modified_files = {}
    process_time = 0

    test_results_parser = TestResultsParser(args.failed_tests)
    
    # handle Test
    for file_path, test_class in target_test_map.items():
        failed_tests = test_results_parser.get_failed_test_info_by_test_class(test_class)
        if not failed_tests or len(failed_tests) == 0:
            logger.info(f"No failed tests found for {test_class}")
            continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Could not read file {file_path}: {e}")
            raise Exception(f"Could not read file {file_path}: {e}")
        
        modified_files[file_path] = {
            'content': content,
            'lintList': [],
            'testClass': test_class,
            'failed_tests': test_results_parser.get_failed_test_info_by_test_class(test_class)
        }
    
    if args.use_infer and args.include_infer_in_prompt:
        if not args.infer_report_path:
            logger.error("infer_report_path is required when using Infer and including it in the prompt")
            return
            
        # Process Infer report
        logger.info(f"Processing Infer report: {args.infer_report_path}")
        process_start_time = time.time()
        infer_modified_files = process_infer_report(args.infer_report_path)
        process_time = time.time() - process_start_time
        
        if not infer_modified_files:
            logger.info(f"No issues found to repair (processing took {process_time:.2f}s)")
        else:
            for file_path, modified_content in infer_modified_files.items():
                if file_path in modified_files:
                    modified_files[file_path]['content'] = modified_content['content']
                    modified_files[file_path]['lintList'] = modified_content['lintList']
                else:
                    modified_files[file_path] = {
                        'content': modified_content['content'],
                        'lintList': modified_content['lintList'],
                        'testClass': '',
                        'failed_tests': [],
                        'summary': modified_content['summary']
                    }
            logger.info(f"Found {len(infer_modified_files)} files with issues (processing took {process_time:.2f}s)")
            logger.debug(f"Modified files: {modified_files}")
    # Repair files with issues
    repair_start_time = time.time()
    fixed_files = repair_files(modified_files, args.output_dir)
    repair_time = time.time() - repair_start_time
    
    # Print summary
    total_time = time.time() - total_start_time
    logger.info(f"Total repair time: {total_time:.2f}s (processing: {process_time:.2f}s, repair: {repair_time:.2f}s)")
    
    if fixed_files:
        logger.info("Successfully repaired files:")
        for file_path in fixed_files:
            logger.info(f"  - {file_path}")

if __name__ == "__main__":
    main()