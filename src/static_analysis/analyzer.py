"""
Static analysis module for code analysis.

This module handles running static analysis tools and processing their results.
"""
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.static_analysis.infer_integration import run_infer_analysis


def get_static_analysis_results(target_file: str) -> Dict[str, Any]:
    """
    Get static analysis results for a target file.
    
    Args:
        target_file: Path to the file to analyze
        
    Returns:
        Dictionary containing error information from static analysis
    """
    file_path = Path(target_file)
    if not file_path.exists():
        raise FileNotFoundError(f"Target file not found: {target_file}")
        
    file_extension = file_path.suffix.lower()
    
    # Determine the appropriate analyzer based on file extension
    if file_extension in ['.cpp', '.cc', '.c', '.h', '.hpp']:
        return analyze_cpp_file(target_file)
    elif file_extension in ['.py']:
        return analyze_python_file(target_file)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")


def analyze_cpp_file(target_file: str) -> Dict[str, Any]:
    """
    Analyze a C++ file using Infer and other static analysis tools.
    
    Args:
        target_file: Path to the C++ file to analyze
        
    Returns:
        Dictionary containing error information
    """
    # Use Infer for C++ analysis
    infer_results = run_infer_analysis(target_file)
    
    # Process and categorize the results
    processed_results = {
        "file_path": target_file,
        "language": "cpp",
        "errors": [],
        "warnings": [],
        "total_issues": 0
    }
    
    if infer_results:
        for issue in infer_results:
            issue_type = issue.get("bug_type", "unknown")
            severity = issue.get("severity", "").lower()
            
            issue_info = {
                "type": issue_type,
                "severity": severity,
                "line": issue.get("line", 0),
                "column": issue.get("column", 0),
                "description": issue.get("qualifier", ""),
                "suggestion": _generate_suggestion(issue_type, issue.get("qualifier", ""))
            }
            
            if severity == "error":
                processed_results["errors"].append(issue_info)
            else:
                processed_results["warnings"].append(issue_info)
                
        processed_results["total_issues"] = len(processed_results["errors"]) + len(processed_results["warnings"])
        
    return processed_results


def analyze_python_file(target_file: str) -> Dict[str, Any]:
    """
    Analyze a Python file using static analysis tools.
    
    Args:
        target_file: Path to the Python file to analyze
        
    Returns:
        Dictionary containing error information
    """
    # Run pylint for Python analysis
    result = _run_pylint(target_file)
    
    processed_results = {
        "file_path": target_file,
        "language": "python",
        "errors": [],
        "warnings": [],
        "total_issues": 0
    }
    
    if result:
        for issue in result:
            severity = "error" if issue["type"] in ["E", "F"] else "warning"
            
            issue_info = {
                "type": issue["message-id"],
                "severity": severity,
                "line": issue["line"],
                "column": issue["column"],
                "description": issue["message"],
                "suggestion": _generate_suggestion(issue["message-id"], issue["message"])
            }
            
            if severity == "error":
                processed_results["errors"].append(issue_info)
            else:
                processed_results["warnings"].append(issue_info)
                
        processed_results["total_issues"] = len(processed_results["errors"]) + len(processed_results["warnings"])
        
    return processed_results


def _run_pylint(target_file: str) -> List[Dict[str, Any]]:
    """
    Run pylint on a Python file and return the results.
    
    Args:
        target_file: Path to the Python file to analyze
        
    Returns:
        List of issues found by pylint
    """
    try:
        # Run pylint with JSON output format
        result = subprocess.run(
            ["pylint", "--output-format=json", target_file],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"Error running pylint: {str(e)}")
        return []


def _generate_suggestion(issue_type: str, description: str) -> str:
    """
    Generate a suggestion for fixing an issue based on its type and description.
    
    Args:
        issue_type: Type of the issue
        description: Description of the issue
        
    Returns:
        Suggestion for fixing the issue
    """
    # Common suggestions for different issue types
    # In a real implementation, this would be more comprehensive
    if "null pointer" in issue_type.lower() or "null pointer" in description.lower():
        return "Check for null pointers before dereferencing"
    elif "buffer overflow" in issue_type.lower() or "buffer overflow" in description.lower():
        return "Ensure proper bounds checking for array accesses"
    elif "memory leak" in issue_type.lower() or "memory leak" in description.lower():
        return "Properly free allocated memory"
    elif "undefined variable" in description.lower():
        return "Define the variable before using it"
    elif "unused variable" in description.lower():
        return "Remove the unused variable or use it"
    
    # Default suggestion
    return "Review the code for the described issue" 