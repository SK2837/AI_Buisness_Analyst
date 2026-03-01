import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.core.config import settings

class ReportGenerator:
    """Service for generating and managing reports."""
    
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
    def generate_html_report(self, title: str, sections: List[Dict[str, Any]]) -> str:
        """
        Render a report to HTML.
        
        Args:
            title: Report title
            sections: List of section dictionaries. Each section should have:
                      - title: Section title
                      - narrative: HTML/Text narrative
                      - key_points: List of key points
                      - chart_json: Plotly JSON string (optional)
                      - chart_id: Unique ID for the chart div (optional)
                      
        Returns:
            Rendered HTML string
        """
        template = self.env.get_template("report_base.html")
        
        # Ensure chart_json is properly serialized if it's a dict
        for section in sections:
            if "chart_json" in section and isinstance(section["chart_json"], dict):
                section["chart_json"] = json.dumps(section["chart_json"])
                
        return template.render(
            title=title,
            sections=sections,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    async def create_report(self, db, user_id: str, title: str, content: Dict[str, Any]) -> Any:
        """
        Save report metadata to database.
        (Placeholder for actual DB implementation)
        """
        # TODO: Implement database persistence using the Report model
        pass
