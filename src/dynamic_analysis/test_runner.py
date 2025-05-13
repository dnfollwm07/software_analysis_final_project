"""
Test runner module for dynamic analysis.

This module provides functionality to run tests against code to identify issues
and validate repairs.
"""
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import the test generator for dynamic test creation
from src.dynamic_analysis.test_generator import generate_tests


def run_tests(target_file: str) -> Dict[str, Any]:
    """
    Run tests for a target file and return the results.
    
    Args:
        target_file: Path to the file to test
        
    Returns:
        Dictionary containing test results
    """
    file_path = Path(target_file)
    if not file_path.exists():
        raise FileNotFoundError(f"Target file not found: {target_file}")
        
    file_extension = file_path.suffix.lower()
    
    # Determine the appropriate test runner based on file extension
    if file_extension in ['.cpp', '.cc', '.c', '.h', '.hpp']:
        return run_cpp_tests(target_file)
    elif file_extension in ['.py']:
        return run_python_tests(target_file)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")


def run_cpp_tests(target_file: str) -> Dict[str, Any]:
    """
    Run tests for a C++ file.
    
    Args:
        target_file: Path to the C++ file to test
        
    Returns:
        Dictionary containing test results
    """
    test_results = {
        "file_path": target_file,
        "language": "cpp",
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_details": []
    }
    
    # Find or generate test files for the target
    test_files = _find_cpp_test_files(target_file)
    
    if not test_files:
        # If no tests exist, attempt to generate them
        test_files = generate_tests(target_file)
        
    if not test_files:
        print(f"Warning: No tests found or generated for {target_file}")
        return test_results
        
    # Compile and run each test
    for test_file in test_files:
        # Build the test executable
        build_dir = Path("build") / Path(test_file).stem
        build_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate a unique executable name
        executable = build_dir / "test_executable"
        if os.name == "nt":  # Windows
            executable = executable.with_suffix(".exe")
            
        # Build command
        build_cmd = ["g++", "-std=c++17", "-o", str(executable), test_file, "-I", "."]
        
        # Add the target file unless it's already included in the test
        if not _file_includes_other(test_file, target_file):
            build_cmd.extend([target_file])
            
        try:
            # Compile the test
            build_result = subprocess.run(
                build_cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if build_result.returncode != 0:
                # Compilation failed
                test_results["test_details"].append({
                    "test_file": test_file,
                    "status": "build_failed",
                    "output": build_result.stderr,
                    "error_message": "Failed to compile test"
                })
                test_results["failed_tests"] += 1
                continue
                
            # Run the test
            run_result = subprocess.run(
                [str(executable)],
                capture_output=True,
                text=True,
                check=False
            )
            
            # Process test results
            test_status = "passed" if run_result.returncode == 0 else "failed"
            test_output = run_result.stdout if run_result.returncode == 0 else run_result.stderr
            
            test_results["test_details"].append({
                "test_file": test_file,
                "status": test_status,
                "output": test_output
            })
            
            if test_status == "passed":
                test_results["passed_tests"] += 1
            else:
                test_results["failed_tests"] += 1
                
        except Exception as e:
            test_results["test_details"].append({
                "test_file": test_file,
                "status": "error",
                "output": str(e),
                "error_message": "Error running test"
            })
            test_results["failed_tests"] += 1
            
    test_results["total_tests"] = test_results["passed_tests"] + test_results["failed_tests"]
    
    return test_results


def run_python_tests(target_file: str) -> Dict[str, Any]:
    """
    Run tests for a Python file.
    
    Args:
        target_file: Path to the Python file to test
        
    Returns:
        Dictionary containing test results
    """
    test_results = {
        "file_path": target_file,
        "language": "python",
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_details": []
    }
    
    # Find or generate test files for the target
    test_files = _find_python_test_files(target_file)
    
    if not test_files:
        # If no tests exist, attempt to generate them
        test_files = generate_tests(target_file)
        
    if not test_files:
        print(f"Warning: No tests found or generated for {target_file}")
        return test_results
        
    # Run each test using pytest
    for test_file in test_files:
        try:
            result = subprocess.run(
                ["pytest", test_file, "-v"],
                capture_output=True,
                text=True,
                check=False
            )
            
            # Parse pytest output to get test results
            output = result.stdout
            
            # Simple parsing of pytest output
            # In a real implementation, you might want to use pytest's JSON output
            passed_count = output.count("PASSED")
            failed_count = output.count("FAILED")
            
            test_status = "passed" if result.returncode == 0 else "failed"
            
            test_results["test_details"].append({
                "test_file": test_file,
                "status": test_status,
                "output": output,
                "passed_count": passed_count,
                "failed_count": failed_count
            })
            
            test_results["passed_tests"] += passed_count
            test_results["failed_tests"] += failed_count
            
        except Exception as e:
            test_results["test_details"].append({
                "test_file": test_file,
                "status": "error",
                "output": str(e),
                "error_message": "Error running test"
            })
            test_results["failed_tests"] += 1
            
    test_results["total_tests"] = test_results["passed_tests"] + test_results["failed_tests"]
    
    return test_results


def _find_cpp_test_files(target_file: str) -> List[str]:
    """
    Find test files for a C++ source file.
    
    Args:
        target_file: Path to the C++ file
        
    Returns:
        List of test file paths
    """
    target_path = Path(target_file)
    base_name = target_path.stem
    
    test_files = []
    
    # Check common test file naming patterns
    test_dirs = [
        "tests",
        "test",
        target_path.parent / "tests",
        target_path.parent / "test"
    ]
    
    test_patterns = [
        f"test_{base_name}.cpp",
        f"{base_name}_test.cpp",
        f"Test{base_name}.cpp",
        f"{base_name}Test.cpp"
    ]
    
    # Look for test files in test directories
    for test_dir in test_dirs:
        test_dir_path = Path(test_dir)
        if test_dir_path.exists() and test_dir_path.is_dir():
            for pattern in test_patterns:
                potential_test = test_dir_path / pattern
                if potential_test.exists():
                    test_files.append(str(potential_test))
    
    return test_files


def _find_python_test_files(target_file: str) -> List[str]:
    """
    Find test files for a Python source file.
    
    Args:
        target_file: Path to the Python file
        
    Returns:
        List of test file paths
    """
    target_path = Path(target_file)
    base_name = target_path.stem
    
    test_files = []
    
    # Check common test file naming patterns
    test_dirs = [
        "tests",
        "test",
        target_path.parent / "tests",
        target_path.parent / "test"
    ]
    
    test_patterns = [
        f"test_{base_name}.py",
        f"{base_name}_test.py",
        f"test{base_name}.py",
        f"{base_name}Test.py"
    ]
    
    # Look for test files in test directories
    for test_dir in test_dirs:
        test_dir_path = Path(test_dir)
        if test_dir_path.exists() and test_dir_path.is_dir():
            for pattern in test_patterns:
                potential_test = test_dir_path / pattern
                if potential_test.exists():
                    test_files.append(str(potential_test))
    
    return test_files


def _file_includes_other(file_path: str, target_file: str) -> bool:
    """
    Check if one file includes or imports another.
    
    Args:
        file_path: Path to the file to check
        target_file: Path of the file to look for
        
    Returns:
        True if file_path includes target_file, False otherwise
    """
    target_filename = Path(target_file).name
    
    with open(file_path, 'r') as f:
        content = f.read()
        
    # Simple check for inclusion/import
    # In a real implementation, this would be more sophisticated
    if f'#include "{target_filename}"' in content or f"#include <{target_filename}>" in content:
        return True
        
    target_module = Path(target_file).stem
    if f"import {target_module}" in content or f"from {target_module} import" in content:
        return True
        
    return False 