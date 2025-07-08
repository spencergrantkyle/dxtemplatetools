# DXTEMPLATETOOLS 🧰

A comprehensive modular Python toolkit for Excel analysis, data extraction, and AI agent development. This project provides enterprise-grade tools for processing Excel workbooks, extracting structured data, and developing LangGraph automation agents.

## 🎯 Project Overview

**DXTEMPLATETOOLS** (also known as **ExcelFlattener** in package configuration) is designed for:

- **Excel Data Processing**: Flatten complex Excel workbooks into structured CSV data for AI/LLM processing
- **Financial Data Extraction**: GUID-based extraction from FRS102 workbooks and similar structured documents  
- **AI Agent Development**: Complete LangGraph agent development playbook with templates and automation
- **Enterprise Integration**: Modular architecture supporting integration into larger data workflows

## 🏗️ Architecture Overview

```
DXTEMPLATETOOLS/
│
├── 🔧 Core Modules
│   ├── flattener/              # Core Excel flattening engine
│   │   ├── __init__.py         # Main API exports
│   │   ├── flattener.py        # Core flattening logic
│   │   └── utils.py            # Analysis utilities
│   ├── shared/                 # Shared utilities across tools
│   │   ├── excel_io.py         # Excel I/O operations
│   │   ├── logger.py           # Centralized logging
│   │   └── file_utils.py       # File/path utilities
│   └── main.py                 # Standalone flattener script
│
├── 🛠️ Tools & Applications  
│   ├── launcher.py             # Central tool launcher & discovery
│   ├── cli.py                  # Enhanced CLI interface
│   └── tools/                  # Modular tool collection
│       ├── excel_flattener/    # Excel workbook flattening
│       └── guid_extractor/     # GUID-based data extraction
│
├── 🤖 AI Agent Development
│   └── agents/                 # LangGraph agent development framework
│       ├── assessment/         # Process evaluation tools
│       ├── templates/          # Code generation templates  
│       ├── examples/           # Complete worked examples
│       └── tools/              # Agent generation utilities
│
└── 📁 Configuration & Data
    ├── pyproject.toml          # Project configuration
    ├── requirements.txt        # Python dependencies
    └── example_guid_mapping.csv # Sample data files
```

## 🚀 Quick Start

### Installation & Setup

```bash
# Navigate to project directory
cd DXTEMPLATETOOLS

# Install dependencies (choose one method)

# Method 1: Using pip
pip install -r requirements.txt

# Method 2: Using UV (recommended for development)
uv sync

# Method 3: Install as package with AI dependencies
pip install -e ".[ai,dev]"
```

### Core Usage Patterns

#### 1. Excel Flattening (Multiple Options)

```bash
# Enhanced CLI (recommended)
python cli.py input.xlsx --save-artifacts --log-level DEBUG

# Central launcher
python launcher.py --tool excel_flattener input.xlsx

# Standalone script  
python main.py input.xlsx -o output.csv

# Direct module usage
python -m flattener input.xlsx --include-empty
```

#### 2. GUID-Based Data Extraction

```bash
# Extract data using GUID mappings
python launcher.py --tool guid_extractor frs102.xlsx guid_mappings.csv

# Custom column range
python launcher.py --tool guid_extractor frs102.xlsx mappings.csv --start-col 100 --end-col 150
```

#### 3. Tool Discovery & Management

```bash
# List all available tools
python launcher.py --list

# Get tool-specific help
python launcher.py --tool excel_flattener --help

# Run with verbose logging
python launcher.py --tool guid_extractor input.xlsx mappings.csv --verbose
```

## 🔧 Core Components

### 📊 Excel Flattener

**Purpose**: Transform complex Excel workbooks into structured, AI-ready CSV data.

**Key Features**:
- Comprehensive cell metadata extraction (formulas, types, positions)
- Support for all Excel data types (formulas, numbers, strings, dates, booleans)
- Configurable empty cell inclusion
- Multi-sheet processing with sheet identification
- Detailed processing analytics and summaries

**Output Schema**:
```csv
Sheet,RowNum,ColRef,Formula Text of cell,CellValue,Value Type
SoCI,1,A,"=SUM(B1:B10)",150.5,formula
SoCI,1,B,,150.5,number
SoCI,1,C,"Report Title",string
```

**Advanced Usage**:
```python
from flattener import flatten_workbook

# Programmatic usage with full control
result = flatten_workbook("complex_workbook.xlsx", include_empty_cells=True)
print(f"Processed {result.total_cells} cells across {result.sheet_count} sheets")
```

### 🔍 GUID Extractor  

**Purpose**: Extract specific data rows from FRS102 workbooks using GUID identifiers.

**Key Features**:
- 8-character GUID-based row identification
- Sheet-specific searching with configurable column ranges  
- Bulk extraction with comprehensive reporting
- Support for custom column ranges (default: 124-200)
- Consolidated output across multiple sheets

**GUID Mapping Format**:
```csv
GUID,SheetName
00CAC489,SoCI
12345678,PL  
87654321,BS
```

**Workflow**:
1. Reads GUID-to-sheet mappings from CSV
2. Searches column A of each specified sheet for GUID matches
3. Extracts data from specified column range (default cols 124-200)
4. Consolidates results into single output file

### 🤖 LangGraph Agent Development Playbook

**Purpose**: Structured framework for converting business processes into executable LangGraph agents.

**Complete Workflow**:
1. **Process Assessment** - Evaluate documentation readiness using comprehensive checklist
2. **Structured Documentation** - Notion template system for capturing requirements
3. **Code Generation** - Automated agent creation using Jinja2 templates
4. **Testing & Deployment** - Built-in testing frameworks and examples

**Quick Start**:
```bash
# Assess process readiness
open agents/assessment/process_assessment_checklist.md

# Document using structured template
open agents/templates/notion_template.md

# Generate agent from documentation
python agents/tools/generate_agent.py --json-file process_specification.json

# Review examples
ls agents/examples/llp_1a_linkmap_update/
```

### � Shared Utilities

**Purpose**: Common functionality across all tools ensuring consistency and maintainability.

**Components**:
- **Excel I/O** (`shared/excel_io.py`): Robust workbook loading, sheet processing, error handling
- **Logging** (`shared/logger.py`): Centralized logging with file output, level control  
- **File Utilities** (`shared/file_utils.py`): Path validation, output naming, file type checking

**Usage in Custom Tools**:
```python
from shared.excel_io import load_excel_workbook, save_to_csv
from shared.logger import setup_logging, get_logger
from shared.file_utils import validate_excel_file, generate_output_filename

logger = get_logger(__name__)
```

## 🛠️ Development Guide

### Adding New Tools

1. **Create Tool Structure**:
```bash
mkdir tools/my_new_tool
touch tools/my_new_tool/{__init__.py,main.py,utils.py,config.yaml}
```

2. **Implement Tool Interface**:
```python
# tools/my_new_tool/main.py
import sys
from pathlib import Path

# Enable imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logger import setup_logging, get_logger
from shared.excel_io import load_excel_workbook

def main():
    """Tool entry point - called by launcher."""
    logger = get_logger(__name__)
    logger.info("Running my_new_tool")
    # Tool implementation here

if __name__ == "__main__":
    main()
```

3. **Configure Tool**:
```yaml
# tools/my_new_tool/config.yaml
tool_name: "my_new_tool"
description: "Brief description of tool functionality"
version: "1.0.0"
defaults:
  log_level: "INFO"
  output_suffix: "_processed"
```

4. **Test Integration**:
```bash
python launcher.py --list  # Should show your tool
python launcher.py --tool my_new_tool --help
```

### Architecture Patterns

**Modular Design**: Each tool is self-contained but leverages shared utilities
**Dynamic Discovery**: Launcher automatically discovers tools in `/tools` directory  
**Consistent Interfaces**: All tools follow same patterns for arguments, logging, error handling
**Configuration-Driven**: YAML configs for tool defaults and behavior
**Extensible**: Easy to add new functionality without breaking existing tools

## 📋 Configuration

### Environment Setup

```bash
# Python version
cat .python-version  # Shows required Python version (3.12)

# Project metadata
cat pyproject.toml   # Full project configuration

# Dependencies  
cat requirements.txt # Runtime dependencies
```

### Logging Configuration

```bash
# Debug level logging with file output
python cli.py input.xlsx --log-level DEBUG --log-file processing.log

# Tool-specific logging
python launcher.py --tool excel_flattener input.xlsx --verbose --log-file tool.log
```

### Output Configuration

```bash
# Save complete analysis artifacts
python cli.py input.xlsx --save-artifacts  # Creates analysis_output/ directory

# Custom output paths
python main.py input.xlsx -o /path/to/output.csv
```

## 🧪 Testing & Validation

### Sample Data
```bash
# Use provided sample data for testing
python launcher.py --tool guid_extractor sample.xlsx example_guid_mapping.csv

# Validate with different Excel formats
python cli.py sample.xlsx --include-empty --save-artifacts
```

### Error Handling
- Comprehensive validation for Excel file formats (.xlsx, .xlsm)
- Graceful handling of corrupted/protected workbooks
- Detailed error logging with stack traces
- User-friendly error messages for common issues

## 🔗 Integration Patterns

### Python API Usage
```python
from flattener import flatten_workbook
from tools.guid_extractor import extract_guid_data

# Flatten workbook
result = flatten_workbook("data.xlsx", include_empty_cells=False)

# Extract GUID data  
guid_result = extract_guid_data("frs102.xlsx", "mappings.csv")
```

### CLI Integration
```bash
# Pipeline processing
python cli.py input.xlsx --save-artifacts && \
python launcher.py --tool guid_extractor input.xlsx mappings.csv
```

### AI/LLM Integration
The flattened CSV output is specifically designed for LLM processing:
- Structured column format for easy parsing
- Cell metadata for understanding formulas and calculations
- Sheet identification for multi-document analysis
- Consistent data types for reliable processing

## 📚 Documentation Structure

- **README.md** (this file): Complete project overview
- **MIGRATION_GUIDE.md**: Migration from older versions
- **REFACTORING_SUMMARY.md**: Recent structural changes
- **IMPLEMENTATION_SUMMARY.md**: Technical implementation details
- **agents/README.md**: LangGraph agent development guide

## 🤝 Contributing

1. Follow the modular architecture patterns
2. Use shared utilities for common functionality
3. Include comprehensive error handling and logging
4. Add configuration files for new tools
5. Update documentation for new features
6. Test with sample data before committing

## 📄 License & Support

This project is part of the **Draftworx** development ecosystem for Excel analysis and AI automation.

**Support Channels**:
- Tool-specific help: `python launcher.py --tool <tool_name> --help`
- Verbose logging: `--verbose` flag for detailed output
- Error logs: Check log files for diagnostic information
- Documentation: Review relevant .md files in project root and subdirectories

**Requirements**:
- Python 3.12+
- Excel files in .xlsx or .xlsm format
- Sufficient disk space for output artifacts

---

*Generated for Claude Code integration - this README provides comprehensive context for understanding and working with the DXTEMPLATETOOLS project.*
