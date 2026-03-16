"""
HuggingFace Model Integration with Fallback Support
"""
import os
import json
from typing import Optional, Dict, Any, List
from huggingface_hub import InferenceClient
from common.logger import get_logger
from common.config import (
    HUGGINGFACE_API_KEY,
    HF_MODELS,
    GROQ_API_KEY,
    GROQ_MODEL,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL
)

# Import groq for fallback
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger = get_logger("huggingface_model")
    logger.warning("Groq not available, install with: pip install groq")

logger = get_logger("huggingface_model")


class HuggingFaceModel:
    """HuggingFace Inference API wrapper with multiple model fallback"""
    
    def __init__(self):
        """Initialize HuggingFace client with fallback models"""
        if not HUGGINGFACE_API_KEY:
            raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")
        
        self.client = InferenceClient(token=HUGGINGFACE_API_KEY)
        self.models = HF_MODELS
        self.current_model_index = 0
        logger.info(f"HuggingFace client initialized with {len(self.models)} models")
        logger.info(f"Primary model: {self.models[0]}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.3,
    ) -> str:
        """
        Generate text using HuggingFace Inference API with fallback
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling
        
        Returns:
            Generated text
        """
        # Try each model in order
        for idx, model in enumerate(self.models):
            try:
                logger.info(f"Attempting generation with model {idx + 1}/{len(self.models)}: {model}")
                
                # Format messages
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                # Call HuggingFace Inference API
                response = self.client.chat_completion(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                
                # Extract response text
                if response and response.choices:
                    result = response.choices[0].message.content
                    logger.info(f"✓ Successfully generated response with {model}")
                    return result
                
                logger.warning(f"Empty response from {model}, trying next model...")
                
            except Exception as e:
                logger.warning(f"Error with model {model}: {str(e)}")
                if idx < len(self.models) - 1:
                    logger.info(f"Falling back to next model...")
                else:
                    logger.error(f"All HuggingFace models failed, trying Groq as final fallback...")
                    # Try Groq as ultimate fallback
                    try:
                        from huggingface_hub import InferenceClient
                        groq_result = self._try_groq_fallback(prompt, system_prompt, max_tokens, temperature)
                        if groq_result:
                            return groq_result
                    except Exception as groq_error:
                        logger.error(f"Groq fallback also failed: {groq_error}")
                    raise Exception(f"All models exhausted. Last HF error: {str(e)[:100]}")
        
        raise Exception("Failed to generate response from any model")
    
    def _try_groq_fallback(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> Optional[str]:
        """Try Groq as fallback when all HuggingFace models fail"""
        if not GROQ_AVAILABLE or not GROQ_API_KEY:
            logger.warning("Groq not available as fallback")
            return None
            
        try:
            groq_client = Groq(api_key=GROQ_API_KEY)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            logger.info(f"Trying Groq fallback with model: {GROQ_MODEL}")
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            result = response.choices[0].message.content
            logger.info(f"✓ Groq fallback successful!")
            return result
        except Exception as e:
            logger.error(f"Groq fallback failed: {e}")
            return None
    
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        output_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate structured output (attempts JSON parsing)
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            output_schema: Expected output schema (dict with field names and descriptions)
        
        Returns:
            Parsed JSON response
        """
        # Build detailed JSON schema instruction
        schema_instruction = "\n\nIMPORTANT: Respond ONLY with valid JSON matching this EXACT schema. No additional text before or after the JSON."
        
        if output_schema:
            schema_instruction += "\n\nRequired JSON format:\n"
            schema_instruction += json.dumps(output_schema, indent=2)
            schema_instruction += "\n\nEnsure ALL field names match EXACTLY as shown above."
        
        full_system_prompt = (system_prompt or "") + schema_instruction
        
        # Generate response
        response_text = self.generate(
            prompt=prompt,
            system_prompt=full_system_prompt,
            temperature=0.1,  # Lower temperature for structured output
        )
        
        # Try to extract and parse JSON
        try:
            # Try direct JSON parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Try to find any JSON object in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            logger.error(f"Failed to parse JSON from response: {response_text[:200]}...")
            raise ValueError(f"Could not parse JSON from model response")


class MultiProviderLLM:
    """
    Multi-provider LLM with automatic fallback
    Tries HuggingFace first, then Groq, then Ollama
    """
    
    def __init__(self):
        """Initialize with all available providers"""
        self.providers = []
        
        # Try HuggingFace first
        try:
            if HUGGINGFACE_API_KEY:
                self.providers.append(("HuggingFace", HuggingFaceModel()))
                logger.info("✓ HuggingFace provider initialized")
        except Exception as e:
            logger.warning(f"HuggingFace initialization failed: {e}")
        
        # Add Groq as fallback
        if GROQ_API_KEY:
            try:
                from pydantic_ai.models.groq import GroqModel
                os.environ['GROQ_API_KEY'] = GROQ_API_KEY
                self.providers.append(("Groq", GroqModel(model_name=GROQ_MODEL)))
                logger.info("✓ Groq provider initialized as fallback")
            except Exception as e:
                logger.warning(f"Groq initialization failed: {e}")
        
        # Add Ollama as final fallback
        try:
            from pydantic_ai.models.ollama import OllamaModel
            self.providers.append(("Ollama", OllamaModel(model_name=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)))
            logger.info("✓ Ollama provider initialized as fallback")
        except Exception as e:
            logger.warning(f"Ollama initialization failed: {e}")
        
        if not self.providers:
            raise Exception("No LLM providers available!")
        
        logger.info(f"MultiProviderLLM initialized with {len(self.providers)} providers")
    
    def get_primary_provider(self):
        """Get the primary (first available) provider"""
        if self.providers:
            name, model = self.providers[0]
            logger.info(f"Using primary provider: {name}")
            return model
        raise Exception("No providers available")
