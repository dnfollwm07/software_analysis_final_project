"""
LLM-based code repair module.

This module integrates with LLMs to generate code repairs based on static and dynamic
analysis results.
"""
from typing import Dict, List, Any, Optional, Tuple
import os
import json
from pathlib import Path

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline



class CodeRepairPrompt:
    """Class for generating prompts for LLM-based code repair."""
    
    def __init__(self, template_dir: str = "config/prompt_templates"):
        """
        Initialize the code repair prompt generator.
        
        Args:
            template_dir: Directory containing prompt templates
        """
        self.template_dir = Path(template_dir)
        self.templates = {}
        self._load_templates()
        
    def _load_templates(self):
        """Load prompt templates from the template directory."""
        if not self.template_dir.exists():
            print(f"Warning: Template directory {self.template_dir} does not exist")
            return
            
        for template_file in self.template_dir.glob("*.txt"):
            template_name = template_file.stem
            with open(template_file, 'r') as f:
                self.templates[template_name] = f.read()
    
    def generate_repair_prompt(self, error_info: Dict[str, Any], 
                              source_code: str, 
                              test_results: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a prompt for code repair based on error information.
        
        Args:
            error_info: Dictionary containing error information from static analysis
            source_code: Source code containing the error
            test_results: Optional results from test execution
            
        Returns:
            Formatted prompt string to send to the LLM
        """
        if "repair" not in self.templates:
            # Fallback template if no templates are loaded
            prompt = (
                "Please fix the following code:\n\n"
                f"{source_code}\n\n"
                "The static analysis tool found these errors:\n"
                f"{json.dumps(error_info, indent=2)}\n\n"
            )
            
            if test_results:
                prompt += (
                    "Test results:\n"
                    f"{json.dumps(test_results, indent=2)}\n\n"
                )
                
            prompt += "Please provide the corrected code."
            return prompt
            
        # Use the template if available
        prompt = self.templates["repair"]
        
        # Replace placeholders in the template
        prompt = prompt.replace("{{SOURCE_CODE}}", source_code)
        prompt = prompt.replace("{{ERROR_INFO}}", json.dumps(error_info, indent=2))
        
        if test_results:
            prompt = prompt.replace(
                "{{TEST_RESULTS}}", 
                json.dumps(test_results, indent=2)
            )
        else:
            prompt = prompt.replace("{{TEST_RESULTS}}", "No test results available")
            
        return prompt


class CodeRepairManager:
    """Manager class for the code repair process."""
    
    def __init__(self, prompt_generator: CodeRepairPrompt, llm_api_key: Optional[str] = None):
        """
        Initialize the code repair manager.
        
        Args:
            llm_api_key: API key for the LLM service
            prompt_generator: Prompt generator instance
        """
        self.llm_api_key = llm_api_key
        self.prompt_generator = prompt_generator
        self.repair_history = []
        
    def repair_code(self, source_file: str, 
                   error_info: Dict[str, Any],
                   test_results: Optional[Dict[str, Any]] = None) -> Tuple[str, float]:
        """
        Repair code using LLM suggestions based on error information.
        
        Args:
            source_file: Path to the source file to repair
            error_info: Dictionary containing error information from static analysis
            test_results: Optional results from test execution
            
        Returns:
            Tuple containing (repaired_code, confidence_score)
        """
        with open(source_file, 'r') as f:
            source_code = f.read()
            
        prompt = self.prompt_generator.generate_repair_prompt(
            error_info, source_code, test_results
        )
        
        # TODO: Integrate with actual LLM API
        # This is a placeholder for the actual LLM API call
        repaired_code = self._get_llm_repair(prompt)
        confidence_score = 0.8  # Placeholder confidence score
        
        # Record the repair in history
        self.repair_history.append({
            "source_file": source_file,
            "error_info": error_info,
            "original_code": source_code,
            "repaired_code": repaired_code,
            "confidence_score": confidence_score
        })
        
        return repaired_code, confidence_score
    def _get_llm_repair(self, prompt: str) -> str:
        print("Running local LLM (TinyLlama) repair...")

        model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id)

    # ✅ 토큰 길이 제한: 2048 기준 자르기
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids[0]
        max_input_tokens = 2048 - 512  # 출력용 토큰 공간 확보

        if len(input_ids) > max_input_tokens:
            print(f"[Warning] Prompt too long ({len(input_ids)} tokens), truncating...")
            input_ids = input_ids[-max_input_tokens:]
            prompt = tokenizer.decode(input_ids, skip_special_tokens=True)

        generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

    # ✅ 출력 길이 늘리기
        result = generator(prompt, max_new_tokens=512, do_sample=False)

    # ✅ prompt 부분 제거
        generated = result[0]['generated_text']
        if generated.startswith(prompt):
            return generated[len(prompt):].strip()
        return generated.strip()

        
    def evaluate_repair(self, repaired_code: str, 
                       test_results: Dict[str, Any]) -> float:
        """
        Evaluate the quality of a code repair based on test results.
        
        Args:
            repaired_code: Repaired code from LLM
            test_results: Results from running tests on the repaired code
            
        Returns:
            Score from 0.0 to 1.0 indicating repair quality
        """
        # TODO: Implement repair quality evaluation
        # This is a placeholder implementation
        
        # Simple evaluation based on test pass rate
        if "total_tests" in test_results and test_results["total_tests"] > 0:
            return test_results.get("passed_tests", 0) / test_results["total_tests"]
        return 0.5  # Default score 