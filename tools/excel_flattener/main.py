"""
Excel Flattener Tool - Main entry point.

Flattens Excel workbooks into structured CSV data with metadata for each cell.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.excel_io import load_excel_workbook, save_to_csv, get_column_headers
from shared.logger import setup_logging, get_logger
from shared.file_utils import validate_excel_file, generate_output_filename

# Handle relative imports for both direct execution and module usage
try:
    from .utils import FlattenResult, flatten_workbook_to_dataframe, print_summary
except ImportError:
    from utils import FlattenResult, flatten_workbook_to_dataframe, print_summary

logger = get_logger(__name__)


def flatten_excel_workbook(input_path: str, output_path: Optional[str] = None, include_empty_cells: bool = False) -> FlattenResult:
    """
    Flatten an Excel workbook into a DataFrame with metadata for each cell.
    
    Args:
        input_path (str): Path to the Excel workbook
        output_path (str, optional): Output CSV path. If None, auto-generated.
        include_empty_cells (bool): Whether to include empty cells in output
        
    Returns:
        FlattenResult: Object containing flattened data and metadata
    """
    logger.info(f"Starting Excel flattening: {input_path}")
    
    # Validate input
    validate_excel_file(input_path)
    
    # Generate output path if not provided
    if output_path is None:
        output_path = generate_output_filename(input_path, "_flattened")
    
    # Load and flatten workbook
    result = flatten_workbook_to_dataframe(input_path, include_empty_cells)
    
    # Save to CSV
    save_to_csv(result.dataframe, output_path)
    result.output_path = output_path
    
    logger.info(f"Successfully flattened {result.total_cells} cells to: {output_path}")
    return result


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Flatten Excel workbook into a flat CSV file for LLM processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py input.xlsx                    # Basic flattening
  python main.py input.xlsx -o output.csv      # Custom output path
  python main.py input.xlsx --include-empty    # Include empty cells
  python main.py input.xlsx --verbose          # Verbose logging
        """
    )
    
    parser.add_argument('input_file', help='Path to the Excel workbook (.xlsx/.xlsm)')
    parser.add_argument('-o', '--output', help='Output CSV file path (default: auto-generated)')
    parser.add_argument('--include-empty', action='store_true', 
                       help='Include empty cells in the output')
    parser.add_argument('--verbose', action='store_true', 
                       help='Enable verbose logging')
    parser.add_argument('--log-file', help='Log to file instead of console')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level, log_file=args.log_file)
    
    try:
        # Flatten the workbook
        result = flatten_excel_workbook(
            input_path=args.input_file,
            output_path=args.output,
            include_empty_cells=args.include_empty
        )
        
        # Print summary
        print_summary(result)
        
        print(f"\n✅ Success! Flattened data saved to: {result.output_path}")
        
    except Exception as e:
        logger.error(f"Failed to flatten Excel file: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()