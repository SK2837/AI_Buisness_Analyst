from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.services.llm.factory import LLMFactory
from app.services.analysis.prompts import QUERY_CLASSIFICATION_PROMPT

class QueryIntent(BaseModel):
    """Structured representation of user query intent."""
    intent: str
    metrics: List[str]
    dimensions: List[str]
    time_range: Optional[str] = None
    filters: Dict[str, Any] = {}
    complexity: str

class QueryProcessor:
    """Service for processing and understanding user queries."""
    
    def __init__(self):
        self.llm = LLMFactory.get_provider()
        
    async def analyze_query(self, user_query: str) -> QueryIntent:
        """
        Analyze a natural language query to extract intent and entities.
        
        Args:
            user_query: The user's natural language question
            
        Returns:
            QueryIntent object with structured analysis
        """
        response = await self.llm.generate_json(
            prompt=f"Analyze this query: '{user_query}'",
            system_prompt=QUERY_CLASSIFICATION_PROMPT,
            temperature=0.1  # Low temperature for consistent extraction
        )
        
        return QueryIntent(**response)
