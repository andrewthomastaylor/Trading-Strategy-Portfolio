import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
try:
    import config
except ImportError:
    import config_template as config

class EmailNotifier:
    def __init__(self):
        self.sender = config.EMAIL_SENDER
        self.password = config.EMAIL_PASSWORD
        self.receiver = config.EMAIL_RECEIVER

    def send_email(self, subject, body):
        if not self.sender or not self.password or "your_email" in self.sender:
            print(f"Email not configured. Subject: {subject}")
            print(f"Body: {body}")
            return

        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.receiver
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender, self.password)
            text = msg.as_string()
            server.sendmail(self.sender, self.receiver, text)
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

if __name__ == "__main__":
    notifier = EmailNotifier()
    notifier.send_email("Test Subject", "This is a test email from the trading system.")
