"""
Custom Google GenAI LLM wrapper for LangChain
Works with AQ. token format
"""
from typing import Any, List, Optional
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun


class GoogleGenAILLM(LLM):
    """Custom LLM wrapper for Google GenAI SDK"""
    
    api_key: str
    model: str = "gemini-2.0-flash-exp"
    temperature: float = 0.7
    max_tokens: int = 512
    
    @property
    def _llm_type(self) -> str:
        return "google-genai"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call Google GenAI API"""
        try:
            from google import genai
            from google.genai import types
            
            # Initialize client with correct configuration
            client = genai.Client(
                api_key=self.api_key,
                http_options={'api_version': 'v1beta'}
            )
            
            # Generate response
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )
            
            # Extract text
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].content.parts[0].text
            else:
                return str(response)
                
        except Exception as e:
            raise Exception(f"Google GenAI error: {str(e)}")
