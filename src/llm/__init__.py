"""
LLM module for code repair.

This module integrates large language models for automatic code repair.
"""
from pathlib import Path
from .logger import logger
from dotenv import load_dotenv

# Check if .env.local exists
env_local = Path('.env.local')
if env_local.exists():
    logger.info(".env.local found, will load it")
    load_dotenv('.env.local')

from .repair import main as repair_main

