import json
import os
import argparse
import logging
from collections import defaultdict
from pathlib import Path

from src.llm import logger

def get_comment_syntax(file_path):
    """
    Return the appropriate comment syntax based on file extension.
    """
    extension = Path(file_path).suffix.lower()
    
    # Dictionary mapping file extensions to comment prefixes
    comment_map = {
        '.py': '#',
        '.js': '//',
        '.ts': '//',
        '.java': '//',
        '.c': '//',
        '.cpp': '//',
        '.h': '//',
        '.hpp': '//',
        '.cs': '//',
        '.php': '//',
        '.swift': '//',
        '.go': '//',
        '.rs': '//',
        '.rb': '#',
        '.pl': '#',
        '.sh': '#',
        '.bash': '#',
        '.yaml': '#',
        '.yml': '#',
        '.toml': '#',
        '.sql': '--',
    }
    
    return comment_map.get(extension, '//')  # Default to C-style comments if extension not found

def process_infer_report(report_path):
    """
    Process the Infer report JSON file.
    
    1. Group entries by file
    2. Read content of each file
    3. Append qualifier to the specified line
    
    Args:
        report_path: Path to the infer report.json file
        
    Returns:
        A dictionary mapping file paths to their modified content
    """
    # Read and parse the report.json file
    with open(report_path, 'r') as f:
        report_data = json.load(f)
    
    # Group entries by file
    file_groups = defaultdict(list)
    for entry in report_data:
        file_path = entry.get('file')
        if file_path:
            file_groups[file_path].append(entry)
    
    logger.info(f"Found issues in {len(file_groups)} files")
    
    # Store modified content
    modified_files = {}
    
    # Process each file
    for file_path, entries in file_groups.items():
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f"Warning: File not found: {file_path}")
            continue
        
        # Determine comment syntax for this file
        comment_prefix = get_comment_syntax(file_path)
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        file_content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    file_content = f.readlines()
                break  # If we get here, the encoding worked
            except UnicodeDecodeError:
                continue
        
        if file_content is None:
            logger.error(f"Error: Could not read {file_path} with any of the attempted encodings")
            continue
        
        # Track modified lines to avoid multiple modifications to the same line
        modified_lines = {}  # line_idx -> qualifier
        
        # Process each entry for this file
        for entry in entries:
            line_num = entry.get('line')
            qualifier = entry.get('qualifier')
            
            if line_num is None or qualifier is None:
                continue
                
            # Adjust line number (0-indexed in list, 1-indexed in report)
            line_idx = line_num - 1
            
            # Skip if line index is out of range
            if line_idx < 0 or line_idx >= len(file_content):
                logger.warning(f"Warning: Line {line_num} out of range for {file_path}")
                continue
                
            # Skip if this line was already modified
            if line_idx in modified_lines:
                logger.warning(f"Warning: Multiple issues on line {line_num} in {file_path}")
                continue
                
            # Store the line and qualifier
            modified_lines[line_idx] = qualifier
        
        # Handle modifications
        if modified_lines:
            # Create a copy of the content for modification
            modified_content = file_content.copy()
            
            # Apply modifications to the copy
            for line_idx, qualifier in modified_lines.items():
                modified_content[line_idx] = modified_content[line_idx].rstrip() + f" {comment_prefix} INFER_WARNING: {qualifier}\n"
            
            # Store the modified content
            modified_files[file_path] = ''.join(modified_content)
            logger.info(f"Processed {file_path}: modified {len(modified_lines)} lines")
    
    return modified_files

if __name__ == "__main__":
    modified_files = process_infer_report("output/infer-out/report.json")
    # Print summary of modifications
    if modified_files:
        logger.info(f"\nSuccessfully processed {len(modified_files)} files")
        for file_path in modified_files.keys():
            logger.info(f"  - {file_path}")
            logger.debug(modified_files[file_path])
    else:
        logger.info("No files were modified")