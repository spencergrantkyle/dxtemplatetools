"""
GUID Formula Updater Tool - Main entry point.

Processes GUIDs from CSV input, finds them in flattened financial data,
and classifies their Column D formulas using OpenAI API calls.
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.excel_io import save_to_csv
from shared.logger import setup_logging, get_logger
from shared.file_utils import read_guid_mapping_csv

# Handle relative imports for both direct execution and module usage
try:
    from .utils import (
        GuidFormulaResult, load_config, load_flattened_data, 
        validate_flattened_data, filter_guid_data, prepare_classification_data,
        merge_results_with_original, print_processing_summary
    )
    from .openai_client import OpenAIFormulaClassifier, create_classification_request
except ImportError:
    from utils import (
        GuidFormulaResult, load_config, load_flattened_data,
        validate_flattened_data, filter_guid_data, prepare_classification_data,
        merge_results_with_original, print_processing_summary
    )
    from openai_client import OpenAIFormulaClassifier, create_classification_request

logger = get_logger(__name__)


def load_guid_list(guid_file_path: str) -> List[str]:
    """
    Load list of GUIDs from CSV file.
    
    Args:
        guid_file_path: Path to CSV file containing GUIDs
        
    Returns:
        List[str]: List of GUIDs to process
    """
    try:
        # Try to load as simple CSV with GUID column
        import pandas as pd
        df = pd.read_csv(guid_file_path)
        
        if 'GUID' in df.columns:
            guids = df['GUID'].astype(str).tolist()
        elif len(df.columns) == 1:
            # Single column, assume it's GUIDs
            guids = df.iloc[:, 0].astype(str).tolist()
        else:
            # Try the guid mapping format (GUID, SheetName)
            guid_mappings = read_guid_mapping_csv(guid_file_path)
            guids = [mapping['guid'] for mapping in guid_mappings]
        
        logger.info(f"Loaded {len(guids)} GUIDs from {guid_file_path}")
        return guids
        
    except Exception as e:
        logger.error(f"Error loading GUID file {guid_file_path}: {e}")
        raise


async def process_guid_formulas(
    guid_file_path: str,
    flattened_file_path: str,
    output_path: Optional[str] = None,
    instruction: Optional[str] = None,
    config_path: Optional[str] = None
) -> GuidFormulaResult:
    """
    Process GUID formulas and classify them using OpenAI API.
    
    Args:
        guid_file_path: Path to CSV file with GUIDs to process
        flattened_file_path: Path to flattened financial data CSV
        output_path: Output CSV path. If None, auto-generated.
        instruction: Custom instruction for OpenAI. If None, uses default.
        config_path: Path to config file. If None, uses default.
        
    Returns:
        GuidFormulaResult: Object containing processing results and metadata
    """
    logger.info(f"Starting GUID formula processing")
    logger.info(f"GUID file: {guid_file_path}")
    logger.info(f"Flattened file: {flattened_file_path}")
    
    # Load configuration
    config = load_config(Path(config_path) if config_path else None)
    
    # Load GUID list
    guid_list = load_guid_list(guid_file_path)
    
    # Load flattened data
    flattened_df = load_flattened_data(flattened_file_path)
    
    # Validate flattened data
    validation_errors = validate_flattened_data(flattened_df, config)
    if validation_errors:
        error_msg = f"Validation errors: {'; '.join(validation_errors)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Filter data for target GUIDs in Column D
    filtered_df = filter_guid_data(flattened_df, guid_list, config)
    
    # Prepare data for classification
    classification_records = prepare_classification_data(filtered_df, config)
    
    if not classification_records:
        logger.warning("No records found for classification")
        return GuidFormulaResult(
            dataframe=filtered_df,
            guids_processed=len(guid_list),
            guids_found=0,
            guids_classified=0,
            api_calls_made=0,
            guids_not_found=guid_list,
            classification_errors=[],
            input_path=guid_file_path,
            flattened_file_path=flattened_file_path
        )
    
    # Initialize OpenAI classifier
    classifier = OpenAIFormulaClassifier(config_path)
    
    # Use custom instruction or default
    final_instruction = instruction or config["default_instruction"]
    named_ranges = config["named_ranges"]
    
    # Create classification requests
    requests = []
    for record in classification_records:
        request = create_classification_request(
            guid=record["guid"],
            sheet=record["sheet"],
            row_num=record["row_num"],
            formula_text=record["formula_text"],
            cell_value=record["cell_value"],
            instruction=final_instruction,
            named_ranges=named_ranges
        )
        requests.append(request)
    
    logger.info(f"Making {len(requests)} OpenAI API calls for classification")
    
    # Process classifications in batches
    classification_results = await classifier.classify_formulas_batch(requests)
    
    # Merge results with original data
    output_df = merge_results_with_original(
        classification_records, 
        classification_results, 
        config
    )
    
    # Calculate result statistics
    guids_found = len(set(record["guid"] for record in classification_records))
    guids_not_found = [guid for guid in guid_list if guid not in set(record["guid"] for record in classification_records)]
    
    classification_errors = []
    successful_classifications = 0
    for result in classification_results:
        if result.error:
            classification_errors.append(f"GUID {result.guid}: {result.error}")
        else:
            successful_classifications += 1
    
    # Generate output path if not provided
    if output_path is None:
        base_name = Path(guid_file_path).stem
        output_path = f"{base_name}_classified_formulas.csv"
    
    # Save results to CSV
    save_to_csv(output_df, output_path)
    
    # Create result object
    result = GuidFormulaResult(
        dataframe=output_df,
        guids_processed=len(guid_list),
        guids_found=guids_found,
        guids_classified=successful_classifications,
        api_calls_made=len(requests),
        guids_not_found=guids_not_found,
        classification_errors=classification_errors,
        input_path=guid_file_path,
        output_path=output_path,
        flattened_file_path=flattened_file_path
    )
    
    logger.info(f"Successfully processed {successful_classifications} classifications")
    return result


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Process GUIDs and classify their formulas using OpenAI API for FRS102 analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py guids.csv flattened_data.csv                     # Basic processing
  python main.py guids.csv flattened_data.csv -o output.csv       # Custom output path
  python main.py guids.csv flattened_data.csv --instruction "Custom instruction for OpenAI"
  python main.py guids.csv flattened_data.csv --verbose           # Verbose logging

GUID Input CSV Format:
  GUID
  00CAC489
  12345678
  ...

OR (with sheet names):
  GUID,SheetName
  00CAC489,SoCI
  12345678,PL
  ...

Flattened Data CSV Format:
  Must include columns: Sheet, RowNum, ColRef, Formula Text, CellValue
  Tool will process only rows where ColRef = 'D'

Environment Variables:
  OPENAI_API_KEY: Required for OpenAI API access

The tool will:
1. Read GUID list from input CSV
2. Find matching GUIDs in flattened data (Column D only)
3. For each match, extract the formula text
4. Send formula + instruction to OpenAI for FRS102 classification
5. Output CSV with original data + FRS102_Classification column
        """
    )
    
    parser.add_argument('guid_file', help='Path to CSV file with GUIDs to process')
    parser.add_argument('flattened_file', help='Path to flattened financial data CSV')
    parser.add_argument('-o', '--output', help='Output CSV file path (default: auto-generated)')
    parser.add_argument('--instruction', help='Custom instruction for OpenAI classification')
    parser.add_argument('--config', help='Path to config file (default: config.yaml)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--log-file', help='Log to file instead of console')
    
    args = parser.parse_args()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level, log_file=args.log_file)
    
    try:
        # Process GUID formulas
        result = asyncio.run(process_guid_formulas(
            guid_file_path=args.guid_file,
            flattened_file_path=args.flattened_file,
            output_path=args.output,
            instruction=args.instruction,
            config_path=args.config
        ))
        
        # Print summary
        print_processing_summary(result)
        
        print(f"\n✅ Success! GUID formula processing completed: {result.output_path}")
        print(f"📊 Classified {result.guids_classified}/{result.guids_found} formulas found")
        
        if result.classification_errors:
            print(f"⚠️  Note: {len(result.classification_errors)} classification errors occurred (see output file for details)")
        
    except Exception as e:
        logger.error(f"Failed to process GUID formulas: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()