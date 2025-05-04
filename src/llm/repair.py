import os
import argparse
import time
import logging
import difflib
import json
import re
from pathlib import Path
from typing import Dict, Optional, List, Set

from src.llm import logger
from .infer_report_processor import process_infer_report
from .llm import get_code_from_result, request_llm

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

def repair_file(file_path: str, modified_content: Dict, failed_tests: Optional[List[str]] = None) -> Optional[str]:
    """
    Use LLM to repair a file based on the Infer issues and failed tests.
    
    Args:
        file_path: Path to the file to repair
        modified_content: Content of the file with Infer issue comments
        failed_tests: List of failed test names
        
    Returns:
        Fixed content if successful, None otherwise
    """
    language = "C++"
    
    # Extract bug types from the modified content
    bug_types = modified_content['lintList']
    
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
    if failed_tests:
        failed_tests_section = f"""
Failed Tests:
{chr(10).join(failed_tests)}

Please ensure your fixes address these test failures while maintaining the original functionality.
"""
    
    prompt = f"""
As a senior code quality engineer, carefully inspect the following code file with Infer static analysis warnings. 
Each warning is marked with an end-of-line comment containing '//[INFER_WARNING] <bug_type_hum>:<Mqualifier>'.

Requirements:
1. Resolve all warnings while strictly preserving original functionality
2. Maintain existing code style and formatting
3. Prioritize safe fixes that prevent potential runtime errors
4. Use minimal code changes to address each issue
5. Validate solutions against the original code's intent
6. You should only fix marked warnings, do not change other parts of the code
7. Ensure fixes address any failed tests

{custom_prompts_section}
{failed_tests_section}

Language: {language}  # Added context for language-specific fixes

# File content with warnings
```cpp
{modified_content['content']}
```

**Important:**
- Only output the complete fixed code
- Never add explanations or comments
- Keep original comments unless they reference warnings
- Ensure exact syntax validation for {language}
"""
    
    # Request fix from LLM
    logger.info(f"Requesting LLM to fix issues in {file_path}")
    fixed_content = request_llm(prompt)
    
    if not fixed_content:
        logger.error(f"Failed to get repair suggestions for {file_path}")
        return None
    
    fixed_content = get_code_from_result(fixed_content)
        
    return fixed_content

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

def repair_files(modified_files: Dict[str, str], output_dir: Optional[str] = None, failed_tests_path: Optional[str] = None) -> Dict[str, str]:
    """
    Repair all files with Infer issues using LLM.
    
    Args:
        modified_files: Dictionary mapping file paths to content with Infer comments
        output_dir: Directory to write fixed files to (if None, overwrite original)
        failed_tests_path: Path to file containing failed test names
        
    Returns:
        Dictionary mapping file paths to fixed content
    """
    # Load failed tests if provided
    failed_tests = None
    if failed_tests_path and os.path.exists(failed_tests_path):
        with open(failed_tests_path, 'r') as f:
            failed_tests = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(failed_tests)} failed tests from {failed_tests_path}")
    
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
        
        fixed_content = repair_file(file_path, modified_content, failed_tests)
        
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
    parser.add_argument('report_path', help='Path to Infer report.json file')
    parser.add_argument('--output-dir', help='Directory to write fixed files to (if not provided, will overwrite original files)')
    parser.add_argument('--failed-tests', help='Path to file containing failed test names')
    
    args = parser.parse_args()
    
    total_start_time = time.time()
    
    # Process Infer report
    logger.info(f"Processing Infer report: {args.report_path}")
    process_start_time = time.time()
    modified_files = process_infer_report(args.report_path)
    process_time = time.time() - process_start_time
    
    if not modified_files:
        logger.info(f"No issues found to repair (processing took {process_time:.2f}s)")
        return
    
    logger.info(f"Found {len(modified_files)} files with issues (processing took {process_time:.2f}s)")
    
    # Repair files with issues
    repair_start_time = time.time()
    fixed_files = repair_files(modified_files, args.output_dir, args.failed_tests)
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