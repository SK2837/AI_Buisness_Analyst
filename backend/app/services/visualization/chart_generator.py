import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from typing import Dict, Any, Optional, List

class ChartGenerator:
    """Service for generating Plotly charts."""

    @staticmethod
    def generate_chart(
        df: pd.DataFrame, 
        chart_type: str, 
        x_col: str, 
        y_col: str, 
        title: Optional[str] = None,
        color_col: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a Plotly chart configuration.
        
        Args:
            df: Data to visualize
            chart_type: 'line', 'bar', 'scatter', 'pie', 'histogram'
            x_col: Column for X-axis
            y_col: Column for Y-axis
            title: Chart title
            color_col: Column for color grouping
            
        Returns:
            Dictionary containing Plotly JSON configuration (data and layout)
        """
        if df.empty:
            return {}
            
        try:
            if chart_type == 'line':
                fig = px.line(df, x=x_col, y=y_col, title=title, color=color_col)
            elif chart_type == 'bar':
                fig = px.bar(df, x=x_col, y=y_col, title=title, color=color_col)
            elif chart_type == 'scatter':
                fig = px.scatter(df, x=x_col, y=y_col, title=title, color=color_col)
            elif chart_type == 'pie':
                fig = px.pie(df, values=y_col, names=x_col, title=title)
            elif chart_type == 'histogram':
                fig = px.histogram(df, x=x_col, title=title, color=color_col)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
                
            # Update layout for better aesthetics
            fig.update_layout(
                template="plotly_white",
                margin=dict(l=40, r=40, t=40, b=40),
                font=dict(family="Inter, sans-serif")
            )
            
            # Return as JSON-compatible dict
            return json.loads(fig.to_json())
            
        except Exception as e:
            # Fallback or error handling
            print(f"Error generating chart: {e}")
            return {"error": str(e)}

    @staticmethod
    def recommend_chart_type(df: pd.DataFrame, x_col: str, y_col: str) -> str:
        """
        Heuristic to recommend the best chart type.
        """
        # If X axis is datetime, prefer Line
        if pd.api.types.is_datetime64_any_dtype(df[x_col]):
            return 'line'
            
        # If X axis has many unique values (categorical), prefer Bar
        if df[x_col].nunique() < 20:
            return 'bar'
            
        # Default to Scatter for numeric X
        if pd.api.types.is_numeric_dtype(df[x_col]):
            return 'scatter'
            
        return 'bar'
