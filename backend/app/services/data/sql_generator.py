from typing import Dict, Any, Optional
from app.services.llm.factory import LLMFactory
from app.services.analysis.prompts import SQL_GENERATION_PROMPT
from app.services.data.sql_validator import SQLValidator

class SQLGenerator:
    """Service for generating SQL from natural language."""
    
    def __init__(self):
        self.llm = LLMFactory.get_provider()
        
    async def generate_sql(self, user_query: str, schema_context: Dict[str, Any], dialect: str = "sqlite") -> Dict[str, Any]:
        """
        Generate SQL query from natural language.
        
        Args:
            user_query: The user's question
            schema_context: Dictionary describing tables and columns
            
        Returns:
            Dictionary with 'sql', 'explanation', and 'can_answer'
        """
        # Format schema context as string for prompt
        schema_str = self._format_schema(schema_context)
        
        prompt = SQL_GENERATION_PROMPT.format(
            schema_context=schema_str,
            user_query=user_query,
            dialect=dialect
        )
        
        response = await self.llm.generate_json(
            prompt=prompt,
            temperature=0.1  # Low temperature for precise SQL
        )
        
        # Validate generated SQL
        if response.get("can_answer") and response.get("sql"):
            is_safe = SQLValidator.validate_sql(response["sql"])
            if not is_safe:
                return {
                    "sql": "",
                    "explanation": "Generated SQL was flagged as unsafe (contained forbidden keywords).",
                    "can_answer": False
                }
                
        return response
        
    def _format_schema(self, schema: Dict[str, Any]) -> str:
        """Format schema dictionary into a readable string for the LLM."""
        output = []
        for table_name, table_info in schema.items():
            output.append(f"Table: {table_name}")
            if "description" in table_info:
                output.append(f"Description: {table_info['description']}")
            
            columns = table_info.get("columns", [])
            col_strs = []
            for col in columns:
                col_str = f"{col['name']} ({col['type']})"
                if "description" in col:
                    col_str += f" - {col['description']}"
                col_strs.append(col_str)
            
            output.append("Columns:")
            output.append("\n".join(f"  - {c}" for c in col_strs))
            output.append("")
            
        return "\n".join(output)
