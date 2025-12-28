import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

class EmailAlertManager:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        # In a real app, these would be configured securely
        self.sender_email = os.getenv("EMAIL_USER", "your_email@gmail.com")
        self.sender_password = os.getenv("EMAIL_PASS", "your_password")

    def send_alert_email(self, recipient_email, crowd_count, threshold):
        """
        Send an alert email when crowd threshold is exceeded
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Crowd Alert - Count: {crowd_count}"

            # Email body
            body = f"""
            Crowd Monitoring Alert

            Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Current Crowd Count: {crowd_count}
            Threshold: {threshold}

            The crowd count has exceeded the configured threshold.
            Please take appropriate action.

            This is an automated message from the Crowd Monitoring System.
            """

            msg.attach(MIMEText(body, 'plain'))

            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)

            # Send email
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient_email, text)
            server.quit()

            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False