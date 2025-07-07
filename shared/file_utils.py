"""
Shared file and path utilities.
"""

import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def validate_excel_file(file_path: str) -> Path:
    """
    Validate that a file exists and is an Excel file.
    
    Args:
        file_path (str): Path to validate
        
    Returns:
        Path: Validated Path object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not Excel format
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if path.suffix.lower() not in ['.xlsx', '.xlsm']:
        raise ValueError(f"File must be Excel format (.xlsx/.xlsm), got: {path.suffix}")
    
    return path


def ensure_output_dir(output_path: str) -> Path:
    """
    Ensure the output directory exists.
    
    Args:
        output_path (str): Output file or directory path
        
    Returns:
        Path: Path object for the output
    """
    path = Path(output_path)
    
    # If it's a file path, create parent directory
    if path.suffix:
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        # If it's a directory path, create the directory
        path.mkdir(parents=True, exist_ok=True)
    
    return path


def generate_output_filename(input_file: str, suffix: str, output_dir: Optional[str] = None) -> str:
    """
    Generate an output filename based on input file.
    
    Args:
        input_file (str): Input file path
        suffix (str): Suffix to add (e.g., '_flattened', '_guid_extracted')
        output_dir (str, optional): Output directory. If None, uses same dir as input.
        
    Returns:
        str: Generated output file path
    """
    input_path = Path(input_file)
    
    if output_dir:
        output_path = Path(output_dir)
        ensure_output_dir(output_dir)
    else:
        output_path = input_path.parent
    
    output_filename = f"{input_path.stem}{suffix}.csv"
    return str(output_path / output_filename)


def read_guid_mapping_csv(csv_path: str) -> list:
    """
    Read GUID mapping from CSV file.
    Expected format: GUID,SheetName
    
    Args:
        csv_path (str): Path to CSV file with GUID mappings
        
    Returns:
        list: List of dicts with 'guid' and 'sheet_name' keys
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV format is invalid
    """
    import pandas as pd
    
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"GUID mapping file not found: {csv_file}")
    
    try:
        df = pd.read_csv(csv_file)
        
        # Validate required columns
        required_cols = ['GUID', 'SheetName']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"CSV missing required columns: {missing_cols}")
        
        # Convert to list of dicts
        guid_mappings = []
        for _, row in df.iterrows():
            guid_mappings.append({
                'guid': str(row['GUID']).strip(),
                'sheet_name': str(row['SheetName']).strip()
            })
        
        logger.info(f"Loaded {len(guid_mappings)} GUID mappings from {csv_file}")
        return guid_mappings
        
    except Exception as e:
        raise ValueError(f"Error reading GUID mapping CSV: {e}")