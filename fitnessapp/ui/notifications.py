import smtplib
from email.mime.text import MIMEText

class EmailNotifier:
    def __init__(self, smtp_server, port, username, password):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password

    def send_notification(self, recipient_email, subject, body):
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = recipient_email

            with smtplib.SMTP_SSL(self.smtp_server, self.port) as server:
                server.login(self.username, self.password)
                server.send_message(msg)
            print(f"Notification sent to {recipient_email}")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
