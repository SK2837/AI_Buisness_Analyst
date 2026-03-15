from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.database import get_db

router = APIRouter()

PREDEFINED_REPORTS = [
    {
        "id": "revenue-by-category",
        "title": "Revenue by Product Category",
        "description": "Total revenue broken down by product category",
    },
    {
        "id": "order-status-summary",
        "title": "Order Status Summary",
        "description": "Count of orders by status across the dataset",
    },
    {
        "id": "delivery-performance",
        "title": "Delivery Performance",
        "description": "On-time vs late deliveries by seller state",
    },
    {
        "id": "top-sellers",
        "title": "Top Sellers by Revenue",
        "description": "Top 20 sellers ranked by total revenue",
    },
    {
        "id": "monthly-orders",
        "title": "Monthly Order Volume",
        "description": "Number of orders and revenue per month",
    },
]


@router.get("/")
def list_reports():
    return PREDEFINED_REPORTS


@router.get("/{report_id}/render", response_class=HTMLResponse)
def render_report(report_id: str, db: Session = Depends(get_db)):
    queries = {
        "revenue-by-category": {
            "title": "Revenue by Product Category",
            "sql": """
                SELECT
                    COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') AS category,
                    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
                    COUNT(DISTINCT oi.order_id) AS total_orders
                FROM olist_order_items oi
                JOIN olist_products p ON oi.product_id = p.product_id
                LEFT JOIN product_category_translation t ON p.product_category_name = t.product_category_name
                GROUP BY category
                ORDER BY total_revenue DESC
                LIMIT 20
            """,
        },
        "order-status-summary": {
            "title": "Order Status Summary",
            "sql": """
                SELECT order_status, COUNT(*) AS total_orders,
                    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) AS pct
                FROM olist_orders
                GROUP BY order_status
                ORDER BY total_orders DESC
            """,
        },
        "delivery-performance": {
            "title": "Delivery Performance by State",
            "sql": """
                SELECT
                    c.customer_state AS state,
                    COUNT(*) AS total_orders,
                    SUM(CASE WHEN o.order_delivered_customer_date::timestamp <= o.order_estimated_delivery_date::timestamp THEN 1 ELSE 0 END) AS on_time,
                    SUM(CASE WHEN o.order_delivered_customer_date::timestamp > o.order_estimated_delivery_date::timestamp THEN 1 ELSE 0 END) AS late,
                    ROUND(100.0 * SUM(CASE WHEN o.order_delivered_customer_date::timestamp <= o.order_estimated_delivery_date::timestamp THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0), 1) AS on_time_pct
                FROM olist_orders o
                JOIN olist_customers c ON o.customer_id = c.customer_id
                WHERE o.order_status = 'delivered'
                  AND o.order_delivered_customer_date IS NOT NULL
                GROUP BY c.customer_state
                ORDER BY total_orders DESC
                LIMIT 20
            """,
        },
        "top-sellers": {
            "title": "Top 20 Sellers by Revenue",
            "sql": """
                SELECT
                    oi.seller_id,
                    s.seller_city, s.seller_state,
                    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
                    COUNT(DISTINCT oi.order_id) AS total_orders
                FROM olist_order_items oi
                JOIN olist_sellers s ON oi.seller_id = s.seller_id
                GROUP BY oi.seller_id, s.seller_city, s.seller_state
                ORDER BY total_revenue DESC
                LIMIT 20
            """,
        },
        "monthly-orders": {
            "title": "Monthly Order Volume",
            "sql": """
                SELECT
                    TO_CHAR(order_purchase_timestamp::timestamp, 'YYYY-MM') AS month,
                    COUNT(*) AS total_orders,
                    ROUND(SUM(p.payment_value)::numeric, 2) AS total_revenue
                FROM olist_orders o
                JOIN olist_order_payments p ON o.order_id = p.order_id
                WHERE p.payment_sequential = 1
                GROUP BY month
                ORDER BY month
            """,
        },
    }

    if report_id not in queries:
        return HTMLResponse("<h2>Report not found</h2>", status_code=404)

    q = queries[report_id]
    rows = db.execute(text(q["sql"])).fetchall()
    cols = db.execute(text(q["sql"])).keys() if rows else []
    cols = list(rows[0]._mapping.keys()) if rows else []

    rows_html = "".join(
        "<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>"
        for row in rows
    )
    headers_html = "".join(f"<th>{c}</th>" for c in cols)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{q['title']}</title>
        <style>
            body {{ font-family: -apple-system, sans-serif; padding: 40px; color: #1a1a1a; }}
            h1 {{ font-size: 24px; margin-bottom: 8px; }}
            p {{ color: #666; margin-bottom: 24px; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
            th {{ background: #f4f4f5; text-align: left; padding: 10px 14px; border-bottom: 2px solid #e4e4e7; }}
            td {{ padding: 9px 14px; border-bottom: 1px solid #f0f0f0; }}
            tr:hover td {{ background: #fafafa; }}
        </style>
    </head>
    <body>
        <h1>{q['title']}</h1>
        <p>Generated from Olist Brazilian E-Commerce dataset &mdash; {len(rows)} rows</p>
        <table>
            <thead><tr>{headers_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
