"""
GUID Formula Updater Tool

A tool for processing GUIDs from flattened financial data and updating them
with FRS102 accounting standard classifications via OpenAI API calls.
"""

__version__ = "1.0.0"
__author__ = "Financial Tools Team"

from .main import process_guid_formulas
from .utils import GuidFormulaResult

__all__ = ["process_guid_formulas", "GuidFormulaResult"]