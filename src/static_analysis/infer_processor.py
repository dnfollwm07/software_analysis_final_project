"""
Infer output processor for making static analysis results more LLM-friendly.

This module transforms raw Infer output into structured data that is easier for LLMs
to understand and use for generating code repairs.
"""
import json
import re
import os
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path


class InferOutputProcessor:
    """Class for processing Infer output into LLM-friendly format."""
    
    def __init__(self, infer_results_dir: Optional[str] = "infer-out"):
        """
        Initialize the Infer output processor.
        
        Args:
            infer_results_dir: Path to the Infer results directory
        """
        self.infer_results_dir = Path(infer_results_dir)
        self.raw_results = []
        self.processed_results = []
        self.infer_report_text = ""
        
    def load_results(self) -> bool:
        """
        Load Infer results from the report.json file and also capture text report.
        
        Returns:
            bool: True if results loaded successfully, False otherwise
        """
        report_path = self.infer_results_dir / "report.json"
        
        if not report_path.exists():
            print(f"Infer report not found at {report_path}")
            return False
            
        # Load JSON report
        try:
            with open(report_path, 'r') as f:
                self.raw_results = json.load(f)
                
            # Also capture text output from infer report to get more context
            try:
                result = subprocess.run(
                    ["infer", "report"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                self.infer_report_text = result.stdout
            except Exception as e:
                print(f"Warning: Could not capture infer report text: {str(e)}")
                
            return True
        except Exception as e:
            print(f"Error loading Infer results: {str(e)}")
            return False
    
    def process_results(self) -> List[Dict[str, Any]]:
        """
        Process raw Infer results into LLM-friendly format.
        
        Returns:
            List of processed issue dictionaries
        """
        self.processed_results = []
        
        for result in self.raw_results:
            processed_issue = self._process_single_issue(result)
            if processed_issue:
                self.processed_results.append(processed_issue)
                
        return self.processed_results
    
    def _process_single_issue(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single Infer issue into LLM-friendly format.
        
        Args:
            issue: Raw issue dictionary from Infer
            
        Returns:
            Processed issue dictionary or None if processing failed
        """
        try:
            file_path = issue.get("file", "")
            line_number = issue.get("line", 0)
            
            if not file_path or line_number == 0:
                return None
                
            # Extract issue information
            bug_type = issue.get("bug_type", "UNKNOWN")
            qualifier = issue.get("qualifier", "")
            severity = issue.get("severity", "WARNING")
            
            # Extract column from bug trace or description
            column = issue.get("column", 0)
            if column == 0:
                column = self._estimate_column_from_description(qualifier)
                
            # Extract context code with proper error handling
            context_code = self._extract_code_context(file_path, line_number)
            
            # Extract variables from description
            involved_variables = self._extract_variables(qualifier)
            
            # Extract origin line for null values or other issues
            origin_line = self._extract_origin_line(qualifier)
            
            # Process and enhance the bug trace information
            raw_trace = issue.get("bug_trace", [])
            enhanced_trace = self._enhance_trace(raw_trace, file_path, origin_line, line_number)
            
            # Generate basic analysis info
            possible_cause = self._extract_possible_cause(bug_type, qualifier, origin_line)
            implications = self._extract_implications(bug_type)
            fix_suggestions = self._generate_fix_suggestions(bug_type, qualifier, involved_variables)
            
            # For null dereference issues, check if there's a null comparison
            if bug_type == "NULLPTR_DEREFERENCE":
                # Check if there's a comparison to null in the trace
                for step in raw_trace:
                    if "compared to null" in step.get("description", ""):
                        var_name = involved_variables[0] if involved_variables else "the pointer"
                        # This is an if-else with wrong null check pattern
                        # Add a specific suggestion
                        fix_suggestions.insert(0, f"Move the dereference inside the if ({var_name} != nullptr) block instead of the else block")
                        break
            
            # Create the processed issue
            processed_issue = {
                "issue_id": issue.get("hash", ""),
                "issue_type": bug_type,
                "severity": severity,
                "location": {
                    "file": file_path,
                    "line": line_number,
                    "column": column
                },
                "description": qualifier,
                "context": {
                    "code": context_code,
                    "variables": involved_variables
                },
                "trace": enhanced_trace,
                "analysis": {
                    "possible_cause": possible_cause,
                    "implications": implications,
                    "fix_suggestions": fix_suggestions
                }
            }
            
            return processed_issue
            
        except Exception as e:
            print(f"Error processing issue: {str(e)}")
            return None
    
    def _extract_code_context(self, file_path: str, line_number: int, context_lines: int = 3) -> Dict[str, Any]:
        """
        Extract code context around the issue location.
        
        Args:
            file_path: Path to the file
            line_number: Line number of the issue
            context_lines: Number of lines to extract before and after
            
        Returns:
            Dictionary with code context information
        """
        try:
            # Use absolute path if file_path is relative
            absolute_path = file_path
            if not os.path.isabs(file_path) and not os.path.exists(file_path):
                # Try different base paths for the project
                for base_path in [os.getcwd(), os.path.dirname(os.getcwd())]:
                    potential_path = os.path.join(base_path, file_path)
                    if os.path.exists(potential_path):
                        absolute_path = potential_path
                        break
            
            if not os.path.exists(absolute_path):
                # Try to use grep to find context in the infer report text
                context = self._extract_context_from_report(file_path, line_number)
                if context["target_line"]:
                    return context
                
                return {
                    "full_context": f"Could not find file: {file_path}",
                    "target_line": f"Line {line_number} not accessible",
                    "before": [],
                    "after": []
                }
                
            with open(absolute_path, 'r') as f:
                lines = f.readlines()
                
            start = max(0, line_number - context_lines - 1)
            end = min(len(lines), line_number + context_lines)
            
            target_line = lines[line_number - 1].rstrip() if line_number - 1 < len(lines) else ""
            before_lines = [lines[i].rstrip() for i in range(start, line_number - 1)]
            after_lines = [lines[i].rstrip() for i in range(line_number, end)]
            
            full_context = "".join(lines[start:end])
            
            return {
                "full_context": full_context,
                "target_line": target_line,
                "before": before_lines,
                "after": after_lines,
                "line_range": {
                    "start": start + 1,  # 1-indexed
                    "end": end  # 1-indexed
                }
            }
            
        except Exception as e:
            print(f"Error extracting code context: {str(e)}")
            return {
                "full_context": f"Error reading file: {str(e)}",
                "target_line": f"Line {line_number} not accessible",
                "before": [],
                "after": []
            }
    
    def _enhance_trace(self, bug_trace: List[Dict[str, Any]], file_path: str, 
                       origin_line: Optional[int], target_line: int) -> List[Dict[str, Any]]:
        """
        Enhance trace information with better context.
        
        Args:
            bug_trace: Raw bug trace from Infer
            file_path: Path to the file
            origin_line: Origin line number if available
            target_line: Target line number
            
        Returns:
            Enhanced trace information
        """
        enhanced_trace = []
        
        # If we have an origin line, add it as first step if not present
        if origin_line and not any(step.get("line") == origin_line for step in bug_trace):
            # Try to get context for the origin line
            origin_context = self._extract_code_context(file_path, origin_line, 1)
            origin_code = origin_context.get("target_line", "")
            
            enhanced_trace.append({
                "description": f"Variable is assigned null at line {origin_line}",
                "file": file_path,
                "line": origin_line,
                "column": 0,
                "code_snippet": origin_code
            })
        
        # Process each trace step
        for step in bug_trace:
            # Skip steps without description
            if "description" not in step:
                continue
            
            # Get step info
            step_line = step.get("line", 0)
            step_file = step.get("file", file_path)  # Default to main file if not specified
            step_desc = step.get("description", "")
            
            # Get context for this step if we have line number
            code_snippet = ""
            if step_line > 0:
                try:
                    step_context = self._extract_code_context(step_file, step_line, 0)
                    code_snippet = step_context.get("target_line", "")
                except Exception:
                    pass
            
            # For steps with empty line numbers, try to extract from description
            # e.g., "was compared to null on line 5, column 9"
            if step_line == 0:
                line_match = re.search(r'line (\d+)', step_desc)
                if line_match:
                    step_line = int(line_match.group(1))
                    
                    # Try to get context for this line
                    if step_line > 0:
                        try:
                            step_context = self._extract_code_context(step_file, step_line, 0)
                            code_snippet = step_context.get("target_line", "")
                        except Exception:
                            pass
            
            # For the final step (invalid access), use the target line
            if "invalid access" in step_desc and step_line == 0:
                step_line = target_line
                step_file = file_path
                
                # Get context for the target line
                try:
                    step_context = self._extract_code_context(step_file, step_line, 0)
                    code_snippet = step_context.get("target_line", "")
                except Exception:
                    pass
            
            # Create enhanced step
            enhanced_step = {
                "description": step_desc,
                "file": step_file,
                "line": step_line,
                "column": step.get("column", 0)
            }
            
            # Add code snippet if available
            if code_snippet:
                enhanced_step["code_snippet"] = code_snippet
                
            # Add any additional context from original step
            if "node_tags" in step:
                enhanced_step["tags"] = step["node_tags"]
                
            enhanced_trace.append(enhanced_step)
        
        return enhanced_trace
    
    def _extract_context_from_report(self, file_path: str, line_number: int) -> Dict[str, Any]:
        """
        Extract code context from Infer report text if file cannot be accessed directly.
        
        Args:
            file_path: Path to the file
            line_number: Line number of the issue
            
        Returns:
            Dictionary with context information extracted from the report
        """
        # Try to find code snippets in the report text
        file_base = os.path.basename(file_path)
        pattern = rf"{file_base}:{line_number-3}:{line_number+3}"
        
        # Default empty context
        context = {
            "full_context": "",
            "target_line": "",
            "before": [],
            "after": []
        }
        
        # Look for code snippets in the infer report text
        lines = self.infer_report_text.split('\n')
        in_snippet = False
        snippet_lines = []
        
        for line in lines:
            if f"{file_path}:{line_number}" in line:
                in_snippet = True
                continue
                
            if in_snippet:
                if line.strip() and not line.startswith("Found"):
                    snippet_lines.append(line.strip())
                else:
                    in_snippet = False
                    break
        
        if snippet_lines:
            # Try to identify the target line in the snippet
            target_line = ""
            before_lines = []
            after_lines = []
            found_target = False
            
            for line in snippet_lines:
                # Look for lines that might be the target (they often have a caret pointer)
                if "^" in line or line.strip().endswith(f"{line_number}:"):
                    found_target = True
                    target_line = line
                elif not found_target:
                    before_lines.append(line)
                else:
                    after_lines.append(line)
            
            context = {
                "full_context": "\n".join(snippet_lines),
                "target_line": target_line,
                "before": before_lines,
                "after": after_lines
            }
        
        return context
    
    def _estimate_column_from_description(self, description: str) -> int:
        """
        Estimate column number from issue description.
        
        Args:
            description: Issue description
            
        Returns:
            Estimated column number or 0 if not found
        """
        # Look for patterns like "at column X" or "^ here"
        column_match = re.search(r'at column (\d+)', description)
        if column_match:
            return int(column_match.group(1))
            
        # Look for caret indicators like "x = null; ^ here"
        caret_match = re.search(r'([^\n]+)\n\s*\^', description)
        if caret_match:
            line = caret_match.group(1)
            caret_pos = description.find('^', description.find(line))
            if caret_pos != -1:
                return description.find('^') - description.rfind('\n', 0, caret_pos)
                
        return 0
    
    def _extract_variables(self, description: str) -> List[str]:
        """
        Extract variable names from issue description.
        
        Args:
            description: Issue description
            
        Returns:
            List of variable names
        """
        # First look for variables in backticks
        variables = re.findall(r'`([a-zA-Z_][a-zA-Z0-9_]*)`', description)
        if variables:
            return list(set(variables))
        
        # Also look for patterns like "variable X is null" or "pointer Y may be null"
        var_patterns = [
            r'variable ([a-zA-Z_][a-zA-Z0-9_]*)',
            r'pointer ([a-zA-Z_][a-zA-Z0-9_]*)',
            r'value of ([a-zA-Z_][a-zA-Z0-9_]*)'
        ]
        
        for pattern in var_patterns:
            matches = re.findall(pattern, description)
            variables.extend(matches)
            
        return list(set(variables))  # Remove duplicates
    
    def _extract_origin_line(self, description: str) -> Optional[int]:
        """
        Extract origin line number from description.
        
        Args:
            description: Issue description
            
        Returns:
            Origin line number or None if not found
        """
        # Look for patterns like "originating from line X"
        match = re.search(r'originating from line (\d+)', description)
        if match:
            return int(match.group(1))
        return None
    
    def _extract_trace(self, bug_trace: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract trace information from bug trace.
        
        Args:
            bug_trace: Bug trace from Infer
            
        Returns:
            Processed trace information
        """
        processed_trace = []
        
        for step in bug_trace:
            if "description" not in step:
                continue
                
            processed_step = {
                "description": step.get("description", ""),
                "file": step.get("file", ""),
                "line": step.get("line", 0),
                "column": step.get("column", 0)
            }
            
            # Extract any additional context if present
            if "node_tags" in step:
                processed_step["tags"] = step["node_tags"]
                
            processed_trace.append(processed_step)
            
        return processed_trace
    
    def _extract_possible_cause(self, bug_type: str, description: str, origin_line: Optional[int] = None) -> str:
        """
        Extract possible cause from bug type and description.
        
        Args:
            bug_type: Type of the issue
            description: Issue description
            origin_line: Origin line number if available
            
        Returns:
            String describing the possible cause
        """
        bug_type_lower = bug_type.lower()
        description_lower = description.lower()
        
        # For null pointer dereference
        if "null_dereference" in bug_type_lower or "null pointer dereference" in description_lower:
            if origin_line:
                vars = self._extract_variables(description)
                var_name = vars[0] if vars else "pointer"
                return f"{var_name} is assigned null on line {origin_line} and later dereferenced"
            return "Null pointer is dereferenced without checking"
            
        # For memory leak
        elif "memory_leak" in bug_type_lower:
            return "Allocated memory is not properly freed"
            
        # For buffer overrun
        elif "buffer_overrun" in bug_type_lower or "array bounds" in description_lower:
            return "Array access potentially out of bounds"
            
        # For uninitialized value
        elif "uninitialized_value" in bug_type_lower:
            return "Using uninitialized value in computation"
            
        # For use after free
        elif "use_after_free" in bug_type_lower:
            return "Using memory after it has been freed"
            
        # Try to extract cause from description
        cause_from_desc = re.search(r'(could be|may be|is) ([^\.]+)', description_lower)
        if cause_from_desc:
            return cause_from_desc.group(0)
            
        # Default case
        return "Issue detected in the code"
    
    def _extract_implications(self, bug_type: str) -> List[str]:
        """
        Extract implications of the issue.
        
        Args:
            bug_type: Type of the issue
            
        Returns:
            List of implications
        """
        implications = []
        bug_type_lower = bug_type.lower()
        
        if bug_type.upper() == "NULLPTR_DEREFERENCE" or "null_dereference" in bug_type_lower:
            implications.extend([
                "Will cause segmentation fault (SIGSEGV) at runtime",
                "Program will crash when this code path is executed",
                "This is a critical issue that must be fixed"
            ])
            
        elif "memory_leak" in bug_type_lower:
            implications.extend([
                "Program will consume progressively more memory over time",
                "Can lead to out-of-memory errors in long-running applications",
                "May cause system slowdown as available memory decreases"
            ])
            
        elif "buffer_overrun" in bug_type_lower:
            implications.extend([
                "Will cause memory corruption at runtime",
                "Can lead to crashes or security vulnerabilities",
                "Can be exploited for buffer overflow attacks if input is not properly validated",
                "May enable arbitrary code execution by attackers"
            ])
            
        elif "uninitialized_value" in bug_type_lower:
            implications.extend([
                "Results in unpredictable program behavior",
                "Can lead to incorrect calculations or control flow",
                "May expose sensitive data that was previously in memory"
            ])
            
        elif "use_after_free" in bug_type_lower:
            implications.extend([
                "Will cause memory corruption at runtime",
                "Can lead to crashes or security vulnerabilities",
                "The memory location may have been reallocated for other purposes",
                "Can be exploited for use-after-free attacks"
            ])
        
        elif "resource_leak" in bug_type_lower:
            implications.extend([
                "System resources (file handles, sockets, etc.) won't be properly released",
                "Can lead to resource exhaustion in long-running applications",
                "May prevent other processes from accessing the same resources"
            ])
            
        # If we have no specific implications, add a generic one
        if not implications:
            implications.append("Can cause unexpected program behavior")
            
        return implications
    
    def _generate_fix_suggestions(self, bug_type: str, description: str, variables: List[str]) -> List[str]:
        """
        Generate fix suggestions based on the issue type.
        
        Args:
            bug_type: Type of the issue
            description: Issue description
            variables: List of variables involved in the issue
            
        Returns:
            List of fix suggestions
        """
        bug_type_lower = bug_type.lower()
        suggestions = []
        
        var_name = variables[0] if variables else "the pointer"
        origin_line = self._extract_origin_line(description)
        
        if "null_dereference" in bug_type_lower:
            # More specific suggestions for null pointer dereference
            if origin_line:
                suggestions.extend([
                    f"Add a null check before dereferencing {var_name}",
                    f"Replace nullptr with a valid memory allocation (e.g., {var_name} = new char[1];)",
                    f"Add a guard clause: if ({var_name} == nullptr) return; // or throw an exception"
                ])
                
                # Look for if-else pattern in the raw trace
                has_if_check = False
                for result in self.raw_results:
                    for step in result.get("bug_trace", []):
                        if "compared to null" in step.get("description", ""):
                            has_if_check = True
                            break
                
                if has_if_check:
                    suggestions.append(f"Move the dereference inside the if ({var_name} != nullptr) block instead of the else block")
            else:
                suggestions.extend([
                    f"Add null check before dereferencing {var_name}",
                    f"Initialize {var_name} with a valid value",
                    "Use smart pointers to handle null cases automatically"
                ])
            
        elif "memory_leak" in bug_type_lower:
            suggestions.extend([
                "Free allocated memory when it's no longer needed",
                "Use smart pointers or containers to manage memory automatically",
                "Ensure all code paths properly free resources"
            ])
            
        elif "buffer_overrun" in bug_type_lower:
            suggestions.extend([
                "Add bounds checking before accessing the array",
                "Use safer array access methods or container classes",
                "Validate input sizes before using them for array access"
            ])
            
        elif "uninitialized_value" in bug_type_lower:
            suggestions.extend([
                f"Initialize {var_name} before use",
                "Provide default values for variables",
                "Add validation to ensure variables have been initialized"
            ])
            
        elif "use_after_free" in bug_type_lower:
            suggestions.extend([
                "Set pointers to null after freeing",
                "Use smart pointers to manage object lifetime",
                "Restructure code to avoid accessing freed memory"
            ])
            
        # Add specific suggestions based on code context
        if "null" in description.lower() and origin_line:
            # We have a null pointer issue with known origin
            suggestions.append(f"Consider using a sentinel value instead of null for {var_name}")
            suggestions.append(f"Initialize {var_name} with a safe default value at line {origin_line}")
        
        return suggestions


def process_infer_output(infer_dir: str = "infer-out") -> List[Dict[str, Any]]:
    """
    Process Infer output into LLM-friendly format.
    
    Args:
        infer_dir: Path to the Infer results directory
        
    Returns:
        List of processed issue dictionaries
    """
    processor = InferOutputProcessor(infer_dir)
    
    if processor.load_results():
        return processor.process_results()
    else:
        return []


def save_processed_results(results: List[Dict[str, Any]], output_file: str = "results/infer_processed.json") -> bool:
    """
    Save processed results to a JSON file.
    
    Args:
        results: Processed results
        output_file: Path to save the results
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Pretty print with proper indentation
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        return True
    except Exception as e:
        print(f"Error saving processed results: {str(e)}")
        return False 