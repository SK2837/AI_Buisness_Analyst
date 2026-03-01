from typing import Dict, Any, List
import pandas as pd
import json
from app.services.llm.factory import LLMFactory
from app.services.analysis.prompts import DATA_ANALYSIS_PROMPT

class NarrativeGenerator:
    """Service for generating narratives from data analysis."""
    
    def __init__(self):
        self.llm = LLMFactory.get_provider()
        
    async def generate_narrative(
        self, 
        user_query: str, 
        df: pd.DataFrame, 
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a narrative explanation of the data and analysis.
        
        Args:
            user_query: The original user question
            df: The result DataFrame
            analysis_results: Dictionary of statistical analysis results
            
        Returns:
            Dictionary containing summary, narrative, key_points, etc.
        """
        # Prepare data preview (limit rows to avoid token limits)
        row_limit = 10
        data_preview = df.head(row_limit).to_markdown(index=False)
        
        # Format analysis results as string
        analysis_str = json.dumps(analysis_results, indent=2, default=str)
        
        prompt = DATA_ANALYSIS_PROMPT.format(
            user_query=user_query,
            analysis_results=analysis_str,
            row_limit=row_limit,
            data_preview=data_preview
        )
        
        response = await self.llm.generate_json(
            prompt=prompt,
            temperature=0.3  # Slightly higher temperature for creative but grounded writing
        )
        
        return response
