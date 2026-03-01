# 🚀 Getting Started with AI Business Analyst

This guide will walk you through setting up and using the AI Business Analyst tool to analyze your own data.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation & Setup](#installation--setup)
3. [Running the Application](#running-the-application)
4. [Adding Your Data Source](#adding-your-data-source)
5. [Analyzing Your Data](#analyzing-your-data)
6. [Generating Reports](#generating-reports)
7. [Setting Up Alerts](#setting-up-alerts)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

- **Docker & Docker Compose** installed ([Get Docker](https://docs.docker.com/get-docker/))
- **OpenAI API Key** or **Anthropic API Key** ([OpenAI](https://platform.openai.com/api-keys) | [Anthropic](https://console.anthropic.com/))
- **Your data in a supported database**:
  - PostgreSQL
  - MySQL
  - SQLite
  - MongoDB (planned)

---

## Installation & Setup

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd ai-business-analyst
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file and add your API key:

```bash
# LLM Provider (choose one)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here

# OR use Anthropic
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=your-anthropic-key-here

# Security (generate secure keys for production)
SECRET_KEY=your-secret-key-change-in-production
ENCRYPTION_KEY=your-32-byte-encryption-key-here

# Database (uses Docker PostgreSQL by default)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_business_analyst

# Redis & Celery (uses Docker services by default)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

> **Security Note**: For production, generate strong random keys:
> ```bash
> # Generate SECRET_KEY
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> 
> # Generate ENCRYPTION_KEY (must be 32 bytes)
> python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
> ```

---

## Running the Application

### Using Docker Compose (Recommended)

This will start all required services: web app, database, redis, and background workers.

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

**Services will be available at:**
- 🌐 **Web Application**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs
- 📖 **API ReDoc**: http://localhost:8000/redoc

### Verify Installation

Open your browser and navigate to http://localhost:8000/docs. You should see the Swagger UI with all available API endpoints.

---

## Adding Your Data Source

To analyze your data, you first need to connect your database to the AI Business Analyst.

### Option 1: Using the API (Recommended)

#### 1. Create a Data Source via API

```bash
curl -X POST "http://localhost:8000/api/v1/data_sources/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Sales Database",
    "source_type": "postgresql",
    "connection_config": {
      "host": "your-db-host.com",
      "port": 5432,
      "database": "sales_db",
      "user": "your_username",
      "password": "your_password"
    },
    "description": "Production sales database"
  }'
```

**Supported `source_type` values:**
- `postgresql`
- `mysql`
- `sqlite`

**Example for MySQL:**
```json
{
  "name": "MySQL Analytics DB",
  "source_type": "mysql",
  "connection_config": {
    "host": "localhost",
    "port": 3306,
    "database": "analytics",
    "user": "analyst",
    "password": "secure_password"
  }
}
```

**Example for SQLite:**
```json
{
  "name": "Local SQLite",
  "source_type": "sqlite",
  "connection_config": {
    "database": "/path/to/your/database.db"
  }
}
```

#### 2. Verify Data Source Connection

```bash
# List all data sources
curl http://localhost:8000/api/v1/data_sources/
```

The response will include your data source with an `id`. **Save this ID** - you'll need it for queries.

### Option 2: Using the Frontend

1. Navigate to http://localhost:8000 (frontend)
2. Go to **Settings** or **Data Sources**
3. Click **Add Data Source**
4. Fill in the connection details
5. Click **Test Connection** → **Save**

### Security Note

All database credentials are **encrypted** before storage using Fernet encryption. The encryption key is stored in your `.env` file.

---

## Hands-on Demo Data (Olist + Clickstream)

To make the app immediately usable, load the demo datasets into SQLite:

1. Download clickstream data:
   ```bash
   python data/download_clickstream.py
   ```
2. Download the Olist Kaggle dataset and extract it into:
   ```
   data/olist/
   ```
3. Build the SQLite database:
   ```bash
   python data/prepare_sqlite.py
   ```
4. Point your backend to SQLite:
   ```
   DATABASE_URL=sqlite:////Users/adarshkasula/Documents/New project/ai-business-analyst/data/demo_analytics.sqlite
   ```
5. Create a data source via API:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/data_sources/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Olist + Clickstream Demo",
       "source_type": "sqlite",
       "connection_config": { "path": "/Users/adarshkasula/Documents/New project/ai-business-analyst/data/demo_analytics.sqlite" }
     }'
   ```

## Analyzing Your Data

Now that your data source is connected, you can start asking questions in natural language!

### Using the API

```bash
curl -X POST "http://localhost:8000/api/v1/queries/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language_query": "What were the total sales by region last month?",
    "data_source_id": "your-data-source-id-here",
    "user_id": "user-123"
  }'
```

**Response:**
```json
{
  "query_id": "abc-123",
  "natural_language_query": "What were the total sales by region last month?",
  "generated_sql": "SELECT region, SUM(amount) FROM sales WHERE ...",
  "results": [
    {"region": "North", "total_sales": 50000},
    {"region": "South", "total_sales": 45000}
  ],
  "narrative": {
    "summary": "Sales performance shows the North region leading with $50,000...",
    "detailed_analysis": "...",
    "recommendations": ["Focus on South region growth..."]
  },
  "status": "completed"
}
```

### Using the Frontend

1. Navigate to http://localhost:8000
2. Go to the **Analysis** page
3. Type your question in natural language:
   - "Show me sales trends for the last 6 months"
   - "Which products have the highest revenue?"
   - "Why did customer churn increase in Q3?"
4. Click **Analyze**
5. View the results:
   - **SQL Query**: See the generated SQL
   - **Data Table**: View the raw results
   - **Visualizations**: Interactive charts
   - **Narrative**: AI-generated insights and recommendations

### Example Questions You Can Ask

**Sales Analysis:**
- "What are our top 10 products by revenue this year?"
- "Show me monthly sales trends for 2024"
- "Which sales regions are underperforming?"

**Customer Analysis:**
- "What is our customer retention rate by cohort?"
- "Who are our highest value customers?"
- "What is the average customer lifetime value?"

**Operational:**
- "Which inventory items are below reorder point?"
- "Show me order fulfillment times by warehouse"
- "What is our average response time by support channel?"

---

## Generating Reports

Reports combine multiple queries, visualizations, and narratives into professional documents.

### Creating a Report

```bash
curl -X POST "http://localhost:8000/api/v1/reports/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Q4 2024 Sales Performance",
    "query": "Comprehensive analysis of Q4 sales across all regions and products"
  }'
```

**Response:**
```json
{
  "report_id": "report-xyz-789",
  "status": "processing",
  "url": "/api/v1/reports/report-xyz-789"
}
```

### Viewing a Report

**HTML Version:**
```bash
curl http://localhost:8000/api/v1/reports/report-xyz-789/render
```

**Via Frontend:**
1. Go to **Reports** page
2. Click on your report
3. View the interactive HTML report with charts and insights

### Scheduling Reports

To generate reports automatically (e.g., weekly sales summary):

```bash
curl -X POST "http://localhost:8000/api/v1/reports/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weekly Sales Summary",
    "is_scheduled": true,
    "schedule_config": {
      "cron": "0 9 * * MON",
      "recipients": ["team@company.com"]
    }
  }'
```

This will generate a report every Monday at 9 AM.

---

## Setting Up Alerts

Get proactive notifications when important metrics change.

### Creating an Alert

```bash
curl -X POST "http://localhost:8000/api/v1/alerts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Low Inventory Alert",
    "data_source_id": "your-data-source-id",
    "condition_sql": "SELECT * FROM inventory WHERE quantity < reorder_point",
    "schedule_cron": "0 */6 * * *",
    "notification_channels": ["email"],
    "notification_config": {
      "email": {
        "recipients": ["inventory@company.com"]
      }
    },
    "is_active": true
  }'
```

**Common Alert Patterns:**

**Daily Revenue Check:**
```json
{
  "name": "Daily Revenue Below Target",
  "condition_sql": "SELECT SUM(amount) as revenue FROM sales WHERE date = CURRENT_DATE HAVING revenue < 10000",
  "schedule_cron": "0 20 * * *"
}
```

**Customer Churn Warning:**
```json
{
  "name": "High Churn Rate",
  "condition_sql": "SELECT COUNT(*) FROM cancellations WHERE date >= CURRENT_DATE - INTERVAL '7 days' HAVING COUNT(*) > 50",
  "schedule_cron": "0 9 * * MON"
}
```

---

## Troubleshooting

### Common Issues

**1. "Connection refused" error when accessing http://localhost:8000**

Check if services are running:
```bash
docker-compose ps
```

Restart services:
```bash
docker-compose down
docker-compose up --build
```

**2. "Database connection failed"**

- Verify your database is accessible from Docker
- If using `localhost`, change to `host.docker.internal` (Mac/Windows) or `172.17.0.1` (Linux)
- Check firewall settings

**3. "LLM API error" or "Rate limit exceeded"**

- Verify your API key is correct in `.env`
- Check your API usage/quota
- For testing, use a lower temperature or fewer requests

**4. Data source schema not detected**

Manually refresh the schema:
```bash
curl -X POST "http://localhost:8000/api/v1/data_sources/{id}/refresh-schema"
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs celery-worker

# Follow logs in real-time
docker-compose logs -f web
```

### Resetting the Database

If you need to start fresh:

```bash
# Stop services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Restart
docker-compose up --build
```

---

## Next Steps

Now that you're set up, explore these advanced features:

1. **Custom Visualizations**: Customize chart types and styling
2. **Advanced Analytics**: Implement custom analysis modules
3. **Multi-Source Queries**: Combine data from multiple databases
4. **Export Options**: Export reports as PDF or PowerPoint
5. **API Integration**: Integrate with your existing tools via API

For detailed API documentation, visit http://localhost:8000/docs

---

## Need Help?

- 📚 **Documentation**: See [README.md](README.md)
- 🐛 **Issues**: Report bugs on GitHub
- 💬 **Questions**: Open a discussion

**Happy Analyzing! 🎉**
