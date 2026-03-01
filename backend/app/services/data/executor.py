import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Dict, Optional
from app.models.data_source import DataSource
from app.utils.encryption import EncryptionService
from app.core.config import settings

class QueryExecutor:
    """Service for executing SQL queries against data sources."""
    
    def __init__(self):
        self.encryption_service = EncryptionService()
        
    async def execute_query(self, sql: str, data_source: DataSource) -> pd.DataFrame:
        """
        Execute SQL query against a data source.
        
        Args:
            sql: The SQL query to execute
            data_source: The DataSource model instance
            
        Returns:
            Pandas DataFrame with results
        """
        # Get connection string
        connection_string = self._get_connection_string(data_source)
        
        try:
            # Create engine for this specific data source
            # Note: In a production environment, we should cache these engines
            # or use a connection pool manager
            engine = create_engine(connection_string)
            
            # Execute query using pandas
            with engine.connect() as connection:
                df = pd.read_sql_query(text(sql), connection)
                
            return df
            
        except SQLAlchemyError as e:
            raise Exception(f"Database execution error: {str(e)}")
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
            
    def _get_connection_string(self, data_source: DataSource) -> str:
        """Construct SQLAlchemy connection string from data source config."""
        config = data_source.connection_config
        
        # Check if credentials are encrypted
        if "encrypted" in config:
            decrypted = self.encryption_service.decrypt_credentials(config["encrypted"])
            # Merge decrypted credentials with config
            # This assumes decrypted is a dict of credentials
            # In reality, we might need to parse the decrypted string
            # For this implementation, let's assume decrypt_credentials returns a dict
            # But wait, the encryption service returns a string (JSON dump likely)
            import json
            try:
                creds = json.loads(decrypted)
                config.update(creds)
            except json.JSONDecodeError:
                # If it's just a connection string
                return decrypted
        
        source_type = data_source.source_type.value.upper()
        
        if source_type == "POSTGRESQL":
            return f"postgresql://{config.get('username')}:{config.get('password')}@{config.get('host')}:{config.get('port')}/{config.get('database')}"
        elif source_type == "MYSQL":
            return f"mysql+pymysql://{config.get('username')}:{config.get('password')}@{config.get('host')}:{config.get('port')}/{config.get('database')}"
        elif source_type == "SQLSERVER":
            return f"mssql+pyodbc://{config.get('username')}:{config.get('password')}@{config.get('host')}:{config.get('port')}/{config.get('database')}?driver=ODBC+Driver+17+for+SQL+Server"
        elif source_type == "SQLITE":
            # For testing/local files
            sqlite_path = config.get('path') or config.get('database')
            return f"sqlite:///{sqlite_path}"
        
        raise ValueError(f"Unsupported data source type for direct SQL execution: {source_type}")

    def get_schema_metadata(self, data_source: DataSource) -> Dict[str, Any]:
        """Inspect the data source and return table/column metadata."""
        connection_string = self._get_connection_string(data_source)
        engine = create_engine(connection_string)
        inspector = inspect(engine)

        schema: Dict[str, Any] = {}
        for table_name in inspector.get_table_names():
            columns = []
            for col in inspector.get_columns(table_name):
                columns.append({
                    "name": col.get("name"),
                    "type": str(col.get("type"))
                })
            schema[table_name] = {"columns": columns}

        return schema
