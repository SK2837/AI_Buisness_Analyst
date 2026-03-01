import logging
from typing import List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_from = settings.SMTP_FROM

    async def send_notification(self, user_email: str, subject: str, message: str, channels: List[str] = None):
        """
        Send a notification to a user.
        
        Args:
            user_email: Recipient email
            subject: Notification subject
            message: Notification body
            channels: List of channels ('email', 'slack', 'console'). Defaults to ['console'].
        """
        if channels is None:
            channels = ["console"]
            
        for channel in channels:
            if channel == "console":
                self._send_console(user_email, subject, message)
            elif channel == "email":
                await self._send_email(user_email, subject, message)
            elif channel == "slack":
                await self._send_slack(user_email, subject, message)
            else:
                logger.warning(f"Unsupported notification channel: {channel}")

    def _send_console(self, user_email: str, subject: str, message: str):
        """Log notification to console/logger."""
        logger.info(f"NOTIFICATION [{user_email}] {subject}: {message}")
        print(f"--- NOTIFICATION ---\nTo: {user_email}\nSubject: {subject}\nMessage: {message}\n--------------------")

    async def _send_email(self, user_email: str, subject: str, message: str):
        """Send notification via Email (SMTP)."""
        if not self.smtp_host or not self.smtp_user:
            logger.warning("SMTP not configured. Skipping email notification.")
            return

        # TODO: Implement actual SMTP sending logic using aiosmtplib or similar
        # For now, just log that we would have sent it
        logger.info(f"Sending email to {user_email} via {self.smtp_host}")

    async def _send_slack(self, user_email: str, subject: str, message: str):
        """Send notification via Slack."""
        # Placeholder for Slack integration
        logger.info(f"Skipping Slack notification for {user_email} (not configured)")
