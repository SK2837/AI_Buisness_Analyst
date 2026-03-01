import sqlparse
from typing import List

class SQLValidator:
    """Validator for ensuring SQL safety."""
    
    FORBIDDEN_KEYWORDS = {
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'TRUNCATE', 
        'GRANT', 'REVOKE', 'CREATE', 'REPLACE'
    }
    
    @classmethod
    def validate_sql(cls, sql: str) -> bool:
        """
        Validate that the SQL query is safe (read-only).
        
        Args:
            sql: The SQL query string
            
        Returns:
            True if safe, False otherwise
        """
        if not sql or not sql.strip():
            return False
            
        # Parse the SQL
        parsed = sqlparse.parse(sql)
        
        for statement in parsed:
            # Check token types
            for token in statement.flatten():
                if token.ttype is sqlparse.tokens.Keyword.DML:
                    if token.value.upper() in cls.FORBIDDEN_KEYWORDS:
                        return False
                if token.ttype is sqlparse.tokens.Keyword.DDL:
                    return False
                    
            # Check for specific keywords in the string representation
            # This is a fallback/double-check
            normalized = str(statement).upper()
            for keyword in cls.FORBIDDEN_KEYWORDS:
                # Check for keyword with word boundaries
                # Simple check: keyword at start or preceded by space/newline
                if f" {keyword} " in f" {normalized} ":
                    return False
                    
        return True

    @classmethod
    def extract_tables(cls, sql: str) -> List[str]:
        """
        Extract table names from the SQL query.
        Useful for checking against allowed schema.
        """
        # This is a simplified extraction and might need a more robust parser
        # for complex queries.
        # For now, we rely on the LLM to use correct tables and the database 
        # permissions to enforce access.
        return []
