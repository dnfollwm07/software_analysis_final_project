import json
import os
import argparse
from collections import defaultdict
from pathlib import Path

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
        dry_run: If True, only print what would be done without making changes
        
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
    
    print(f"Found issues in {len(file_groups)} files")
    
    # Store modified content
    modified_files = {}
    
    # Process each file
    for file_path, entries in file_groups.items():
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
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
            print(f"Error: Could not read {file_path} with any of the attempted encodings")
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
                print(f"Warning: Line {line_num} out of range for {file_path}")
                continue
                
            # Skip if this line was already modified
            if line_idx in modified_lines:
                print(f"Warning: Multiple issues on line {line_num} in {file_path}")
                continue
                
            # Store the line and qualifier
            modified_lines[line_idx] = qualifier
        
        # Handle modifications
        if modified_lines:
            # Create a copy of the content for modification
            modified_content = file_content.copy()
            
            # Apply modifications to the copy
            for line_idx, qualifier in modified_lines.items():
                modified_content[line_idx] = modified_content[line_idx].rstrip() + f" {comment_prefix} {qualifier}\n"
            
            # Store the modified content
            modified_files[file_path] = ''.join(modified_content)
            print(f"Processed {file_path}: modified {len(modified_lines)} lines")
    
    return modified_files

def main():
    parser = argparse.ArgumentParser(description='Process Infer report and annotate source files with qualifiers')
    parser.add_argument('--report', default="output/infer-out/report.json", 
                        help='Path to the Infer report.json file (default: output/infer-out/report.json)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.report):
        print(f"Error: Report file not found: {args.report}")
        return
        
    modified_files = process_infer_report(args.report)
    
    
    # Print summary of modifications
    if modified_files:
        print(f"\nSuccessfully processed {len(modified_files)} files")
        for file_path in modified_files.keys():
            print(f"  - {file_path}")
            print(modified_files[file_path])
    else:
        print("No files were modified")

if __name__ == "__main__":
    main() 