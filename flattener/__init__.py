"""
Excel Flattener - A modular tool for flattening Excel workbooks into structured data.
"""

from .flattener import flatten_workbook, FlattenResult
from .utils import setup_logging, log_run_to_file

__version__ = "0.2.0"
__all__ = ["flatten_workbook", "FlattenResult", "setup_logging", "log_run_to_file"]