"""
LLM Adapters for different providers to ensure compatibility with LangChain.
"""

import requests
import time
from typing import Any, Dict, List, Optional
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from config import get_logger

logger = get_logger(__name__)


class HuggingFaceLLM(LLM):
    """
    Hugging Face Inference API LLM wrapper compatible with LangChain.
    """
    
    model_name: str
    api_key: str
    api_url: str = "https://api-inference.huggingface.co/models"
    max_retries: int = 3
    retry_delay: int = 1
    temperature: float = 0.7
    max_length: int = 512
    
    def __init__(self, model_name: str, api_key: str, **kwargs):
        super().__init__(
            model_name=model_name,
            api_key=api_key,
            **kwargs
        )
        self.api_url = f"{self.api_url}/{model_name}"
    
    @property
    def _llm_type(self) -> str:
        """Return identifier of llm type."""
        return "huggingface"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Call the Hugging Face Inference API.
        
        Args:
            prompt: The prompt to send to the model
            stop: Stop sequences (not used in this implementation)
            run_manager: Callback manager (not used in this implementation)
            **kwargs: Additional keyword arguments
            
        Returns:
            Generated text response
        """
        logger.debug(f"🤗 HuggingFace LLM: Calling API with prompt length: {len(prompt)}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare payload based on model type
        payload = self._prepare_payload(prompt, **kwargs)
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"🔄 HuggingFace LLM: Attempt {attempt + 1}/{self.max_retries}")
                
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = self._parse_response(response.json(), prompt)
                    logger.debug(f"✅ HuggingFace LLM: Got response length: {len(result)}")
                    return result
                
                elif response.status_code == 503:
                    # Model is loading, wait and retry
                    logger.warning(f"⏳ HuggingFace LLM: Model loading, retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                    continue
                
                else:
                    error_msg = f"API request failed with status {response.status_code}: {response.text}"
                    logger.error(f"❌ HuggingFace LLM: {error_msg}")
                    
                    if attempt == self.max_retries - 1:
                        return f"Error: {error_msg}"
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ HuggingFace LLM: Request exception on attempt {attempt + 1}: {e}")
                
                if attempt == self.max_retries - 1:
                    return f"Error: Failed to connect to Hugging Face API: {e}"
                
                time.sleep(self.retry_delay)
        
        return "Error: All retry attempts failed"
    
    def _prepare_payload(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare the API payload based on the model type.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            API payload dictionary
        """
        # For text-generation models
        if "instruct" in self.model_name.lower() or "chat" in self.model_name.lower():
            return {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": kwargs.get("max_length", self.max_length),
                    "temperature": kwargs.get("temperature", self.temperature),
                    "return_full_text": False,
                    "do_sample": True,
                }
            }
        
        # For conversational models (like DialoGPT)
        elif "dialogpt" in self.model_name.lower():
            return {
                "inputs": {
                    "past_user_inputs": [],
                    "generated_responses": [],
                    "text": prompt
                },
                "parameters": {
                    "max_length": kwargs.get("max_length", self.max_length),
                    "temperature": kwargs.get("temperature", self.temperature),
                }
            }
        
        # Default for general text-generation
        else:
            return {
                "inputs": prompt,
                "parameters": {
                    "max_length": kwargs.get("max_length", self.max_length),
                    "temperature": kwargs.get("temperature", self.temperature),
                    "num_return_sequences": 1,
                }
            }
    
    def _parse_response(self, response_data: Any, original_prompt: str) -> str:
        """
        Parse the API response based on the model type.
        
        Args:
            response_data: Raw API response
            original_prompt: Original prompt for context
            
        Returns:
            Parsed text response
        """
        try:
            # Handle different response formats
            if isinstance(response_data, list) and len(response_data) > 0:
                first_item = response_data[0]
                
                # Text generation format
                if isinstance(first_item, dict):
                    if "generated_text" in first_item:
                        text = first_item["generated_text"]
                        # Remove the original prompt if it's included
                        if text.startswith(original_prompt):
                            text = text[len(original_prompt):].strip()
                        return text
                    
                    elif "conversation" in first_item:
                        # Conversational format
                        conversation = first_item["conversation"]
                        if "generated_responses" in conversation and conversation["generated_responses"]:
                            return conversation["generated_responses"][-1]
                
                # Simple string response
                elif isinstance(first_item, str):
                    return first_item
            
            # Conversational model direct response
            elif isinstance(response_data, dict):
                if "conversation" in response_data:
                    conv = response_data["conversation"]
                    if "generated_responses" in conv and conv["generated_responses"]:
                        return conv["generated_responses"][-1]
                elif "generated_text" in response_data:
                    return response_data["generated_text"]
            
            # Fallback
            logger.warning(f"⚠️ HuggingFace LLM: Unexpected response format: {type(response_data)}")
            return str(response_data)
            
        except Exception as e:
            logger.error(f"❌ HuggingFace LLM: Error parsing response: {e}")
            return f"Error parsing response: {e}"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_length": self.max_length,
        } 