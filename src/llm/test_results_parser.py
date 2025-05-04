"""
Test Results Parser Module.

This module provides functionality to parse JUnit XML test results and extract failed test information.
"""

import xml.etree.ElementTree as ET
import sys
import logging
from typing import Dict, List, Optional

from src.llm import logger


class TestResultsParser:
    """Parser for JUnit XML test results.
    
    This class parses JUnit XML test results and provides methods to extract
    information about failed tests.
    """
    
    def __init__(self, xml_file_path: str):
        """Initialize the parser with a JUnit XML file path.
        
        Args:
            xml_file_path: Path to the JUnit XML test results file.
        """
        self.xml_file_path = xml_file_path
        self.tree = None
        self.root = None
        self._parse_xml()
    
    def _parse_xml(self) -> None:
        """Parse the XML file into an ElementTree."""
        try:
            self.tree = ET.parse(self.xml_file_path)
            self.root = self.tree.getroot()
        except Exception as e:
            raise RuntimeError(f"Failed to parse XML file: {e}")
    
    def get_test_summary(self) -> Dict[str, int]:
        """Get summary of test results.
        
        Returns:
            Dictionary containing test summary (total, failures, etc.)
        """
        if self.root is None:
            return {}
        
        return {
            "total": int(self.root.get("tests", 0)),
            "failures": int(self.root.get("failures", 0)),
            "disabled": int(self.root.get("disabled", 0)),
            "skipped": int(self.root.get("skipped", 0)),
        }
    
    def get_failed_tests(self) -> List[Dict[str, str]]:
        """Get list of failed tests with their details.
        
        Returns:
            List of dictionaries containing information about each failed test.
        """
        if self.root is None:
            return []
        
        failed_tests = []
        
        for testcase in self.root.findall(".//testcase"):
            failure = testcase.find("failure")
            if failure is not None:
                system_out = testcase.find("system-out")
                output_text = system_out.text if system_out is not None else ""
                
                failed_tests.append({
                    "name": testcase.get("name", ""),
                    "classname": testcase.get("classname", ""),
                    "time": testcase.get("time", ""),
                    "failure_message": failure.get("message", ""),
                    "output": output_text
                })
        
        return failed_tests
    
    def get_failed_test_outputs(self) -> List[str]:
        """Get only the output text of failed tests.
        
        Returns:
            List of output texts from failed tests.
        """
        failed_tests = self.get_failed_tests()
        return [test["output"] for test in failed_tests]
    
    def get_detailed_failed_test_info(self) -> List[Dict[str, str]]:
        """Get detailed information about failed tests, including only relevant output.
        
        Returns:
            List of dictionaries with test name and filtered output containing error messages.
        """
        failed_tests = self.get_failed_tests()
        detailed_info = []
        
        for test in failed_tests:
            output_lines = test["output"].splitlines()
            filtered_output = []
            
            # Extract only relevant error information
            capture_lines = False
            for line in output_lines:
                if "[ RUN      ]" in line:
                    capture_lines = True
                    filtered_output.append(line)
                elif "[  FAILED  ]" in line:
                    filtered_output.append(line)
                    capture_lines = False
                elif "Failure" in line or "Failed" in line or "Error" in line:
                    filtered_output.append(line)
                elif capture_lines and line.strip() and not line.startswith("["):
                    filtered_output.append(line)
            
            detailed_info.append({
                "name": test["name"],
                "classname": test["classname"],
                "filtered_output": "\n".join(filtered_output)
            })
        
        return detailed_info

if __name__ == "__main__":
    # Example usage
    
    if len(sys.argv) < 2:
        logger.error("Usage: python test_results_parser.py <path_to_xml_file>")
        sys.exit(1)
    
    xml_file = sys.argv[1]
    parser = TestResultsParser(xml_file)
    
    logger.info("Test Summary:")
    logger.info(parser.get_test_summary())
    
    logger.info("\nFailed Tests:")
    failed_tests = parser.get_detailed_failed_test_info()
    logger.info(failed_tests)
    
    for i, test in enumerate(failed_tests, 1):
        logger.info(f"\n{i}. {test['name']} ({test['classname']})")
        logger.info("-" * 50)
        logger.info(test['filtered_output'])
        logger.info("-" * 50) 