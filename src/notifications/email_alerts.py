import smtplib
from email.mime.text import MIMEText
from src.utils.logger import logger
import os

class EmailNotifier:
    def __init__(self, smtp_server, smtp_port, email_address, app_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_address = email_address
        self.app_password = app_password

    def send_alert(self, subject, body):
        if not self.email_address or not self.app_password:
            logger.warning("Email credentials not set. Skipping alert.")
            return

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_address
        msg['To'] = self.email_address # Sending to self

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email_address, self.app_password)
                server.send_message(msg)
            logger.info(f"Email alert sent: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
