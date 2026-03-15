# 🤖 AI Business Analyst — Insight Atlas

An AI-powered virtual business analyst that transforms raw data into actionable insights through natural language interactions. Built on the Brazilian E-Commerce (Olist) dataset.

## 📸 Screenshots

### Dashboard — Live KPIs from Real Data
![Dashboard](screenshots/Dashboard.png)

> The Dashboard pulls live metrics directly from PostgreSQL. It displays **Order Pulse** (total orders, AOV, revenue, cancellation rate for the last 30 days of the dataset), **Delivery Reliability** (on-time %, avg shipping days, late order %), **Order Status Breakdown** (delivered, shipped, canceled, etc.), and **Highlights** (top revenue category, avg review score, active sellers). All numbers are computed in real time — no hardcoded values.

---

### Analysis — Natural Language to SQL to Insights
![Analysis - Query Input](screenshots/Analysis.png)

> The Analysis console is the core AI feature. Type any business question in plain English — the backend uses **GPT-4 to extract intent and entities**, generates **schema-aware SQL**, executes it against the Olist PostgreSQL database, runs **statistical analysis**, and returns an **AI-generated narrative** with key points and raw results. No SQL knowledge required.

![Analysis - Results](screenshots/Analysis2.png)

> After submitting a query, the AI returns a structured response: **Key Points** summarizing the findings, the **raw data table** with query results, and **statistical context**. The entire pipeline — from natural language to insight — runs in seconds.

---

### Reports — Prebuilt Live Reports
![Reports](screenshots/Reports.png)

> The Reports Library contains 5 prebuilt reports that query live Olist data on demand: **Revenue by Product Category**, **Order Status Summary**, **Delivery Performance by State**, **Top 20 Sellers by Revenue**, and **Monthly Order Volume**. Each report opens as a formatted HTML table generated directly from the database.

---

## 📋 Overview

This tool enables executives, managers, and business stakeholders to query business data conversationally and receive comprehensive reports with visualizations and narratives — no SQL or data science expertise required.

**Key Features:**
- 💬 Natural language query interface (GPT-4 powered)
- 📊 Real KPI dashboard from live data
- 📝 AI-generated narrative reports
- 🔗 Multi-source data integration (PostgreSQL, CSV, APIs)
- 📅 Prebuilt and on-demand report generation
- 🔒 Encrypted data source credentials

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
- [x] Database schema and models
- [x] LLM integration  
- [x] Query processing engine
- [x] Data analysis modules
- [x] Visualization generation
- [x] Report generation
- [x] Alert system
- [x] Frontend interface
- [x] Docker deployment
- [x] CI/CD pipeline

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Set your API keys
export OPENAI_API_KEY=your-key-here

# Build and start all services
docker-compose up --build

# Access the application
open http://localhost:8000
```

Services included:
- **Web**: FastAPI backend + React frontend (port 8000)
- **PostgreSQL**: Database (port 5432)
- **Redis**: Message broker and cache (port 6379)
- **Celery Worker**: Background task processing
- **Celery Beat**: Scheduled task execution

### Manual Docker Build

```bash
# Build image
docker build -t ai-business-analyst .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  -e OPENAI_API_KEY=your-key \
  ai-business-analyst
```

## 📡 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

**Query Analysis**
```bash
POST /api/v1/queries/analyze
{
  "natural_language_query": "Show me sales trends for Q4",
  "data_source_id": "datasource-id"
}
```

**Reports**
```bash
POST /api/v1/reports/generate
{
  "title": "Q4 Sales Report",
  "query": "Quarterly sales analysis"
}

GET /api/v1/reports/{report_id}/render
```

**Alerts**
```bash
GET /api/v1/alerts/
POST /api/v1/alerts/
{
  "name": "Low Sales Alert",
  "condition_sql": "SELECT * FROM sales WHERE amount < 1000",
  "schedule_cron": "0 9 * * *"
}
```


## 🤝 Contributing

This is currently a development project. Contribution guidelines will be added once the MVP is complete.


