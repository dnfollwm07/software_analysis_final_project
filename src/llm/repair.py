#!/usr/bin/env python
"""
Command-line interface for LLM-based code repair.

This module provides a CLI for repairing code using LLM suggestions
based on static analysis results and test outcomes.
"""
import argparse
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

from src.llm.code_repair import CodeRepairPrompt, CodeRepairManager
from src.static_analysis.analyzer import get_static_analysis_results
from src.dynamic_analysis.test_runner import run_tests


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LLM-based code repair tool")
    parser.add_argument(
        "--target", 
        type=str, 
        required=True, 
        help="Path to the target file to repair"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        help="Path to save the repaired code (defaults to overwriting target)"
    )
    parser.add_argument(
        "--no-tests", 
        action="store_true", 
        help="Skip running tests on the repaired code"
    )
    parser.add_argument(
        "--api-key", 
        type=str, 
        help="LLM API key (defaults to environment variable LLM_API_KEY)"
    )
    parser.add_argument(
        "--template-dir", 
        type=str, 
        default="config/prompt_templates",
        help="Directory containing prompt templates"
    )
    return parser.parse_args()


def get_llm_api_key(provided_key: Optional[str] = None) -> str:
    """Get LLM API key from arguments or environment variables."""
    if provided_key:
        return provided_key
        
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        print("Error: LLM API key not provided and LLM_API_KEY environment variable not set")
        sys.exit(1)
    return api_key


def save_repaired_code(repaired_code: str, target_file: str, output_file: Optional[str] = None) -> str:
    """
    Save the repaired code to a file.
    
    Args:
        repaired_code: The repaired code content
        target_file: Original file path
        output_file: Optional output file path (defaults to target_file)
        
    Returns:
        Path to the file where the repaired code was saved
    """
    save_path = output_file if output_file else target_file
    with open(save_path, 'w') as f:
        f.write(repaired_code)
    print(f"Repaired code saved to: {save_path}")
    return save_path


def main():
    """Main function for the code repair CLI."""
    args = parse_arguments()
    
    # Validate target file
    target_file = Path(args.target)
    if not target_file.exists():
        print(f"Error: Target file '{args.target}' does not exist")
        sys.exit(1)
    
    # Get LLM API key
    api_key = get_llm_api_key(args.api_key)
    
    # Initialize repair components
    prompt_generator = CodeRepairPrompt(template_dir=args.template_dir)
    repair_manager = CodeRepairManager(llm_api_key=api_key, prompt_generator=prompt_generator)
    
    # Get static analysis results
    try:
        print(f"Running static analysis on {target_file}...")
        error_info = get_static_analysis_results(str(target_file))
        
        if not error_info:
            print("No errors found by static analysis. No repair needed.")
            sys.exit(0)
            
    except Exception as e:
        print(f"Error during static analysis: {str(e)}")
        sys.exit(1)
    
    # Run tests if not skipped
    test_results = None
    if not args.no_tests:
        try:
            print("Running tests before repair...")
            test_results = run_tests(str(target_file))
        except Exception as e:
            print(f"Warning: Error running tests: {str(e)}")
    
    # Perform code repair
    try:
        print("Generating code repair using LLM...")
        repaired_code, confidence = repair_manager.repair_code(
            str(target_file), 
            error_info,
            test_results
        )
        
        print(f"Repair generated with confidence score: {confidence:.2f}")
        
        # Save repaired code
        output_file = args.output if args.output else str(target_file)
        save_repaired_code(repaired_code, str(target_file), output_file)
        
        # Run tests on repaired code if not skipped
        if not args.no_tests:
            print("Running tests on repaired code...")
            post_repair_results = run_tests(output_file)
            
            if post_repair_results.get("passed_tests", 0) > test_results.get("passed_tests", 0):
                print("✅ Repair improved test results!")
            else:
                print("⚠️ Repair did not improve test results.")
                
            quality_score = repair_manager.evaluate_repair(repaired_code, post_repair_results)
            print(f"Repair quality score: {quality_score:.2f}")
            
    except Exception as e:
        print(f"Error during code repair: {str(e)}")
        sys.exit(1)
        
    print("Code repair completed successfully.")


if __name__ == "__main__":
    main() 