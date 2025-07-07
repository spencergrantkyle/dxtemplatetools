"""
GUID Extractor Tool - Main entry point.

Extracts data from specific Excel rows based on GUID mappings and sheet targeting.
Uses GUIDs as unique row identifiers to extract columns 124-200 from FRS102 workbooks.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.excel_io import load_excel_workbook, save_to_csv, find_guid_in_column_a, extract_row_data, get_column_headers
from shared.logger import setup_logging, get_logger
from shared.file_utils import validate_excel_file, generate_output_filename, read_guid_mapping_csv

# Handle relative imports for both direct execution and module usage
try:
    from .utils import GuidExtractionResult, process_guid_mappings, print_extraction_summary
except ImportError:
    from utils import GuidExtractionResult, process_guid_mappings, print_extraction_summary

logger = get_logger(__name__)


def extract_guid_data(
    frs_workbook_path: str,
    guid_mapping_path: str,
    output_path: Optional[str] = None,
    start_col: int = 124,
    end_col: int = 200
) -> GuidExtractionResult:
    """
    Extract data from Excel rows based on GUID mappings.
    
    Args:
        frs_workbook_path (str): Path to the FRS102 Excel workbook
        guid_mapping_path (str): Path to CSV file with GUID,SheetName mappings
        output_path (str, optional): Output CSV path. If None, auto-generated.
        start_col (int): Starting column index for data extraction (default: 124)
        end_col (int): Ending column index for data extraction (default: 200)
        
    Returns:
        GuidExtractionResult: Object containing extracted data and metadata
    """
    logger.info(f"Starting GUID extraction from: {frs_workbook_path}")
    logger.info(f"Using GUID mappings from: {guid_mapping_path}")
    logger.info(f"Extracting columns {start_col}-{end_col}")
    
    # Validate inputs
    validate_excel_file(frs_workbook_path)
    guid_mappings = read_guid_mapping_csv(guid_mapping_path)
    
    # Generate output path if not provided
    if output_path is None:
        output_path = generate_output_filename(frs_workbook_path, "_guid_extracted")
    
    # Load the FRS workbook
    logger.info("Loading FRS workbook...")
    wb = load_excel_workbook(frs_workbook_path, data_only=True)
    
    # Process GUID mappings and extract data
    result = process_guid_mappings(
        workbook=wb,
        guid_mappings=guid_mappings,
        start_col=start_col,
        end_col=end_col,
        output_path=output_path
    )
    
    # Save results to CSV
    save_to_csv(result.dataframe, output_path)
    result.output_path = output_path
    
    logger.info(f"Successfully extracted {result.rows_extracted} rows to: {output_path}")
    return result


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Extract data from Excel rows using GUID mappings for FRS102 analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py frs102.xlsx guids.csv                    # Basic extraction (cols 124-200)
  python main.py frs102.xlsx guids.csv -o output.csv      # Custom output path
  python main.py frs102.xlsx guids.csv --start-col 100 --end-col 150  # Custom column range
  python main.py frs102.xlsx guids.csv --verbose          # Verbose logging

GUID Mapping CSV Format:
  GUID,SheetName
  00CAC489,SoCI
  12345678,PL
  ...

The tool will:
1. Read GUID mappings from CSV
2. For each GUID, find it in column A of the specified sheet
3. Extract data from columns 124-200 (or custom range) of that row
4. Consolidate all results into a single CSV output
        """
    )
    
    parser.add_argument('frs_workbook', help='Path to the FRS102 Excel workbook (.xlsx/.xlsm)')
    parser.add_argument('guid_mapping', help='Path to CSV file with GUID,SheetName mappings')
    parser.add_argument('-o', '--output', help='Output CSV file path (default: auto-generated)')
    parser.add_argument('--start-col', type=int, default=124, 
                       help='Starting column index for data extraction (default: 124)')
    parser.add_argument('--end-col', type=int, default=200, 
                       help='Ending column index for data extraction (default: 200)')
    parser.add_argument('--verbose', action='store_true', 
                       help='Enable verbose logging')
    parser.add_argument('--log-file', help='Log to file instead of console')
    
    args = parser.parse_args()
    
    # Validate column range
    if args.start_col >= args.end_col:
        print("❌ Error: start-col must be less than end-col")
        sys.exit(1)
    
    if args.start_col < 1 or args.end_col < 1:
        print("❌ Error: Column indices must be positive")
        sys.exit(1)
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level, log_file=args.log_file)
    
    try:
        # Extract GUID data
        result = extract_guid_data(
            frs_workbook_path=args.frs_workbook,
            guid_mapping_path=args.guid_mapping,
            output_path=args.output,
            start_col=args.start_col,
            end_col=args.end_col
        )
        
        # Print summary
        print_extraction_summary(result)
        
        print(f"\n✅ Success! GUID extraction completed: {result.output_path}")
        
    except Exception as e:
        logger.error(f"Failed to extract GUID data: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()