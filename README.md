# DXTEMPLATETOOLS 🧰

A modular collection of Excel analysis and processing tools designed for scalable, maintainable data extraction and analysis workflows.

## 🏗️ Architecture

The project follows a clean, modular architecture:

```
DXTEMPLATETOOLS/
│
├── tools/                     # Each tool lives in its own folder
│   ├── excel_flattener/       # Flatten Excel workbooks to CSV
│   │   ├── __init__.py
│   │   ├── main.py            # Entry point
│   │   ├── utils.py           # Tool-specific utilities
│   │   └── config.yaml        # Tool configuration
│   │
│   ├── guid_extractor/        # Extract data using GUID mappings
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── utils.py
│   │   └── config.yaml
│   │
│   └── ...                    # Future tools
│
├── shared/                    # Shared utilities across tools
│   ├── excel_io.py           # Excel I/O operations
│   ├── logger.py             # Logging setup
│   └── file_utils.py         # File/path utilities
│
├── launcher.py               # Central tool launcher
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Installation

```bash
# Clone or navigate to the DXTEMPLATETOOLS directory
cd DXTEMPLATETOOLS

# Install dependencies
pip install -r requirements.txt
```

### Running Tools

You can run tools in three ways:

#### 1. Using the Central Launcher (Recommended)

```bash
# List available tools
python launcher.py --list

# Run excel_flattener
python launcher.py --tool excel_flattener input.xlsx

# Run guid_extractor
python launcher.py --tool guid_extractor frs102.xlsx guid_mappings.csv

# Get tool-specific help
python launcher.py --tool excel_flattener --help
```

#### 2. Running Tools Directly

```bash
# Run excel_flattener directly
python tools/excel_flattener/main.py input.xlsx

# Run guid_extractor directly
python tools/guid_extractor/main.py frs102.xlsx guid_mappings.csv
```

#### 3. As Python Modules

```python
from tools.excel_flattener import flatten_excel_workbook
from tools.guid_extractor import extract_guid_data

# Flatten a workbook
result = flatten_excel_workbook("input.xlsx")
print(f"Processed {result.total_cells} cells")

# Extract GUID data
result = extract_guid_data("frs102.xlsx", "mappings.csv")
print(f"Extracted {result.rows_extracted} rows")
```

## 🛠️ Available Tools

### 🤖 LangGraph Agent Development Playbook

**NEW**: A comprehensive framework for converting support processes into executable LangGraph agents.

**Location**: `agents/`

**Features:**
- Process assessment checklist for evaluating documentation readiness
- Structured Notion template system for agent specification
- Automated code generation using Jinja2 templates
- Complete worked examples with test cases
- CLI tools for agent generation and validation

**Quick Start:**
```bash
# Assess if your process is ready for automation
open agents/assessment/process_assessment_checklist.md

# Set up Notion template for documentation
open agents/templates/notion_template.md

# Generate agent from documentation
python agents/tools/generate_agent.py --json-file process.json
```

👉 **[View Complete Playbook](agents/README.md)**

### 📊 Excel Flattener

Flattens Excel workbooks into structured CSV data for analysis and LLM processing.

**Features:**
- Processes all sheets in a workbook
- Extracts cell metadata (formulas, value types, positions)
- Configurable empty cell inclusion
- Detailed processing summaries

**Usage:**
```bash
python launcher.py --tool excel_flattener input.xlsx
python launcher.py --tool excel_flattener input.xlsx -o output.csv --include-empty
```

**Output CSV Columns:**
- `Sheet`: Sheet name
- `RowNum`: Row number
- `ColRef`: Column reference (A, B, C, etc.)
- `Formula Text`: Formula text if it's a formula cell
- `CellValue`: Actual cell value
- `Value Type`: Type classification (formula, number, string, etc.)

### 🔍 GUID Extractor

Extracts data from specific Excel rows using GUID mappings for FRS102 workbook analysis.

**Features:**
- GUID-based row identification (8-character unique identifiers)
- Sheet-specific searching
- Configurable column range extraction (default: columns 124-200)
- Comprehensive extraction reporting

**Usage:**
```bash
python launcher.py --tool guid_extractor frs102.xlsx guid_mappings.csv
python launcher.py --tool guid_extractor frs102.xlsx mappings.csv --start-col 100 --end-col 150
```

**GUID Mapping CSV Format:**
```csv
GUID,SheetName
00CAC489,SoCI
12345678,PL
87654321,BS
```

**How it Works:**
1. Reads GUID mappings from CSV
2. For each GUID, searches column A of the specified sheet
3. Extracts data from columns 124-200 (or custom range) of the matching row
4. Consolidates all results into a single CSV output

**Output CSV Columns:**
- `SheetName`: Source sheet name
- `GUID`: The matched GUID
- `RowNum`: Row number where GUID was found
- `Col124`, `Col125`, ..., `Col200`: Extracted column data

## � Development

### Adding New Tools

1. **Create Tool Directory:**
   ```bash
   mkdir tools/my_new_tool
   ```

2. **Create Required Files:**
   ```bash
   touch tools/my_new_tool/__init__.py
   touch tools/my_new_tool/main.py
   touch tools/my_new_tool/utils.py
   touch tools/my_new_tool/config.yaml
   ```

3. **Implement main.py:**
   ```python
   # tools/my_new_tool/main.py
   import sys
   from pathlib import Path
   
   # Add parent directories to path for imports
   sys.path.insert(0, str(Path(__file__).parent.parent.parent))
   
   from shared.logger import setup_logging, get_logger
   
   def main():
       """Main entry point for my_new_tool."""
       print("Hello from my new tool!")
   
   if __name__ == "__main__":
       main()
   ```

4. **Test with Launcher:**
   ```bash
   python launcher.py --tool my_new_tool
   ```

### Using Shared Utilities

The `shared/` module provides common functionality:

```python
# Excel I/O
from shared.excel_io import load_excel_workbook, save_to_csv

# Logging
from shared.logger import setup_logging, get_logger

# File utilities
from shared.file_utils import validate_excel_file, generate_output_filename
```

### Configuration Files

Each tool can have a `config.yaml` file for default settings:

```yaml
# tools/my_tool/config.yaml
tool_name: "my_tool"
description: "Description of what this tool does"
version: "1.0.0"

defaults:
  log_level: "INFO"
  output_suffix: "_processed"
```

## � Logging

All tools support configurable logging:

```bash
# Verbose logging
python launcher.py --tool excel_flattener input.xlsx --verbose

# Log to file
python launcher.py --tool excel_flattener input.xlsx --log-file process.log
```

## 🤝 Contributing

1. Follow the modular architecture
2. Use shared utilities when possible
3. Include comprehensive error handling
4. Add configuration files for tool settings
5. Update this README when adding new tools

## 📄 License

This project is part of the DXTEMPLATETOOLS suite for Excel analysis and processing.

## � Support

- Check tool-specific help: `python launcher.py --tool <tool_name> --help`
- Review log files for detailed error information
- Ensure Excel files are in supported formats (.xlsx, .xlsm)
