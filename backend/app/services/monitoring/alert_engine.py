import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.alert import Alert, AlertType
from app.models.alert_execution import AlertExecution, ExecutionStatus
from app.services.data.executor import QueryExecutor
from app.services.analysis.stats_engine import StatsEngine
from app.services.monitoring.notifier import NotificationService

logger = logging.getLogger(__name__)

class AlertEngine:
    """Service for evaluating alerts."""
    
    def __init__(self, db: Session):
        self.db = db
        self.query_executor = QueryExecutor()
        self.stats_engine = StatsEngine()
        self.notifier = NotificationService()

    async def evaluate_alert(self, alert_id: str):
        """
        Evaluate a specific alert rule.
        """
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert or not alert.is_active:
            return

        execution = AlertExecution(
            alert_id=alert.id,
            status=ExecutionStatus.NOT_TRIGGERED, # Default
            executed_at=datetime.utcnow()
        )
        self.db.add(execution)
        self.db.commit()

        try:
            # 1. Fetch Data
            # Assuming alert.query_id points to a saved query, or we use alert.config['sql']
            # For this implementation, let's assume the alert config contains the SQL
            sql = alert.config.get("sql")
            if not sql:
                raise ValueError("No SQL query defined for alert")

            df = await self.query_executor.execute_query(sql, alert.data_source)
            
            # 2. Evaluate Condition
            is_triggered = False
            trigger_value = None
            message = ""

            if alert.type == AlertType.THRESHOLD:
                is_triggered, trigger_value, message = self._check_threshold(df, alert.config)
            elif alert.type == AlertType.ANOMALY:
                is_triggered, trigger_value, message = self._check_anomaly(df, alert.config)
            
            # 3. Update Execution Status
            execution.status = ExecutionStatus.TRIGGERED if is_triggered else ExecutionStatus.NOT_TRIGGERED
            execution.result_data = {"value": trigger_value, "message": message}
            
            # 4. Notify if triggered
            if is_triggered:
                await self.notifier.send_notification(
                    user_email="user@example.com", # TODO: Get from alert.owner
                    subject=f"Alert Triggered: {alert.name}",
                    message=message,
                    channels=alert.channels
                )
                alert.last_triggered_at = datetime.utcnow()
                execution.notification_sent = True

        except Exception as e:
            logger.error(f"Error evaluating alert {alert_id}: {e}")
            execution.status = ExecutionStatus.ERROR
            execution.error_message = str(e)
        
        finally:
            self.db.commit()

    def _check_threshold(self, df, config) -> tuple[bool, Any, str]:
        """Check if data exceeds a threshold."""
        column = config.get("column")
        operator = config.get("operator") # >, <, >=, <=, ==
        threshold = config.get("threshold")
        
        if df.empty or column not in df.columns:
            return False, None, "Data empty or column missing"

        # Check latest value
        value = df[column].iloc[-1]
        
        triggered = False
        if operator == ">" and value > threshold:
            triggered = True
        elif operator == "<" and value < threshold:
            triggered = True
        elif operator == ">=" and value >= threshold:
            triggered = True
        elif operator == "<=" and value <= threshold:
            triggered = True
        elif operator == "==" and value == threshold:
            triggered = True
            
        return triggered, float(value), f"Value {value} {operator} {threshold}"

    def _check_anomaly(self, df, config) -> tuple[bool, Any, str]:
        """Check for anomalies in data."""
        column = config.get("column")
        method = config.get("method", "zscore")
        
        anomalies = self.stats_engine.detect_anomalies(df, column, method=method)
        
        # Check if the LATEST row is an anomaly
        if anomalies:
            # This is a simplification. We should check if the last row is in the anomalies list.
            # Assuming detect_anomalies returns a list of dicts with values.
            # We need to match by index or timestamp if possible.
            # For now, let's just check if ANY anomaly was found in the window
            # But typically alerts are for "current" state.
            
            # Let's assume we want to know if the *latest* data point is anomalous
            last_val = df[column].iloc[-1]
            for anomaly in anomalies:
                # If values match (weak check)
                if anomaly.get(column) == last_val:
                    return True, float(last_val), f"Anomaly detected: {anomaly.get('anomaly_reason')}"
                    
        return False, None, "No anomaly detected"
