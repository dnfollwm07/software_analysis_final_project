# Infer Report Processor

This script processes Infer static analysis report files and returns modified versions of the source code files with bug qualifiers added as comments.

## Features

- Groups issues by source file
- Automatically determines the appropriate comment syntax based on file extension
- Handles different character encodings
- Supports dry-run mode to preview changes without modifying files
- Returns modified content as strings instead of directly modifying source files
- Avoids duplicate annotations when multiple issues occur on the same line

## Usage

```bash
# Process with default report location (output/infer-out/report.json)
python src/llm/infer_report_processor.py

# Specify a custom report path
python src/llm/infer_report_processor.py --report path/to/report.json

# Preview changes without modifying files
python src/llm/infer_report_processor.py --dry-run

# Optionally save output to a directory
python src/llm/infer_report_processor.py --output-dir output/modified_files
```

## How It Works

1. The script reads the Infer report JSON file
2. Issues are grouped by the source file they occur in
3. For each source file:
   - The file content is read
   - For each issue, the qualifier is appended as a comment at the end of the specified line
   - The modified content is returned as a string
4. Modified content can be optionally saved to files in a specified output directory

## Programmatic Usage

You can also use the script's functions in your own code:

```python
from src.llm.infer_report_processor import process_infer_report

# Get a dictionary of modified files
modified_files = process_infer_report("path/to/report.json")

# Process the modified content
for file_path, content in modified_files.items():
    # Do something with file_path and content
    print(f"Modified content for {file_path}:")
    print(content)
```

## Supported File Types

The script automatically detects the appropriate comment syntax based on file extension:
- C-style languages (C, C++, Java, etc.): `//`
- Python, Ruby, Shell, YAML: `#`
- SQL: `--`
- And more...

Default comment syntax is `//` if the file extension is unknown. 