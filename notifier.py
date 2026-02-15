import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
try:
    import config
except ImportError:
    import config_template as config

def send_email_alert(subject, body):
    """Sends an email alert if configured."""
    sender = config.EMAIL_SENDER
    password = config.EMAIL_PASSWORD
    receiver = config.EMAIL_RECEIVER

    if not sender or not password or "your_email" in sender:
        print(f"Email Alert (Not Configured): {subject}\n{body}")
        return

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print("Email alert sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")
