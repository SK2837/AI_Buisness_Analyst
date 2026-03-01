from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate_text(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text response from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instruction
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            
        Returns:
            Generated text string
        """
        pass

    @abstractmethod
    async def generate_json(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instruction
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            
        Returns:
            Parsed JSON dictionary
        """
        pass
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate response from a list of chat messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            
        Returns:
            Generated text response
        """
        pass
