# GUID Formula Updater Tool

A tool for processing GUIDs from flattened financial data and updating them with FRS102 accounting standard classifications via OpenAI API calls.

## Overview

This tool converts the GUID extractor approach to work with flattened CSV files and integrates OpenAI API calls for FRS102 classification. It processes Column D formulas from accounting policies and provides automated classification using GPT-4o with web search capabilities.

## Features

- **CSV-based processing**: Works with flattened financial data in CSV format
- **Column D focus**: Specifically processes formulas in Column D (accounting policies)
- **OpenAI integration**: Uses GPT-4o model with web search for accurate FRS102 classification
- **Batch processing**: Handles multiple GUIDs efficiently with rate limiting
- **Named ranges support**: Includes knowledge base for common formula fields
- **Error handling**: Robust error handling with detailed reporting
- **Configurable instructions**: Customizable OpenAI prompts for different use cases

## Installation

1. Ensure you have the required dependencies:
```bash
pip install openai>=1.0.0 pandas>=2.0.0 PyYAML>=6.0.0
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Usage

### Basic Usage

```bash
python main.py guids.csv flattened_data.csv
```

### Advanced Usage

```bash
# Custom output path
python main.py guids.csv flattened_data.csv -o output.csv

# Custom instruction for OpenAI
python main.py guids.csv flattened_data.csv --instruction "Custom classification instruction"

# Verbose logging
python main.py guids.csv flattened_data.csv --verbose

# Custom config file
python main.py guids.csv flattened_data.csv --config custom_config.yaml
```

## Input Formats

### GUID List CSV
Simple format with just GUIDs:
```csv
GUID
00CAC489
12345678
87654321
```

Or with sheet names (legacy format):
```csv
GUID,SheetName
00CAC489,SoCI
12345678,PL
87654321,BS
```

### Flattened Data CSV
Must include these columns:
- `Sheet`: Sheet name where the GUID was found
- `RowNum`: Row number in the original sheet
- `ColRef`: Column reference (tool processes only 'D')
- `Formula Text`: The formula text to be classified
- `CellValue`: Current value of the cell
- `Value Type`: Type of the value (formula, string, etc.)

Example:
```csv
Sheet,RowNum,ColRef,Formula Text,CellValue,Value Type
Notes,63,D,The charity maintains three main classes of fund as required by the,string,string
Notes,65,D,Unrestricted funds are funds that are available for use at the discretion,string,string
```

## Output

The tool generates a CSV file with all original columns plus:
- `FRS102_Classification`: The FRS102 standard classification from OpenAI
- `Classification_Error`: Error details if classification failed

Example output:
```csv
Sheet,RowNum,ColRef,Formula Text,CellValue,Value Type,FRS102_Classification
Notes,63,D,Fund accounting,string,string,FRS102 Section 21.2 (Paragraph 21.2A)
Notes,65,D,Unrestricted funds are funds that are available...,string,string,FRS102 Section 21.3 (Paragraph 21.3A)
Notes,67,D,Designated funds are unrestricted funds...,string,string,General FS Verbage
```

## Configuration

The tool uses `config.yaml` for configuration. Key settings:

### OpenAI Settings
```yaml
openai:
  model: "gpt-4o"  # Model with web search capabilities
  temperature: 0.1  # Low temperature for consistent results
  max_tokens: 500
  timeout: 30
```

### Processing Settings
```yaml
batch_processing:
  batch_size: 10  # Number of API calls per batch
  delay_between_batches: 1  # Seconds between batches
```

### Named Ranges Knowledge Base
```yaml
named_ranges:
  CompanyName: "The name of the reporting company"
  ReportingDate: "The financial year end date"
  CharityRegNum: "Charity Registration Number"
```

## Default Instruction

The default OpenAI instruction is:
```
Review the accounting policy formula and assign the UK FRS102 accounting standard and paragraph reference that is applicable for that paragraph. 
If the paragraph is not specifically attributable to a certain standard, mark it as "General FS Verbage".
Return your response in this exact format: "FRS102 Section X.Y (Paragraph Z)" or "General FS Verbage".
```

## Error Handling

The tool includes comprehensive error handling:
- **API errors**: Continues processing other GUIDs if one fails
- **Missing data**: Handles missing columns gracefully
- **Rate limiting**: Built-in delays to respect OpenAI rate limits
- **Validation**: Checks input data format and requirements

## Examples

### Example 1: Basic Processing
```bash
python main.py example_guid_list_for_formulas.csv example_flattened_data.csv
```

### Example 2: Custom Classification
```bash
python main.py guids.csv flattened_data.csv \
  --instruction "Classify this accounting policy according to UK GAAP standards and provide specific section references"
```

### Example 3: Debugging
```bash
python main.py guids.csv flattened_data.csv --verbose --log-file debug.log
```

## Integration with Other Tools

This tool is designed to work in a pipeline:
1. **Excel Flattener**: Converts Excel workbooks to flattened CSV
2. **GUID Extractor**: Extracts specific data ranges (legacy)
3. **GUID Formula Updater**: This tool - classifies formulas with AI
4. **Analysis Tools**: Further processing of classified data

## Performance

- **Batch processing**: Processes 10 requests in parallel by default
- **Rate limiting**: 1-second delay between batches
- **Memory efficient**: Streams large CSV files
- **Configurable**: Adjust batch size based on your OpenAI plan

## Troubleshooting

### Common Issues

1. **Missing OpenAI API Key**
   ```
   Error: OPENAI_API_KEY environment variable is required
   ```
   Solution: Set your API key with `export OPENAI_API_KEY='your-key'`

2. **No Column D entries found**
   ```
   Validation errors: No rows found with ColRef = 'D'
   ```
   Solution: Check that your flattened data has entries with ColRef = 'D'

3. **Rate limit errors**
   ```
   OpenAI API Error: Rate limit exceeded
   ```
   Solution: Increase `delay_between_batches` in config or reduce `batch_size`

### Debug Mode
Enable verbose logging to see detailed processing information:
```bash
python main.py guids.csv flattened_data.csv --verbose
```

## Contributing

When extending this tool:
1. Update configuration in `config.yaml`
2. Add new named ranges to the knowledge base
3. Modify the OpenAI instruction for different classification schemes
4. Test with sample data before processing large datasets

## License

This tool is part of the Financial Tools Suite for FRS102 analysis.