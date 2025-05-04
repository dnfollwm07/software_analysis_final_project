from typing import Dict, List, Any, Optional, Tuple
import os
import json
from pathlib import Path
import requests
import json
import re
import logging

from src.llm import logger
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def request_llm(prompt: str) -> str:
    logger.debug(f"Running LLM...\n\n{prompt}")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_API_KEY:

        OPENAI_API_URL = os.getenv("OPENAI_API_URL")
        if not OPENAI_API_URL:
            OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
        logger.debug("Running GPT-4 API..." + OPENAI_API_URL)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        payload = {
            "model": "qwen-plus",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }

        logger.debug(prompt)
        
        try:
            response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                logger.error("[Error] Unexpected response format from GPT-4 API")
                return ""
                
        except requests.exceptions.RequestException as e:
            logger.error(f"[Error] Failed to connect to GPT-4 API: {str(e)}")
            return ""
        except json.JSONDecodeError:
            logger.error("[Error] Invalid JSON response from GPT-4 API")
            return ""
        except Exception as e:
            logger.error(f"[Error] Unexpected error calling GPT-4 API: {str(e)}")
            return ""

    OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
    if OLLAMA_API_URL:
        logger.debug("Running Ollama LLM repair..." + OLLAMA_API_URL)
        # Ollama API endpoint
        api_url = f"{OLLAMA_API_URL}/api/generate"
        
        # Prepare the request payload
        payload = {
            "model": "llama3.1:8b", # Or other model name configured in Ollama
            "prompt": prompt,
            "stream": False
        }
        
        try:
            # Make API request
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            if "response" in result:
                return result["response"].strip()
            else:
                logger.error("[Error] Unexpected response format from Ollama")
                return ""
                
        except requests.exceptions.RequestException as e:
            logger.error(f"[Error] Failed to connect to Ollama service: {str(e)}")
            return ""
        except json.JSONDecodeError:
            logger.error("[Error] Invalid JSON response from Ollama")
            return ""
        except Exception as e:
            logger.error(f"[Error] Unexpected error calling Ollama: {str(e)}")
            return ""
    
    logger.debug("Running local LLM (Mistral-7B-Instruct) repair...")

    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",         # GPU 자동 매핑
        torch_dtype="auto"         # mixed precision
    )

    # 최대 입력 길이 설정 (Mistral은 8192 지원)
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids[0]
    max_input_tokens = 2048 - 512 # 출력 여유 확보

    if len(input_ids) > max_input_tokens:
        logger.warning(f"[Warning] Prompt too long ({len(input_ids)} tokens), truncating...")
        input_ids = input_ids[-max_input_tokens:]
        prompt = tokenizer.decode(input_ids, skip_special_tokens=True)

    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=1024,
        do_sample=False
    )

    result = generator(prompt)[0]['generated_text']

    if result.startswith(prompt):
        return result[len(prompt):].strip()
    return result.strip()

def get_code_from_result(result: str) -> str:
    """Extract code from markdown code block in the result.
    
    Args:
        result: String containing markdown formatted code
        
    Returns:
        Extracted code content or original string if no code block found
    """

    # Match code blocks with or without language specification
    pattern = r"```(?:\w+)?\n(.*?)\n```"
    matches = re.findall(pattern, result, re.DOTALL)
    
    if matches:
        # Return first code block content
        return matches[0].strip()
    
    return result.strip()
