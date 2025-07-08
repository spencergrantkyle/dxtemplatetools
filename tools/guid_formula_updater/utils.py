"""
GUID Formula Updater Tool - Utility functions and data structures.
"""

import pandas as pd
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logger import get_logger
from shared.file_utils import read_guid_mapping_csv

logger = get_logger(__name__)


@dataclass
class GuidFormulaResult:
    """Result object containing GUID formula processing data and metadata."""
    dataframe: pd.DataFrame
    guids_processed: int
    guids_found: int
    guids_classified: int
    api_calls_made: int
    guids_not_found: List[str]
    classification_errors: List[str]
    input_path: str
    output_path: Optional[str] = None
    flattened_file_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization."""
        return {
            "guids_processed": self.guids_processed,
            "guids_found": self.guids_found,
            "guids_classified": self.guids_classified,
            "api_calls_made": self.api_calls_made,
            "guids_not_found": self.guids_not_found,
            "classification_errors": self.classification_errors,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "flattened_file_path": self.flattened_file_path
        }


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file: {e}")
        raise


def load_flattened_data(file_path: str) -> pd.DataFrame:
    """
    Load flattened financial data from CSV file.
    
    Args:
        file_path: Path to the flattened CSV file
        
    Returns:
        pd.DataFrame: Loaded data
    """
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} rows from flattened file: {file_path}")
        return df
    except FileNotFoundError:
        logger.error(f"Flattened file not found: {file_path}")
        raise
    except pd.errors.EmptyDataError:
        logger.error(f"Flattened file is empty: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading flattened file {file_path}: {e}")
        raise


def validate_flattened_data(df: pd.DataFrame, config: Dict[str, Any]) -> List[str]:
    """
    Validate that the flattened data has required columns.
    
    Args:
        df: DataFrame to validate
        config: Configuration dictionary
        
    Returns:
        List[str]: List of validation errors
    """
    errors = []
    required_columns = config["validation"]["required_columns"]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")
    
    # Check if we have any Column D entries
    col_ref_column = config["csv_processing"]["input_columns"]["col_ref_column"]
    target_column = config["csv_processing"]["target_column"]
    
    if col_ref_column in df.columns:
        column_d_count = len(df[df[col_ref_column] == target_column])
        if column_d_count == 0:
            errors.append(f"No rows found with {col_ref_column} = '{target_column}'")
        else:
            logger.info(f"Found {column_d_count} rows with {col_ref_column} = '{target_column}'")
    
    return errors


def filter_guid_data(
    flattened_df: pd.DataFrame, 
    guid_list: List[str], 
    config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Filter flattened data to only include specified GUIDs in Column D.
    
    Args:
        flattened_df: DataFrame with flattened financial data
        guid_list: List of GUIDs to filter for
        config: Configuration dictionary
        
    Returns:
        pd.DataFrame: Filtered data
    """
    input_cols = config["csv_processing"]["input_columns"]
    target_column = config["csv_processing"]["target_column"]
    
    # Filter for Column D only
    column_d_df = flattened_df[
        flattened_df[input_cols["col_ref_column"]] == target_column
    ].copy()
    
    logger.info(f"Found {len(column_d_df)} total Column D entries")
    
    # Filter for specified GUIDs
    # Handle case where GUID column might have different values
    if input_cols["guid_column"] in column_d_df.columns:
        # Direct GUID column filtering
        filtered_df = column_d_df[
            column_d_df[input_cols["guid_column"]].isin(guid_list)
        ].copy()
    else:
        # If no direct GUID column, we might need to match on other criteria
        # This is a fallback - log a warning
        logger.warning(f"No {input_cols['guid_column']} column found, returning all Column D entries")
        filtered_df = column_d_df.copy()
    
    logger.info(f"Filtered to {len(filtered_df)} rows matching target GUIDs in Column D")
    return filtered_df


def prepare_classification_data(
    filtered_df: pd.DataFrame,
    config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Prepare data for classification API calls.
    
    Args:
        filtered_df: Filtered DataFrame with GUID data
        config: Configuration dictionary
        
    Returns:
        List[Dict]: List of records ready for classification
    """
    input_cols = config["csv_processing"]["input_columns"]
    records = []
    
    for _, row in filtered_df.iterrows():
        # Extract data safely with fallbacks
        record = {
            "guid": str(row.get(input_cols["guid_column"], "Unknown")),
            "sheet": str(row.get(input_cols["sheet_column"], "Unknown")),
            "row_num": row.get(input_cols["row_column"], 0),
            "formula_text": str(row.get(input_cols["formula_column"], "")),
            "cell_value": str(row.get(input_cols["cell_value_column"], "")),
            "original_row": row.to_dict()  # Keep original row for output
        }
        
        # Skip if no formula text
        if not record["formula_text"] or record["formula_text"].strip() == "":
            logger.warning(f"Skipping GUID {record['guid']} - no formula text")
            continue
        
        # Skip if formula is too long
        max_length = config["validation"]["max_formula_length"]
        if len(record["formula_text"]) > max_length:
            logger.warning(f"Skipping GUID {record['guid']} - formula too long ({len(record['formula_text'])} chars)")
            continue
        
        records.append(record)
    
    logger.info(f"Prepared {len(records)} records for classification")
    return records


def merge_results_with_original(
    original_records: List[Dict[str, Any]],
    classification_results: List[Any],  # ClassificationResult objects
    config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Merge classification results back with original data.
    
    Args:
        original_records: Original record data
        classification_results: Results from OpenAI classification
        config: Configuration dictionary
        
    Returns:
        pd.DataFrame: Merged results
    """
    # Create a mapping of GUID to classification
    classification_map = {}
    for result in classification_results:
        classification_map[result.guid] = {
            "classification": result.classification,
            "error": result.error
        }
    
    # Build output records
    output_records = []
    for record in original_records:
        # Start with original row data
        output_row = record["original_row"].copy()
        
        # Add classification result
        guid = record["guid"]
        if guid in classification_map:
            classification_info = classification_map[guid]
            output_row[config["csv_processing"]["output_columns"]["classification_column"]] = classification_info["classification"]
            
            # Optionally add error information
            if classification_info["error"]:
                output_row["Classification_Error"] = classification_info["error"]
        else:
            output_row[config["csv_processing"]["output_columns"]["classification_column"]] = "Not_Processed"
        
        output_records.append(output_row)
    
    return pd.DataFrame(output_records)


def print_processing_summary(result: GuidFormulaResult) -> None:
    """Print a formatted summary of the processing result."""
    print(f"\n🔍 GUID Formula Processing Summary:")
    print(f"   📁 Input GUID file: {result.input_path}")
    print(f"   📄 Flattened data file: {result.flattened_file_path}")
    print(f"   📋 GUIDs processed: {result.guids_processed}")
    print(f"   ✅ GUIDs found in data: {result.guids_found}")
    print(f"   🎯 GUIDs classified: {result.guids_classified}")
    print(f"   🌐 API calls made: {result.api_calls_made}")
    print(f"   ❌ GUIDs not found: {len(result.guids_not_found)}")
    print(f"   ⚠️  Classification errors: {len(result.classification_errors)}")
    
    if result.guids_not_found:
        print(f"\n⚠️  GUIDs not found in flattened data:")
        for guid in result.guids_not_found[:10]:  # Show first 10
            print(f"      • {guid}")
        if len(result.guids_not_found) > 10:
            print(f"      ... and {len(result.guids_not_found) - 10} more")
    
    if result.classification_errors:
        print(f"\n❌ Classification errors:")
        for error in result.classification_errors[:5]:  # Show first 5
            print(f"      • {error}")
        if len(result.classification_errors) > 5:
            print(f"      ... and {len(result.classification_errors) - 5} more")


def create_guid_list_template(output_path: str = "guid_list_template.csv") -> str:
    """
    Create a template CSV file for GUID input.
    
    Args:
        output_path: Path for the template file
        
    Returns:
        str: Path to created template
    """
    template_data = {
        'GUID': ['00CAC489', '12345678', '87654321', 'ABCD1234']
    }
    
    df = pd.DataFrame(template_data)
    df.to_csv(output_path, index=False)
    
    logger.info(f"Created GUID list template: {output_path}")
    return output_path