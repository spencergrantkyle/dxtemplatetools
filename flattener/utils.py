"""
Utility functions for logging, output formatting, and run tracking.
"""

import logging
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from functools import wraps
from .flattener import FlattenResult


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Set up logging configuration.
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file (str, optional): Path to log file. If None, logs to console only.
    """
    logging_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(logging_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def log_run_to_file(run_name: str, output_dir: str = "logs"):
    """
    Decorator to log function execution details to a JSON file.
    
    Args:
        run_name (str): Name for this run/operation
        output_dir (str): Directory to store log files
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.datetime.now()
            
            # Create logs directory if it doesn't exist
            log_dir = Path(output_dir)
            log_dir.mkdir(exist_ok=True)
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Log successful execution
                end_time = datetime.datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                log_data = {
                    "run_name": run_name,
                    "function": func.__name__,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration,
                    "status": "success",
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                
                # Add result metadata if it's a FlattenResult
                if isinstance(result, FlattenResult):
                    log_data["result_metadata"] = result.to_dict()
                
                # Save log
                timestamp = start_time.strftime("%Y%m%d_%H%M%S")
                log_file = log_dir / f"{run_name}_{timestamp}.json"
                
                with open(log_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
                
                logging.info(f"Run logged to: {log_file}")
                return result
                
            except Exception as e:
                # Log failed execution
                end_time = datetime.datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                log_data = {
                    "run_name": run_name,
                    "function": func.__name__,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration,
                    "status": "error",
                    "error": str(e),
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                
                # Save error log
                timestamp = start_time.strftime("%Y%m%d_%H%M%S")
                log_file = log_dir / f"{run_name}_ERROR_{timestamp}.json"
                
                with open(log_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
                
                logging.error(f"Error logged to: {log_file}")
                raise
                
        return wrapper
    return decorator


def print_summary(result: FlattenResult) -> None:
    """Print a formatted summary of the flattening result."""
    print(f"\nFlattening Summary:")
    print(f"- File: {result.file_path}")
    print(f"- Total cells: {result.total_cells:,}")
    print(f"- Sheets processed: {result.sheets_processed}")
    
    if result.value_types:
        print(f"- Value types:")
        for value_type, count in result.value_types.items():
            print(f"  • {value_type}: {count:,}")


def create_analysis_preview(result: FlattenResult, max_rows: int = 10) -> str:
    """
    Create a preview of the flattened data for LLM analysis.
    
    Args:
        result (FlattenResult): The flattening result
        max_rows (int): Maximum number of rows to include in preview
        
    Returns:
        str: Formatted preview text
    """
    df = result.dataframe
    
    preview_text = f"""
Excel Workbook Analysis Preview
==============================

File: {result.file_path}
Total Cells: {result.total_cells:,}
Sheets: {result.sheets_processed}
Value Types: {', '.join(f'{k}({v})' for k, v in result.value_types.items())}

Sample Data (first {min(max_rows, len(df))} rows):
{df.head(max_rows).to_string(index=False)}

Sheet Distribution:
{df['Sheet'].value_counts().to_string()}
"""
    
    return preview_text


def save_analysis_artifacts(result: FlattenResult, output_dir: str = "analysis_output") -> Dict[str, str]:
    """
    Save all analysis artifacts (CSV, JSON metadata, preview) to a directory.
    
    Args:
        result (FlattenResult): The flattening result
        output_dir (str): Directory to save artifacts
        
    Returns:
        Dict[str, str]: Paths to saved files
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate base filename from input
    input_name = Path(result.file_path).stem
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{input_name}_{timestamp}"
    
    # Save CSV
    csv_path = output_path / f"{base_name}_flattened.csv"
    result.dataframe.to_csv(csv_path, index=False)
    
    # Save metadata JSON
    metadata_path = output_path / f"{base_name}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(result.to_dict(), f, indent=2)
    
    # Save preview text
    preview_path = output_path / f"{base_name}_preview.txt"
    with open(preview_path, 'w') as f:
        f.write(create_analysis_preview(result))
    
    return {
        "csv": str(csv_path),
        "metadata": str(metadata_path), 
        "preview": str(preview_path)
    }