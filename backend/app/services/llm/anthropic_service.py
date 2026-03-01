import json
from typing import Dict, Any, Optional, List
import anthropic
from app.core.config import settings
from app.services.llm.base import LLMProvider

class AnthropicService(LLMProvider):
    """Anthropic implementation of LLMProvider."""

    def __init__(self):
        """Initialize Anthropic client."""
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
        self.default_max_tokens = settings.ANTHROPIC_MAX_TOKENS

    async def generate_text(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using Anthropic Claude."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens or self.default_max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
            
        if temperature is not None:
            kwargs["temperature"] = temperature

        response = await self.client.messages.create(**kwargs)
        return response.content[0].text

    async def generate_json(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate JSON using Anthropic."""
        # Append instruction to ensure JSON output
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens or self.default_max_tokens,
            "messages": [{"role": "user", "content": json_prompt}]
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
            
        if temperature is not None:
            kwargs["temperature"] = temperature

        response = await self.client.messages.create(**kwargs)
        content = response.content[0].text
        
        # Basic cleanup to extract JSON if wrapped in markdown blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse JSON response: {content}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate chat completion."""
        # Extract system message if present as first message
        system_prompt = None
        filtered_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                filtered_messages.append(msg)
                
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens or self.default_max_tokens,
            "messages": filtered_messages
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
            
        if temperature is not None:
            kwargs["temperature"] = temperature

        response = await self.client.messages.create(**kwargs)
        return response.content[0].text
