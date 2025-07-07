"""
GUID Extractor Tool - Utility functions and data structures.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.excel_io import find_guid_in_column_a, extract_row_data, get_column_headers
from shared.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GuidExtractionResult:
    """Result object containing GUID extraction data and metadata."""
    dataframe: pd.DataFrame
    rows_extracted: int
    guids_processed: int
    guids_found: int
    guids_not_found: List[str]
    sheets_processed: List[str]
    column_range: str
    input_path: str
    output_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization."""
        return {
            "rows_extracted": self.rows_extracted,
            "guids_processed": self.guids_processed,
            "guids_found": self.guids_found,
            "guids_not_found": self.guids_not_found,
            "sheets_processed": self.sheets_processed,
            "column_range": self.column_range,
            "input_path": self.input_path,
            "output_path": self.output_path
        }


def process_guid_mappings(
    workbook,
    guid_mappings: List[Dict[str, str]],
    start_col: int = 124,
    end_col: int = 200,
    output_path: Optional[str] = None
) -> GuidExtractionResult:
    """
    Process GUID mappings and extract data from the workbook.
    
    Args:
        workbook: openpyxl workbook object
        guid_mappings: List of dicts with 'guid' and 'sheet_name' keys
        start_col: Starting column index for extraction
        end_col: Ending column index for extraction
        output_path: Optional output path for tracking
        
    Returns:
        GuidExtractionResult: Object containing extracted data and metadata
    """
    logger.info(f"Processing {len(guid_mappings)} GUID mappings")
    
    all_data = []
    guids_not_found = []
    sheets_processed = set()
    guids_found = 0
    
    # Generate column headers
    column_headers = get_column_headers(start_col, end_col)
    
    for mapping in guid_mappings:
        guid = mapping['guid']
        sheet_name = mapping['sheet_name']
        
        logger.debug(f"Processing GUID {guid} in sheet {sheet_name}")
        
        try:
            # Check if sheet exists
            if sheet_name not in workbook.sheetnames:
                logger.warning(f"Sheet '{sheet_name}' not found in workbook for GUID {guid}")
                guids_not_found.append(guid)
                continue
            
            # Get the worksheet
            worksheet = workbook[sheet_name]
            sheets_processed.add(sheet_name)
            
            # Find GUID in column A
            row_num = find_guid_in_column_a(worksheet, guid)
            
            if row_num is None:
                logger.warning(f"GUID {guid} not found in column A of sheet {sheet_name}")
                guids_not_found.append(guid)
                continue
            
            # Extract data from the specified columns
            row_data = extract_row_data(worksheet, row_num, start_col, end_col)
            
            # Create data row with metadata
            data_row = {
                'SheetName': sheet_name,
                'GUID': guid,
                'RowNum': row_num
            }
            
            # Add extracted column data
            for i, value in enumerate(row_data):
                col_header = column_headers[i]
                data_row[col_header] = value
            
            all_data.append(data_row)
            guids_found += 1
            
            logger.debug(f"Successfully extracted data for GUID {guid} from row {row_num}")
            
        except Exception as e:
            logger.error(f"Error processing GUID {guid} in sheet {sheet_name}: {e}")
            guids_not_found.append(guid)
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Create result object
    result = GuidExtractionResult(
        dataframe=df,
        rows_extracted=len(df),
        guids_processed=len(guid_mappings),
        guids_found=guids_found,
        guids_not_found=guids_not_found,
        sheets_processed=list(sheets_processed),
        column_range=f"{start_col}-{end_col}",
        input_path="", # Will be set by caller
        output_path=output_path
    )
    
    logger.info(f"Extraction complete: {guids_found}/{len(guid_mappings)} GUIDs found")
    return result


def print_extraction_summary(result: GuidExtractionResult) -> None:
    """Print a formatted summary of the extraction result."""
    print(f"\n🔍 GUID Extraction Summary:")
    print(f"   📁 Input file: {result.input_path}")
    print(f"   📋 GUIDs processed: {result.guids_processed}")
    print(f"   ✅ GUIDs found: {result.guids_found}")
    print(f"   ❌ GUIDs not found: {len(result.guids_not_found)}")
    print(f"   📄 Sheets processed: {len(result.sheets_processed)}")
    print(f"   📊 Rows extracted: {result.rows_extracted}")
    print(f"   📏 Column range: {result.column_range}")
    
    if result.guids_not_found:
        print(f"\n⚠️  GUIDs not found:")
        for guid in result.guids_not_found[:10]:  # Show first 10
            print(f"      • {guid}")
        if len(result.guids_not_found) > 10:
            print(f"      ... and {len(result.guids_not_found) - 10} more")
    
    if result.sheets_processed:
        print(f"\n📄 Sheets processed:")
        for sheet in result.sheets_processed:
            print(f"      • {sheet}")


def create_guid_mapping_template(output_path: str = "guid_mapping_template.csv") -> str:
    """
    Create a template CSV file for GUID mappings.
    
    Args:
        output_path: Path for the template file
        
    Returns:
        str: Path to created template
    """
    template_data = {
        'GUID': ['00CAC489', '12345678', '87654321'],
        'SheetName': ['SoCI', 'PL', 'BS']
    }
    
    df = pd.DataFrame(template_data)
    df.to_csv(output_path, index=False)
    
    logger.info(f"Created GUID mapping template: {output_path}")
    return output_path


def validate_guid_mappings(guid_mappings: List[Dict[str, str]]) -> List[str]:
    """
    Validate GUID mappings for common issues.
    
    Args:
        guid_mappings: List of GUID mapping dictionaries
        
    Returns:
        List[str]: List of validation warnings/errors
    """
    warnings = []
    
    # Check for duplicate GUIDs
    guids = [mapping['guid'] for mapping in guid_mappings]
    duplicates = set([guid for guid in guids if guids.count(guid) > 1])
    if duplicates:
        warnings.append(f"Duplicate GUIDs found: {', '.join(duplicates)}")
    
    # Check GUID format (should be 8 characters)
    for mapping in guid_mappings:
        guid = mapping['guid']
        if len(guid) != 8:
            warnings.append(f"GUID '{guid}' is not 8 characters long")
    
    # Check for empty sheet names
    empty_sheets = [mapping['guid'] for mapping in guid_mappings if not mapping['sheet_name'].strip()]
    if empty_sheets:
        warnings.append(f"Empty sheet names for GUIDs: {', '.join(empty_sheets)}")
    
    return warnings