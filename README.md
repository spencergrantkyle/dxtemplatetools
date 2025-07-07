# Excel Flattener

A Python tool to flatten Excel workbooks into CSV files, capturing detailed metadata for each cell. Useful for data analysis, LLM processing, and auditing spreadsheet content.

---

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Output Format](#output-format)
- [Development & Upgrades](#development--upgrades)
- [Contributing](#contributing)

---

## Features
- Flattens all sheets in an Excel workbook (.xlsx or .xlsm) into a single CSV file
- Captures:
  - Sheet name
  - Row and column reference
  - Formula text (if present)
  - Cell value
  - Value type (formula, number, string, bool, date, other)
- Outputs a summary after processing

## Requirements
- Python 3.12 (see `.python-version`)
- [pandas](https://pandas.pydata.org/) >= 2.0.0
- [openpyxl](https://openpyxl.readthedocs.io/) >= 3.1.0

All dependencies are listed in `pyproject.toml`.

## Installation
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd excelflattener
   ```
2. **(Recommended) Create a virtual environment:**
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # OR, if using PEP 621/pyproject.toml:
   pip install .
   ```

## Usage
Flatten an Excel workbook to a CSV file:

```bash
python main.py <input_file.xlsx> [-o output.csv]
```

- `<input_file.xlsx>`: Path to the Excel file to flatten (must be `.xlsx` or `.xlsm`)
- `-o, --output`: (Optional) Output CSV file path. If omitted, defaults to `<input_file>_flattened.csv` in the same directory.

**Example:**
```bash
python main.py data/my_workbook.xlsx
# Output: data/my_workbook_flattened.csv
```

**With custom output:**
```bash
python main.py data/my_workbook.xlsx -o output/flat.csv
```

After running, you will see a summary of processed cells, sheets, and value types.

## Output Format
The resulting CSV will have the following columns:
- `Sheet`: Name of the worksheet
- `RowNum`: Row number (1-based)
- `ColRef`: Excel-style column letter (e.g., A, B, C)
- `Formula Text of cell`: Formula string if present, else blank
- `CellValue`: The value of the cell (as stored in Excel)
- `Value Type`: One of `formula`, `number`, `string`, `bool`, `date`, or `other`

## Development & Upgrades

### For Future Developers & AI Agents
- **Code Structure:**
  - Main logic is in `main.py`.
  - The `flatten_excel_workbook` function handles the flattening and metadata extraction.
  - Command-line interface is provided via `argparse` in the `main()` function.
- **Adding Features:**
  - To add new metadata columns, modify the dictionary in the `all_data.append({...})` section.
  - To support new file types, update the input validation logic in `main()`.
  - For performance improvements, consider chunked processing or parallelization for very large files.
- **Testing:**
  - Add test Excel files and compare output CSVs for regression testing.
  - Consider adding unit tests for the flattening logic.
- **Dependencies:**
  - Update `pyproject.toml` for new dependencies.
  - Pin versions as needed for reproducibility.
- **Python Version:**
  - The project is pinned to Python 3.12. Update `.python-version` and `pyproject.toml` if upgrading.
- **Error Handling:**
  - All errors are printed to the console. For production, consider raising exceptions or logging.
- **AI Agent Guidance:**
  - Always check for changes in the Excel file format or requirements before making upgrades.
  - Document any new features or breaking changes in this README.

## Contributing
Pull requests and suggestions are welcome! Please:
- Follow PEP8 style guidelines
- Document new features and changes
- Update this README as needed

---

© 2024 excelflattener contributors
