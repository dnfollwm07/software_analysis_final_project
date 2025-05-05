import logging
import os
from pathlib import Path

# Configure logger
logger = logging.getLogger('llm')
logger.setLevel(logging.DEBUG)  # Set overall logger level to DEBUG

# Add console handler if not already added
if not logger.handlers:
    # Console handler - INFO level with colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = '%(asctime)s - %(name)s - \033[30;47m%(levelname)s\033[0m - %(message)s'
    console_handler.setFormatter(logging.Formatter(console_format))
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
