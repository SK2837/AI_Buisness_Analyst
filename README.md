# 🤖 AI Business Analyst

An AI-powered virtual business analyst that transforms raw data into actionable insights through natural language interactions.

## 📋 Overview

This tool enables executives, managers, and business stakeholders to query business data conversationally and receive comprehensive reports with visualizations and narratives—no SQL or data science expertise required.

**Key Features:**
- 💬 Natural language query interface
- 📊 Automatic chart generation
- 📝 AI-generated narrative reports
- 🔔 Proactive insights and alerts
- 🔗 Multi-source data integration
- 📅 Scheduled report generation

## 🏗️ Architecture

```
ai-business-analyst/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Configuration
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   └── tests/           # Backend tests
├── frontend/            # React frontend (coming soon)
├── data/               # Sample datasets
└── docker-compose.yml  # Docker orchestration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)
- Redis (or use Docker)

### Installation

1. **Clone the repository**
   ```bash
   cd /path/to/ai-business-analyst
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your API keys
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Verify services are running**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs
   - Flower (Celery monitoring): http://localhost:5555

### Alternative: Local Development

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database**
   ```bash
   # Make sure PostgreSQL is running
   # Update DATABASE_URL in .env
   ```

4. **Run the application**
   ```bash
   python -m app.main
   # or
   uvicorn app.main:app --reload
   ```

## 📖 Documentation

- **[Requirements](requirements.md)** - Functional and non-functional requirements
- **[Implementation Plan](implementation_plan.md)** - Technical architecture and roadmap
- **[Task List](task.md)** - Development checklist

## 🔑 Environment Variables

Key configuration options (see `.env.example` for complete list):

```bash
# LLM Provider
OPENAI_API_KEY=your-key-here
# or
ANTHROPIC_API_KEY=your-key-here

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_query_processor.py
```

## 📊 Example Usage

**Coming soon:** Once the API is fully implemented, you'll be able to:

```python
import requests

# Submit a natural language query
response = requests.post("http://localhost:8000/api/v1/query", json={
    "query": "Why did our sales dip in the Midwest last quarter?"
})

# Get generated report
report = response.json()
print(report["narrative"])
print(report["charts"])
```

## 🛠️ Technology Stack

**Backend:**
- FastAPI - Modern async web framework
- SQLAlchemy - ORM for database operations
- LangChain - LLM orchestration
- Celery - Background task processing
- Redis - Caching and message broker
- PostgreSQL - Primary database

**Frontend (Planned):**
- React + TypeScript
- Material-UI or Shadcn/UI
- Recharts or Plotly.js

## 📈 Development Status

- [x] Project setup and infrastructure
- [ ] Database schema and models
- [ ] LLM integration
- [ ] Query processing engine
- [ ] Data analysis modules
- [ ] Visualization generation
- [ ] Report generation
- [ ] Alert system
- [ ] Frontend interface

## 🤝 Contributing

This is currently a development project. Contribution guidelines will be added once the MVP is complete.

## 📝 License

TBD

## 📧 Contact

For questions or feedback, please open an issue.

---

**Built with ❤️ using AI-powered development**
