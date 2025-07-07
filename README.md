# Excel Flattener

A modular Python tool for flattening Excel workbooks into structured data, designed for AI agent integration and automated analysis workflows.

## ✨ Features

### Core Functionality
- **Modular Design**: Clean, callable API perfect for AI agent integration
- **Comprehensive Flattening**: Extracts all cell data including formulas, values, and metadata
- **Robust Error Handling**: Safe processing of large and complex financial spreadsheets
- **Multiple Output Formats**: CSV export with optional analysis artifacts
- **Logging & Traceability**: Full audit trail of processing runs

### AI Agent Ready
- **Headless Operation**: No CLI prompts or UI dependencies
- **Structured Data Output**: Clean DataFrame format for LLM processing
- **Analysis Preview Generation**: Formatted summaries for AI analysis
- **Instruction Processing**: Designed to work with LangChain/LangGraph workflows
- **Artifact Management**: Automatic saving of analysis outputs and metadata

---

## 🏗️ Architecture

```
excelflattener/
│
├── flattener/                   # Core module
│   ├── __init__.py             # Public API exports
│   ├── flattener.py            # Main flattening logic
│   └── utils.py                # Logging, formatting, artifacts
│
├── cli.py                      # Command-line interface
├── agent_example.py            # AI agent integration example
├── main.py                     # Legacy CLI (deprecated)
├── requirements.txt            # Dependencies
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

---

## 🚀 Installation

### Option 1: Editable Install (Recommended for development)
```bash
git clone <repository-url>
cd excelflattener
pip install -e .
```

### Option 2: From Requirements
```bash
pip install -r requirements.txt
```

### Option 3: With AI Dependencies
```bash
pip install -e ".[ai]"  # Includes LangChain components
```

---

## 📖 Usage

### As a Python Module (Recommended)

```python
from flattener import flatten_workbook, setup_logging

# Set up logging
setup_logging(level="INFO")

# Flatten an Excel file
result = flatten_workbook("financial_model.xlsx")

# Access the data
print(f"Processed {result.total_cells} cells from {result.sheets_processed} sheets")
df = result.dataframe

# Save to CSV
from flattener.flattener import save_flattened_data
output_path = save_flattened_data(result, "output.csv")
```

### With AI Agent Integration

```python
from flattener import flatten_workbook, log_run_to_file
from flattener.utils import create_analysis_preview, save_analysis_artifacts

@log_run_to_file("ExcelAnalysis")
def analyze_spreadsheet(file_path: str):
    # Flatten the workbook
    result = flatten_workbook(file_path)
    
    # Create AI-ready preview
    preview = create_analysis_preview(result, max_rows=20)
    
    # Send to your LLM agent for analysis
    # instructions = your_langchain_agent.analyze(preview)
    
    # Save all artifacts
    artifacts = save_analysis_artifacts(result)
    return result, artifacts

# Use in your AI workflow
result, artifacts = analyze_spreadsheet("client_financials.xlsx")
```

### Command Line Interface

```bash
# Basic usage
python cli.py input_file.xlsx

# With options
python cli.py input_file.xlsx --output custom_output.csv --include-empty --save-artifacts

# Legacy CLI (deprecated but still works)
python main.py input_file.xlsx
```

### Command Line Options

- `--output, -o`: Custom output CSV path
- `--include-empty`: Include empty cells in output
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `--log-file`: Save logs to file
- `--save-artifacts`: Save all analysis artifacts (CSV, metadata, preview)

---

## 📊 Output Format

The flattened data contains these columns:

| Column | Description |
|--------|-------------|
| `Sheet` | Worksheet name |
| `RowNum` | Row number (1-based) |
| `ColRef` | Excel column reference (A, B, C, etc.) |
| `Formula Text` | Formula string (if cell contains formula) |
| `CellValue` | Cell value |
| `Value Type` | Data type: formula, number, string, bool, date, other |

---

## 🤖 AI Agent Integration

### LangChain/LangGraph Example

```python
from flattener import flatten_workbook
from flattener.utils import create_analysis_preview

def excel_analysis_agent(file_path: str) -> dict:
    """
    Complete AI workflow for Excel analysis.
    """
    # Step 1: Flatten Excel
    result = flatten_workbook(file_path)
    
    # Step 2: Create LLM-ready preview
    preview = create_analysis_preview(result)
    
    # Step 3: Your LangChain agent processes the preview
    # agent_response = your_langchain_chain.invoke({
    #     "excel_data": preview,
    #     "task": "analyze_financial_model"
    # })
    
    return {
        "flatten_result": result,
        "preview": preview,
        # "ai_analysis": agent_response
    }
```

### Instruction Format for AI Agents

The tool is designed to work with structured instructions from LLMs:

```json
[
  {
    "action": "flag_inconsistency",
    "sheet": "Income Statement", 
    "issue": "Potential typo in header",
    "description": "Found 'Revnue' which might be 'Revenue'",
    "suggested_fix": "rename_header",
    "confidence": 0.9
  }
]
```

---

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone and install with dev dependencies
git clone <repository-url>
cd excelflattener
pip install -e ".[dev]"

# Run formatting
black .
isort .

# Run type checking
mypy flattener/
```

### Adding New Features

1. **Core Logic**: Add to `flattener/flattener.py`
2. **Utilities**: Add to `flattener/utils.py` 
3. **AI Integration**: Update `agent_example.py`
4. **CLI Options**: Update `cli.py`

### Testing

```bash
# Run example workflow
python agent_example.py

# Test CLI
python cli.py test_file.xlsx --save-artifacts
```

---

## 📁 Analysis Artifacts

When using `--save-artifacts` or the programmatic equivalent, the tool generates:

- `{filename}_flattened.csv`: Raw flattened data
- `{filename}_metadata.json`: Processing metadata
- `{filename}_preview.txt`: Human-readable preview
- `{filename}_ai_instructions.json`: AI-generated instructions (if applicable)
- `{filename}_suggestions.txt`: Human-readable suggestions (if applicable)

---

## 🔧 Configuration

### Logging Configuration

```python
from flattener import setup_logging

# Console only
setup_logging(level="INFO")

# With file output
setup_logging(level="DEBUG", log_file="excel_processing.log")
```

### Custom Output Directories

```python
from flattener.utils import save_analysis_artifacts

# Save to custom directory
artifacts = save_analysis_artifacts(result, output_dir="my_analysis")
```

---

## 🚀 Integration with Draftworx AI Agent

This tool is designed to integrate seamlessly with the Draftworx AI Agent architecture:

1. **n8n Workflows**: Call via Python subprocess or HTTP API
2. **LangGraph Agents**: Use as a tool in your agent workflow
3. **Notion Integration**: Auto-generate documentation using the analysis artifacts
4. **Dev CLI**: Add as a subcommand in your Draftworx development toolkit

### Example n8n Integration

```javascript
// n8n Python node
const { flatten_workbook } = require('./flattener');

const result = flatten_workbook(inputFile);
return {
  flattenedData: result.dataframe,
  metadata: result.to_dict(),
  cellCount: result.total_cells
};
```

---

## 📚 Migration from v0.1.x

If you're upgrading from the original `main.py` implementation:

```python
# Old way
from main import flatten_excel_workbook
df = flatten_excel_workbook("file.xlsx")

# New way  
from flattener import flatten_workbook
result = flatten_workbook("file.xlsx")
df = result.dataframe
```

The output DataFrame structure remains the same, but you now get additional metadata and capabilities.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the existing code style
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🏷️ Version History

- **v0.2.0**: Modular architecture, AI agent integration, enhanced logging
- **v0.1.0**: Initial CLI implementation

---

*Built for the Draftworx AI Agent ecosystem 🤖*
