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

    def _summarize_issues(self, issues: List[Dict[str, Any]], max_issues: int = 3) -> List[Dict[str, Any]]:
        summarized = []
        for issue in issues[:max_issues]:
            context = issue.get("context", {})
            snippet = "\n".join(
                context.get("before", []) +
                [">>> " + context.get("target_line", "")] +
                context.get("after", [])
            )
            summarized.append({
                "location": issue.get("location"),
                "description": issue.get("description"),
                "issue_type": issue.get("issue_type"),
                "code_snippet": snippet,
                "suggestions": issue.get("analysis", {}).get("fix_suggestions", [])
            })
        return summarized

    
    # def generate_repair_prompt(self, error_info: Dict[str, Any], 
    #                           source_code: str, 
    #                           test_results: Optional[Dict[str, Any]] = None) -> str:
    #     """
    #     Generate a prompt for code repair based on error information.
        
    #     Args:
    #         error_info: Dictionary containing error information from static analysis
    #         source_code: Source code containing the error
    #         test_results: Optional results from test execution
            
    #     Returns:
    #         Formatted prompt string to send to the LLM
    #     """
    #     # Check if we have the enhanced format
    #     using_enhanced_format = error_info.get("using_enhanced_format", False)
        
    #     # Determine which template to use based on the format
    #     template_name = "repair_enhanced" if using_enhanced_format and "repair_enhanced" in self.templates else "repair"
        
    #     if template_name not in self.templates:
    #         # Fallback template if no templates are loaded
    #         if using_enhanced_format and "processed_issues" in error_info:
    #             short_code_snippets = []
    #             for issue in error_info["processed_issues"][:3]:
    #                 ctx = issue.get("context", {})
    #                 snippet = "\n".join(
    #                     ctx.get("before", []) + 
    #                     [">>> " + ctx.get("target_line", "")] + 
    #                     ctx.get("after", [])
    #                 )
    #                 short_code_snippets.append(f"// From {issue['location']['file']}:{issue['location']['line']}\n{snippet}")

    #             source_code = "\n\n".join(short_code_snippets)

    #         else:
    #             # Use standard format for the fallback template
    #             prompt = (
    #                 "Please fix the following code:\n\n"
    #                 f"{source_code}\n\n"
    #                 "The static analysis tool found these errors:\n"
    #                 f"{json.dumps(error_info, indent=2)}\n\n"
    #             )
            
    #         if test_results:
    #             prompt += (
    #                 "Test results:\n"
    #                 f"{json.dumps(test_results, indent=2)}\n\n"
    #             )
                
    #         prompt += "Please provide the corrected code."
    #         return prompt
            
    #     # Use the template if available
    #     prompt = self.templates[template_name]
        
    #     # Replace placeholders in the template
    #     prompt = prompt.replace("{{SOURCE_CODE}}", source_code)
        
    #     if using_enhanced_format and "processed_issues" in error_info:
    #         # Format the enhanced error info in a more readable way
    #         summarized_issues = self._summarize_issues(error_info["processed_issues"], max_issues=3)
    #         formatted_errors = json.dumps(summarized_issues, indent=2)
    #         prompt = prompt.replace("{{ERROR_INFO}}", formatted_errors)

    #     else:
    #         # Use the standard format
    #         prompt = prompt.replace("{{ERROR_INFO}}", json.dumps(error_info, indent=2))
        
    #     if test_results:
    #         prompt = prompt.replace(
    #             "{{TEST_RESULTS}}", 
    #             json.dumps(test_results, indent=2)
    #         )
    #     else:
    #         prompt = prompt.replace("{{TEST_RESULTS}}", "No test results available")
            
    #     return prompt
    def generate_repair_prompt(self, error_info: Dict[str, Any], 
                          source_code: str, 
                          test_results: Optional[Dict[str, Any]] = None) -> str:
   
        using_enhanced_format = error_info.get("using_enhanced_format", False)
        template_name = "repair_enhanced" if using_enhanced_format and "repair_enhanced" in self.templates else "repair"

        # 🧠 만약 enhanced format + 이슈 있으면: 문제 부분만 추려내기
        if using_enhanced_format and "processed_issues" in error_info:
            short_code_snippets = []
            for issue in error_info["processed_issues"][:3]:  # 최대 3개 이슈만
                ctx = issue.get("context", {})
                snippet = "\n".join(
                    ctx.get("before", []) +
                    [">>> " + ctx.get("target_line", "")] +
                    ctx.get("after", [])
                )
                loc = issue.get("location", {})
                file = loc.get("file", "unknown")
                line = loc.get("line", 0)
                short_code_snippets.append(f"// From {file}:{line}\n{snippet}")
            source_code = "\n\n".join(short_code_snippets)

    # 🧩 템플릿 사용 가능하면: 템플릿 기반 생성
        if template_name in self.templates:
            prompt = self.templates[template_name]
            prompt = prompt.replace("{{SOURCE_CODE}}", source_code)

            if using_enhanced_format and "processed_issues" in error_info:
                summarized_issues = self._summarize_issues(error_info["processed_issues"], max_issues=3)
                formatted_errors = json.dumps(summarized_issues, indent=2)
                prompt = prompt.replace("{{ERROR_INFO}}", formatted_errors)
            else:
                prompt = prompt.replace("{{ERROR_INFO}}", json.dumps(error_info, indent=2))

            prompt = prompt.replace("{{TEST_RESULTS}}", json.dumps(test_results or "No test results available", indent=2))
            return prompt

    # 🔙 템플릿 없을 경우 fallback 방식
        prompt = (
            "Please fix the following code:\n\n"
            f"{source_code}\n\n"
            "The static analysis tool found these errors:\n"
            f"{json.dumps(error_info, indent=2)}\n\n"
        )

        if test_results:
            prompt += f"Test results:\n{json.dumps(test_results, indent=2)}\n\n"

        prompt += "Please provide the corrected code."
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
        

        print("\n====================== GENERATED PROMPT ======================\n")
        print(prompt[:5000])  
        print("\n=============================================================\n")

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
        print("Running local LLM (Mistral-7B-Instruct) repair...")

        model_id = "mistralai/Mistral-7B-Instruct-v0.2"
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype="auto"   # mixed precision (fp16/bf16 지원)
        )

        input_ids = tokenizer(prompt, return_tensors="pt").input_ids[0]
        max_input_tokens = 8192 - 512  # 출력 공간 확보

        if len(input_ids) > max_input_tokens:
            print(f"[Warning] Prompt too long ({len(input_ids)} tokens), truncating...")
            input_ids = input_ids[-max_input_tokens:]
            prompt = tokenizer.decode(input_ids, skip_special_tokens=True)

        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            do_sample=False
        )

        result = generator(prompt)[0]['generated_text']

        if result.startswith(prompt):
            return result[len(prompt):].strip()
        return result.strip()
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