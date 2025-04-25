"""
LLM module for code repair.

This module integrates large language models for automatic code repair.
"""
import logging
import os
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds color to the levelname."""
    
    def format(self, record):
        # White background (47) and black text (30)
        levelname = record.levelname
        record.levelname = f"\033[30;47m{levelname}\033[0m"
        return super().format(record)


# Configure logger
logger = logging.getLogger('llm')
logger.setLevel(logging.DEBUG)  # Set overall logger level to DEBUG

# Add console handler if not already added
if not logger.handlers:
    # Console handler - INFO level with colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_handler.setFormatter(ColoredFormatter(console_format))
    logger.addHandler(console_handler)
    
    # File handler - DEBUG level without colors
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)  # Create logs directory if it doesn't exist
    log_file = log_dir / 'log.txt'
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging to console (INFO) and {log_file.absolute()} (DEBUG)")

from src.llm.repair import main as repair_main 