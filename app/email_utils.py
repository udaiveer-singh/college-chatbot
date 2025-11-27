import smtplib
import os
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SENDER = os.getenv("MAIL_SENDER")
PASSWORD = os.getenv("MAIL_PASSWORD")
RECEIVER = os.getenv("MAIL_RECEIVER")

def send_async_email(subject, body):
    """
    Sends email in a separate thread so the chatbot doesn't freeze.
    """
    def _send():
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER
            msg['To'] = RECEIVER
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            # Connect to Gmail Server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER, PASSWORD)
            text = msg.as_string()
            server.sendmail(SENDER, RECEIVER, text)
            server.quit()
            print("✅ Email Alert Sent Successfully!")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")

    # Run in background thread
    thread = threading.Thread(target=_send)
    thread.start()