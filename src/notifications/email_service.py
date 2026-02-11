import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.utils.logger import logger

class EmailService:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587, sender_email=None, app_password=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email or os.getenv("EMAIL_SENDER")
        self.app_password = app_password or os.getenv("EMAIL_APP_PASSWORD")

    def send_email(self, subject, body, to_email=None):
        if not self.sender_email or not self.app_password:
            logger.warning("Email credentials not set. Skipping email alert.")
            return False

        target_email = to_email or self.sender_email

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = target_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.app_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, target_email, text)
            server.quit()

            logger.info(f"Email sent to {target_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
