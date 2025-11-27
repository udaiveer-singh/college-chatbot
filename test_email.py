import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

SENDER = os.getenv("MAIL_SENDER")
PASSWORD = os.getenv("MAIL_PASSWORD")
RECEIVER = os.getenv("MAIL_RECEIVER")

print(f"Attempting to login as: {SENDER}")

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SENDER, PASSWORD)
    print("✅ SUCCESS! Password accepted.")
    
    server.sendmail(SENDER, RECEIVER, "Subject: Test\n\nThis is a test email.")
    print("✅ Email sent!")
    server.quit()
except Exception as e:
    print(f"❌ ERROR: {e}")