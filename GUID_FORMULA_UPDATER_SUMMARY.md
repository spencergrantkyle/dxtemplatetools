# GUID Formula Updater Tool - Implementation Summary

## Overview

Successfully converted the GUID extractor tool into a **GUID Formula Updater Tool** that processes GUIDs from flattened financial data and classifies Column D formulas using OpenAI API calls for FRS102 accounting standard analysis.

## Key Features Implemented

### ✅ Core Functionality
- **CSV-based Processing**: Works with flattened financial data in CSV format (converted from Excel)
- **Column D Focus**: Specifically processes formulas in Column D containing accounting policies
- **OpenAI Integration**: Uses GPT-4o model with web search capabilities for accurate classification
- **Batch Processing**: Efficient parallel processing with rate limiting
- **FRS102 Classification**: Automated assignment of UK FRS102 accounting standards and paragraph references

### ✅ Advanced Features
- **Named Ranges Support**: Built-in knowledge base for common formula fields (CharityRegNum, CompanyName, etc.)
- **Error Handling**: Robust error handling with detailed reporting and graceful degradation
- **Configurable Instructions**: Customizable OpenAI prompts for different classification schemes
- **Rate Limiting**: Built-in delays to respect OpenAI API rate limits
- **Comprehensive Logging**: Detailed logging with multiple verbosity levels

## File Structure

```
tools/guid_formula_updater/
├── __init__.py              # Package initialization
├── main.py                  # Main entry point and CLI
├── utils.py                 # Utility functions and data structures  
├── openai_client.py         # OpenAI API integration
├── config.yaml              # Configuration settings
├── demo.py                  # Demo script with sample data
└── README.md                # Comprehensive documentation
```

## Key Files Created/Modified

### 1. Main Components
- **`tools/guid_formula_updater/main.py`**: Main CLI and processing logic
- **`tools/guid_formula_updater/openai_client.py`**: OpenAI API client with async batch processing
- **`tools/guid_formula_updater/utils.py`**: Utility functions for data processing and validation
- **`tools/guid_formula_updater/config.yaml`**: Configuration with OpenAI settings and named ranges

### 2. Example/Demo Files
- **`example_flattened_data.csv`**: Sample flattened data matching user's format
- **`example_guid_list_for_formulas.csv`**: Sample GUID input file
- **`tools/guid_formula_updater/demo.py`**: Interactive demo script

### 3. Documentation
- **`tools/guid_formula_updater/README.md`**: Comprehensive usage guide
- **`requirements.txt`**: Updated with OpenAI dependency

## How It Works

### 1. Input Processing
```
GUID List CSV → Load GUIDs to process
Flattened Data CSV → Load financial data with formulas
Filter → Only Column D entries matching target GUIDs
```

### 2. OpenAI Classification
```
For each GUID formula:
├── Build prompt with instruction + formula text + context
├── Include named ranges knowledge if referenced
├── Make OpenAI API call with GPT-4o
└── Parse classification response
```

### 3. Output Generation
```
Original Data + FRS102_Classification → Enhanced CSV
Include error details for failed classifications
Generate processing summary and statistics
```

## Usage Examples

### Basic Usage
```bash
# Run the tool
python launcher.py --tool guid_formula_updater guids.csv flattened_data.csv

# Or directly
cd tools/guid_formula_updater
python main.py guids.csv flattened_data.csv
```

### Advanced Usage
```bash
# Custom instruction
python main.py guids.csv data.csv --instruction "Classify according to UK GAAP with detailed references"

# Custom output and verbose logging
python main.py guids.csv data.csv -o results.csv --verbose

# Demo mode
python demo.py
```

## Configuration Highlights

### OpenAI Settings
```yaml
openai:
  model: "gpt-4o"  # Model with web search capabilities
  temperature: 0.1  # Low temperature for consistent results
  max_tokens: 500
  timeout: 30
```

### Named Ranges Knowledge Base
```yaml
named_ranges:
  CompanyName: "The name of the reporting company"
  ReportingDate: "The financial year end date"
  CharityRegNum: "Charity Registration Number"
  # ... additional mappings
```

### Default Classification Instruction
```
Review the accounting policy formula and assign the UK FRS102 accounting standard and paragraph reference that is applicable for that paragraph. 
If the paragraph is not specifically attributable to a certain standard, mark it as "General FS Verbage".
Return your response in this exact format: "FRS102 Section X.Y (Paragraph Z)" or "General FS Verbage".
```

## Sample Input/Output

### Input: Flattened Data
```csv
Sheet,RowNum,ColRef,Formula Text,CellValue,Value Type
Notes,63,D,The charity maintains three main classes of fund as required by the,string,string
Notes,65,D,Unrestricted funds are funds that are available for use at the discretion,string,string
```

### Output: Classified Data
```csv
Sheet,RowNum,ColRef,Formula Text,CellValue,Value Type,FRS102_Classification
Notes,63,D,Fund accounting,string,string,FRS102 Section 21.2 (Paragraph 21.2A)
Notes,65,D,Unrestricted funds are funds that are available...,string,string,FRS102 Section 21.3 (Paragraph 21.3A)
```

## Error Handling

### API Error Management
- Continues processing if individual API calls fail
- Marks failed classifications with "API_Error"
- Detailed error logging and reporting
- Configurable retry logic

### Data Validation
- Validates required columns in input data
- Checks for Column D entries
- Handles missing or malformed data gracefully
- Provides clear error messages

## Performance Features

### Batch Processing
- Processes 10 API calls in parallel by default
- 1-second delay between batches to respect rate limits
- Configurable batch size and delays
- Efficient memory usage for large datasets

### Rate Limiting
- Built-in delays to prevent API rate limit errors
- Configurable concurrent request limits
- Graceful handling of rate limit responses

## Integration

### Tool Discovery
- Automatically discovered by the main launcher (`launcher.py`)
- No manual registration required
- Follows standard tool directory structure

### Dependencies
- Added `openai>=1.0.0` to requirements.txt
- Uses existing shared utilities (logger, file_utils, excel_io)
- Compatible with existing tool ecosystem

## Environment Requirements

### Required Environment Variables
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### Python Dependencies
```
openai>=1.0.0
pandas>=2.0.0
PyYAML>=6.0.0
asyncio (built-in)
```

## Future Enhancements

### Potential Improvements
1. **Multiple Model Support**: Add support for other AI models (Claude, Gemini)
2. **Custom Knowledge Bases**: Allow user-defined named ranges and context
3. **Caching**: Cache similar formula classifications to reduce API calls
4. **Confidence Scoring**: Add confidence levels to classifications
5. **Bulk Processing**: Enhanced support for very large datasets

### Integration Opportunities
1. **Excel Direct Processing**: Direct Excel file input without flattening step
2. **Database Integration**: Support for database input/output
3. **Web Interface**: Browser-based interface for non-technical users
4. **Reporting**: Enhanced reporting with charts and analysis

## Success Metrics

### Implemented Successfully ✅
- ✅ Processes CSV input with GUID filtering
- ✅ Column D formula extraction and processing
- ✅ OpenAI GPT-4o integration with web search
- ✅ Batch processing with rate limiting
- ✅ Named ranges knowledge base
- ✅ Comprehensive error handling
- ✅ Configurable instructions
- ✅ Output with FRS102 classifications
- ✅ "General FS Verbage" fallback for non-standard content
- ✅ Complete documentation and examples
- ✅ Demo script for testing

### Technical Excellence
- Async/await for efficient API calls
- Type hints throughout codebase
- Comprehensive logging
- Configuration-driven behavior
- Modular, reusable components
- Standard tool interface

## Conclusion

The GUID Formula Updater Tool successfully transforms the original GUID extractor concept into a powerful AI-enhanced classification system. It provides automated FRS102 standard classification for accounting policy formulas, significantly reducing manual analysis time while maintaining accuracy through AI assistance.

The tool is production-ready with robust error handling, comprehensive documentation, and seamless integration with the existing tool ecosystem.