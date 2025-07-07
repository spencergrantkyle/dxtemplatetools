"""
Shared logging configuration and utilities.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(level: str = "INFO", log_file: Optional[str] = None, format_string: Optional[str] = None) -> None:
    """
    Set up logging configuration.
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file (str, optional): Path to log file. If None, logs to console only.
        format_string (str, optional): Custom log format string
    """
    logging_level = getattr(logging, level.upper(), logging.INFO)
    
    # Default format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(logging_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name (str): Logger name (typically __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)