# API Query Analysis - Fixed Encryption Issue

## Issue Identification

When testing the `/api/v1/queries/analyze` endpoint, the API was returning a **500 Internal Server Error**. Initial investigation showed the query was being created successfully and intent parsing was working, but the query status was being set to 'FAILED'.

## Root Cause

Added comprehensive error logging and discovered the root cause:

```
cryptography.fernet.InvalidToken
```

The encrypted credentials stored in the data source could not be decrypted because the encryption key in [.env](backend/.env) didn't match the key used to originally encrypt the credentials.

**Error Stack:**
- Location: [app/services/data/executor.py](backend/app/services/data/executor.py) in `get_schema_metadata()`
- Triggered when: Attempting to decrypt data source connection credentials
- Reason: Encryption key mismatch between storage and decryption

## Solution

Created and executed [fix_encryption.py](backend/fix_encryption.py) to re-encrypt the data source credentials with the current encryption key from [.env](backend/.env):

```python
from app.utils.encryption import encrypt_credentials

original_config = {
    "path": "/Users/adarshkasula/Documents/New project/ai-business-analyst/data/demo_analytics.sqlite"
}

encrypted_text = encrypt_credentials(original_config)
```

Updated the database with properly encrypted credentials.

## Verification

After fixing the encryption, the API query now works successfully:

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/queries/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language_query": "Show average order value by state for the last 3 months",
    "data_source_id": "b0d23d4d-9573-432e-b452-d12524c685b8"
  }'
```

**Response:**
- ✅ **Status:** 200 OK
- ✅ **Intent Parsing:** DESCRIPTIVE with correct entities extracted
- ✅ **SQL Generation:** Generated valid SQLite query
- ✅ **Query Execution:** Successfully executed against demo database
- ✅ **Narrative Generation:** Created natural language summary

**Generated SQL:**
```sql
SELECT c.customer_state AS state, AVG(p.payment_value) AS avg_order_value
FROM olist_orders o
JOIN olist_order_payments p ON o.order_id = p.order_id
JOIN olist_customers c ON o.customer_id = c.customer_id
WHERE o.order_purchase_timestamp >= date('now', '-3 months')
GROUP BY c.customer_state
LIMIT 100;
```

## Complete Pipeline Working

The full AI Business Analyst query analysis pipeline is now operational:

1. ✅ Natural language query received
2. ✅ Intent classification (using OpenAI)
3. ✅ Entity extraction (metrics, dimensions, time ranges, filters)
4. ✅ Schema metadata retrieval
5. ✅ SQL generation from natural language
6. ✅ SQL validation and execution
7. ✅ Statistical analysis
8. ✅ Narrative generation

## Frontend UI Access

The frontend is now running and accessible at **http://localhost:5173/**

### Key Features

**Dashboard (`/`):**
- High-level metrics overview (Order Pulse, AOV, Revenue)
- Delivery reliability tracking
- Conversion funnel analytics
- Top categories and revenue trends

**Analysis Console (`/analysis`):**
- Natural language query interface
- Data source selection (Olist + Clickstream Demo)
- Example query templates
- Visual pipeline status showing the AI process:
  - Intent extraction
  - SQL generation
  - Narrative synthesis

## Notes

The query returned no results because the demo database doesn't contain data from the last 3 months (the data is historical). The narrative generator correctly identified this and provided an appropriate message.

## Services Running

- **Backend API:** http://127.0.0.1:8000
- **Frontend UI:** http://localhost:5173
