"""
Test case generation for code repair validation.

This module provides functionality to generate test cases that can validate
whether a code repair has fixed the identified issues.
"""
from typing import List, Dict, Any, Optional
import ast
import os
import re
import tempfile
import subprocess
from pathlib import Path


class TestGenerator:
    """Test case generator for code repair validation."""
    
    def __init__(self, source_file: str, error_info: Optional[Dict[str, Any]] = None):
        """
        Initialize the test generator.
        
        Args:
            source_file: Path to the source file to test
            error_info: Dictionary containing error information from static analysis
        """
        self.source_file = Path(source_file)
        self.error_info = error_info or {}
        self.ast_tree = None
        
    def parse_source(self) -> bool:
        """
        Parse the source file into an AST for analysis.
        
        Returns:
            bool: True if parsing succeeded, False otherwise
        """
        try:
            # Only try to parse Python files
            if self.source_file.suffix.lower() == '.py':
                with open(self.source_file, 'r') as f:
                    source = f.read()
                self.ast_tree = ast.parse(source)
                return True
            return False
        except Exception as e:
            print(f"Error parsing source: {e}")
            return False
        
    def generate_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for the error location.
        
        Returns:
            List of test case dictionaries containing inputs and expected outputs
        """
        if not self.error_info:
            return []
            
        test_cases = []
        
        # Try to parse Python source if available
        file_extension = self.source_file.suffix.lower()
        if file_extension == '.py' and self.parse_source():
            # For Python files, extract function names and generate tests
            functions = self._extract_functions()
            
            for func_name, func_info in functions.items():
                # Generate test cases for each function
                test_cases.extend(self._generate_function_tests(func_name, func_info))
        elif file_extension in ['.cpp', '.cc', '.c', '.h', '.hpp']:
            # For C++ files, extract functions and generate tests
            functions = self._extract_cpp_functions()
            
            for func_name, func_info in functions.items():
                # Generate test cases for each function
                test_cases.extend(self._generate_cpp_function_tests(func_name, func_info))
                
        return test_cases
        
    def generate_symbolic_execution_tests(self) -> List[Dict[str, Any]]:
        """
        Generate test cases using symbolic execution.
        
        Returns:
            List of test cases derived from symbolic execution
        """
        # This would be a more advanced implementation using tools like KLEE
        # For the purpose of this example, we'll return a placeholder
        print("Symbolic execution test generation is not fully implemented")
        return []
        
    def export_tests_to_file(self, output_path: Optional[str] = None) -> str:
        """
        Export generated test cases to a test file.
        
        Args:
            output_path: Path to write the test file
            
        Returns:
            Path to the generated test file
        """
        if output_path:
            test_file_path = Path(output_path)
        else:
            # Generate a default test file path
            base_name = self.source_file.stem
            file_extension = self.source_file.suffix.lower()
            
            if file_extension == '.py':
                test_file_name = f"test_{base_name}.py"
            else:
                test_file_name = f"test_{base_name}.cpp"
                
            # Create test directory if needed
            test_dir = self.source_file.parent / "tests"
            test_dir.mkdir(exist_ok=True)
            
            test_file_path = test_dir / test_file_name
            
        # Generate test cases
        test_cases = self.generate_test_cases()
        
        try:
            # Write test cases to file
            if self.source_file.suffix.lower() == '.py':
                self._write_python_test_file(test_file_path, test_cases)
            else:
                self._write_cpp_test_file(test_file_path, test_cases)
                
            print(f"Generated test file: {test_file_path}")
            return str(test_file_path)
            
        except Exception as e:
            print(f"Error exporting tests: {e}")
            return ""
            
    def _extract_functions(self) -> Dict[str, Dict[str, Any]]:
        """
        Extract function definitions from Python source.
        
        Returns:
            Dictionary mapping function names to their details
        """
        functions = {}
        
        if not self.ast_tree:
            return functions
            
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef):
                # Extract basic function information
                function_info = {
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "line_start": node.lineno,
                    "line_end": max(node.lineno, node.body[-1].lineno if node.body else node.lineno),
                    "returns": self._infer_return_type(node)
                }
                functions[node.name] = function_info
                
        return functions
    
    def _extract_cpp_functions(self) -> Dict[str, Dict[str, Any]]:
        """
        Extract function definitions from C++ source using regex.
        
        Returns:
            Dictionary mapping function names to their details
        """
        functions = {}
        
        try:
            with open(self.source_file, 'r') as f:
                source = f.read()
                
            # Simple regex to find function definitions
            # This is a basic implementation and would need to be more robust in a real system
            function_pattern = r'(\w+)\s+(\w+)\s*\((.*?)\)\s*(?:const)?\s*{'
            
            for match in re.finditer(function_pattern, source, re.DOTALL):
                return_type, func_name, args_str = match.groups()
                
                # Extract arguments
                args = []
                if args_str.strip():
                    # Very simple argument parsing (would need improvement)
                    for arg in args_str.split(','):
                        arg = arg.strip()
                        if arg:
                            # Try to extract param name from "type name"
                            parts = arg.split()
                            if parts:
                                arg_name = parts[-1].replace('*', '').replace('&', '')
                                args.append(arg_name)
                
                # Find the approximate end of the function
                start_pos = match.start()
                line_start = source[:start_pos].count('\n') + 1
                
                # Find matching closing brace (simple approach)
                open_braces = 1
                pos = match.end()
                while open_braces > 0 and pos < len(source):
                    if source[pos] == '{':
                        open_braces += 1
                    elif source[pos] == '}':
                        open_braces -= 1
                    pos += 1
                
                line_end = source[:pos].count('\n') + 1
                
                function_info = {
                    "name": func_name,
                    "return_type": return_type,
                    "args": args,
                    "line_start": line_start,
                    "line_end": line_end
                }
                
                functions[func_name] = function_info
                
        except Exception as e:
            print(f"Error extracting C++ functions: {e}")
            
        return functions
    
    def _infer_return_type(self, node: ast.FunctionDef) -> str:
        """
        Try to infer the return type of a Python function.
        
        Args:
            node: The function's AST node
            
        Returns:
            String representing the return type
        """
        # Check for return annotation
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            return "Any"
            
        # Check return statements
        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Return) and subnode.value:
                if isinstance(subnode.value, ast.Num):
                    return "int" if isinstance(subnode.value.n, int) else "float"
                elif isinstance(subnode.value, ast.Str):
                    return "str"
                elif isinstance(subnode.value, ast.List):
                    return "List"
                elif isinstance(subnode.value, ast.Dict):
                    return "Dict"
                elif isinstance(subnode.value, ast.Name) and subnode.value.id == "None":
                    return "None"
        
        return "Any"
    
    def _generate_function_tests(self, func_name: str, func_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate test cases for a Python function.
        
        Args:
            func_name: Name of the function
            func_info: Function information dictionary
            
        Returns:
            List of test case dictionaries
        """
        test_cases = []
        
        # Generate basic tests based on argument types
        for i in range(min(3, len(func_info["args"]) + 1)):
            test_case = {
                "func_name": func_name,
                "inputs": self._generate_test_inputs(func_info["args"]),
                "expected_type": func_info["returns"],
                "description": f"Test case {i+1} for {func_name}"
            }
            test_cases.append(test_case)
            
        return test_cases
    
    def _generate_cpp_function_tests(self, func_name: str, func_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate test cases for a C++ function.
        
        Args:
            func_name: Name of the function
            func_info: Function information dictionary
            
        Returns:
            List of test case dictionaries
        """
        test_cases = []
        
        # Generate basic tests based on argument types
        for i in range(min(3, len(func_info["args"]) + 1)):
            test_case = {
                "func_name": func_name,
                "inputs": self._generate_cpp_test_inputs(func_info["args"], func_info["return_type"]),
                "expected_type": func_info["return_type"],
                "description": f"Test case {i+1} for {func_name}"
            }
            test_cases.append(test_case)
            
        return test_cases
    
    def _generate_test_inputs(self, args: List[str]) -> Dict[str, Any]:
        """
        Generate test inputs for Python function arguments.
        
        Args:
            args: List of argument names
            
        Returns:
            Dictionary mapping argument names to test values
        """
        inputs = {}
        
        for arg in args:
            # Generate a simple value based on argument name
            if "id" in arg.lower() or "index" in arg.lower():
                inputs[arg] = 1
            elif "name" in arg.lower() or "str" in arg.lower():
                inputs[arg] = "test"
            elif "list" in arg.lower() or "array" in arg.lower():
                inputs[arg] = [1, 2, 3]
            elif "dict" in arg.lower() or "map" in arg.lower():
                inputs[arg] = {"key": "value"}
            elif "bool" in arg.lower() or "flag" in arg.lower():
                inputs[arg] = True
            elif "float" in arg.lower() or "double" in arg.lower():
                inputs[arg] = 1.0
            else:
                inputs[arg] = 0
                
        return inputs
    
    def _generate_cpp_test_inputs(self, args: List[str], return_type: str) -> Dict[str, str]:
        """
        Generate test inputs for C++ function arguments.
        
        Args:
            args: List of argument names
            return_type: Function return type
            
        Returns:
            Dictionary mapping argument names to test values (as strings)
        """
        inputs = {}
        
        for arg in args:
            # Generate a simple value based on argument name
            if "id" in arg.lower() or "index" in arg.lower():
                inputs[arg] = "1"
            elif "name" in arg.lower() or "str" in arg.lower():
                inputs[arg] = '"test"'
            elif "list" in arg.lower() or "array" in arg.lower():
                inputs[arg] = "{1, 2, 3}"
            elif "bool" in arg.lower() or "flag" in arg.lower():
                inputs[arg] = "true"
            elif "float" in arg.lower() or "double" in arg.lower():
                inputs[arg] = "1.0"
            else:
                inputs[arg] = "0"
                
        return inputs
    
    def _write_python_test_file(self, output_path: Path, test_cases: List[Dict[str, Any]]) -> None:
        """
        Write a Python test file with the generated tests.
        
        Args:
            output_path: Path to write the test file
            test_cases: List of test case dictionaries
        """
        import_path = self.source_file.stem
        
        with open(output_path, 'w') as f:
            # Write header and imports
            f.write(f"""
import unittest
import sys
from pathlib import Path
import os

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

# Import the module to test
try:
    from {import_path} import *
except ImportError:
    # Try with the full path
    module_path = str(Path(__file__).parent.parent)
    if module_path not in sys.path:
        sys.path.append(module_path)
    from {import_path} import *


class Test{import_path.capitalize()}(unittest.TestCase):
    \"\"\"Test cases for {import_path}.\"\"\"
""")
            
            # Write test methods
            for i, test_case in enumerate(test_cases):
                func_name = test_case["func_name"]
                inputs = test_case["inputs"]
                inputs_str = ", ".join([f"{k}={repr(v)}" for k, v in inputs.items()])
                description = test_case['description']
                
                f.write(f"""
    def test_{func_name}_{i+1}(self):
        \"\"\"Test {description}.\"\"\"
        # Test function call
        result = {func_name}({inputs_str})
        
        # Add assertions based on expected output
        self.assertIsNotNone(result)
""")
            
            # Add main section
            f.write("""

if __name__ == '__main__':
    unittest.main()
""")
            
    def _write_cpp_test_file(self, output_path: Path, test_cases: List[Dict[str, Any]]) -> None:
        """
        Write a C++ test file with the generated tests.
        
        Args:
            output_path: Path to write the test file
            test_cases: List of test case dictionaries
        """
        header_path = self.source_file.name
        
        with open(output_path, 'w') as f:
            # Write header and includes
            f.write(f"""#include <iostream>
#include <cassert>
#include "{header_path}"

// Test cases for {self.source_file.stem}

int main() {{
    int test_passed = 0;
    int test_failed = 0;
    
""")
            
            # Write test cases
            for i, test_case in enumerate(test_cases):
                func_name = test_case["func_name"]
                inputs = test_case["inputs"]
                inputs_str = ", ".join([f"{v}" for v in inputs.values()])
                description = test_case['description']
                
                f.write(f"""    // Test {description}
    try {{
        auto result = {func_name}({inputs_str});
        std::cout << "Test {i+1} passed\\n";
        test_passed++;
    }} catch (const std::exception& e) {{
        std::cerr << "Test {i+1} failed: " << e.what() << "\\n";
        test_failed++;
    }} catch (...) {{
        std::cerr << "Test {i+1} failed with unknown exception\\n";
        test_failed++;
    }}
    
""")
            
            # Add summary
            f.write("""    // Print test summary
    std::cout << "\\nTest Summary:\\n";
    std::cout << "Passed: " << test_passed << "\\n";
    std::cout << "Failed: " << test_failed << "\\n";
    
    return test_failed;
}
""")


def generate_tests(target_file: str) -> List[str]:
    """
    Generate test files for a target source file.
    
    Args:
        target_file: Path to the source file to test
        
    Returns:
        List of paths to the generated test files
    """
    file_path = Path(target_file)
    if not file_path.exists():
        print(f"Error: Target file {target_file} does not exist")
        return []
        
    # Create a test generator
    generator = TestGenerator(target_file)
    
    # Export test file
    test_file = generator.export_tests_to_file()
    
    if test_file:
        return [test_file]
    return [] 