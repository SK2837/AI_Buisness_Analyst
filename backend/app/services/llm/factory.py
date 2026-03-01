from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.openai_service import OpenAIService
from app.services.llm.anthropic_service import AnthropicService

class LLMFactory:
    """Factory for creating LLM provider instances."""
    
    @staticmethod
    def get_provider() -> LLMProvider:
        """
        Get the configured LLM provider instance.
        
        Returns:
            Instance of LLMProvider (OpenAI or Anthropic)
        """
        provider = settings.LLM_PROVIDER.lower()
        
        if provider == "openai":
            return OpenAIService()
        elif provider == "anthropic":
            return AnthropicService()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
