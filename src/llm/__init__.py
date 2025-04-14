"""
LLM module for code repair.

This module integrates large language models for automatic code repair.
"""
from src.llm.code_repair import CodeRepairPrompt, CodeRepairManager
from src.llm.repair import main as repair_main 