import asyncio
from celery import shared_task
from app.models.database import SessionLocal
from app.models.alert import Alert
from app.services.monitoring.alert_engine import AlertEngine
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_all_alerts():
    """
    Periodic task to check all active alerts.
    """
    logger.info("Starting scheduled alert check...")
    db = SessionLocal()
    try:
        # Get all active alerts
        alerts = db.query(Alert).filter(Alert.is_active == True).all()
        logger.info(f"Found {len(alerts)} active alerts.")
        
        engine = AlertEngine(db)
        
        # Run evaluations
        # Note: In a real production app, we might want to dispatch individual 
        # celery tasks for each alert to parallelize execution.
        # For now, we'll run them sequentially in this worker.
        
        # We need to run async code in this sync task
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        for alert in alerts:
            logger.info(f"Evaluating alert: {alert.name} ({alert.id})")
            loop.run_until_complete(engine.evaluate_alert(alert.id))
            
    except Exception as e:
        logger.error(f"Error in check_all_alerts: {e}")
    finally:
        db.close()
        logger.info("Finished scheduled alert check.")
