from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.database import get_db

router = APIRouter()


@router.get("/kpis")
def get_dashboard_kpis(db: Session = Depends(get_db)):
    """Calculate real KPIs from Olist data."""

    # --- Order Pulse (last 30 days relative to dataset max date) ---
    order_pulse = db.execute(text("""
        WITH max_date AS (SELECT MAX(order_purchase_timestamp::timestamp) AS md FROM olist_orders)
        SELECT
            COUNT(*) AS total_orders,
            ROUND(AVG(p.payment_value)::numeric, 2) AS avg_order_value,
            ROUND(SUM(p.payment_value)::numeric, 2) AS total_revenue,
            ROUND(100.0 * SUM(CASE WHEN o.order_status = 'canceled' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) AS cancel_rate
        FROM olist_orders o
        JOIN olist_order_payments p ON o.order_id = p.order_id
        CROSS JOIN max_date
        WHERE o.order_purchase_timestamp::timestamp >= max_date.md - INTERVAL '30 days'
          AND p.payment_sequential = 1
    """)).fetchone()

    # --- Previous 30 days for comparison ---
    prev_pulse = db.execute(text("""
        WITH max_date AS (SELECT MAX(order_purchase_timestamp::timestamp) AS md FROM olist_orders)
        SELECT COUNT(*) AS total_orders
        FROM olist_orders
        CROSS JOIN max_date
        WHERE order_purchase_timestamp::timestamp >= max_date.md - INTERVAL '60 days'
          AND order_purchase_timestamp::timestamp < max_date.md - INTERVAL '30 days'
    """)).fetchone()

    # --- Delivery Reliability ---
    delivery = db.execute(text("""
        SELECT
            COUNT(*) AS total_delivered,
            ROUND(100.0 * SUM(CASE WHEN order_delivered_customer_date::timestamp <= order_estimated_delivery_date::timestamp THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) AS on_time_pct,
            ROUND(AVG(EXTRACT(EPOCH FROM (order_delivered_carrier_date::timestamp - order_purchase_timestamp::timestamp)) / 86400)::numeric, 1) AS avg_ship_days,
            ROUND(100.0 * SUM(CASE WHEN order_delivered_customer_date::timestamp > order_estimated_delivery_date::timestamp THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) AS late_pct
        FROM olist_orders
        WHERE order_status = 'delivered'
          AND order_delivered_customer_date IS NOT NULL
          AND order_estimated_delivery_date IS NOT NULL
          AND order_delivered_carrier_date IS NOT NULL
    """)).fetchone()

    # --- Top Category ---
    top_category = db.execute(text("""
        SELECT
            COALESCE(t.product_category_name_english, p.product_category_name) AS category,
            ROUND(SUM(oi.price)::numeric, 2) AS revenue
        FROM olist_order_items oi
        JOIN olist_products p ON oi.product_id = p.product_id
        LEFT JOIN product_category_translation t ON p.product_category_name = t.product_category_name
        GROUP BY category
        ORDER BY revenue DESC
        LIMIT 1
    """)).fetchone()

    # --- Order Status Breakdown ---
    statuses = db.execute(text("""
        SELECT order_status, COUNT(*) AS count
        FROM olist_orders
        GROUP BY order_status
        ORDER BY count DESC
    """)).fetchall()

    # --- Review Score ---
    review = db.execute(text("""
        SELECT ROUND(AVG(review_score)::numeric, 1) AS avg_score
        FROM olist_order_reviews
    """)).fetchone()

    # --- Unique Sellers ---
    sellers = db.execute(text("""
        SELECT COUNT(DISTINCT seller_id) AS total_sellers FROM olist_sellers
    """)).fetchone()

    # Build response
    current_orders = order_pulse.total_orders or 0
    prev_orders = prev_pulse.total_orders or 1
    order_change = round((current_orders - prev_orders) / prev_orders * 100, 1)

    return {
        "order_pulse": {
            "total_orders": current_orders,
            "order_change_pct": order_change,
            "avg_order_value": float(order_pulse.avg_order_value or 0),
            "total_revenue": float(order_pulse.total_revenue or 0),
            "cancel_rate": float(order_pulse.cancel_rate or 0),
        },
        "delivery": {
            "on_time_pct": float(delivery.on_time_pct or 0),
            "avg_ship_days": float(delivery.avg_ship_days or 0),
            "late_pct": float(delivery.late_pct or 0),
            "total_delivered": int(delivery.total_delivered or 0),
        },
        "top_category": {
            "name": top_category.category if top_category else "N/A",
            "revenue": float(top_category.revenue) if top_category else 0,
        },
        "order_statuses": [
            {"status": row.order_status, "count": row.count} for row in statuses
        ],
        "avg_review_score": float(review.avg_score or 0),
        "total_sellers": int(sellers.total_sellers or 0),
    }
