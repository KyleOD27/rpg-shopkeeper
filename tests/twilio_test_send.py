from twilio.rest import Client
import os
from dotenv import load_dotenv

# 🌱 Load environment variables from .env file
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("FROM_SMS_NUMBER")   # Your Twilio number (must support SMS)
to_number = os.getenv("TO_SMS_NUMBER")       # Your own mobile number

# 🔐 Authenticate Twilio client
client = Client(account_sid, auth_token)

# ✉️ Send SMS message
message = client.messages.create(
    body="📨 SMS test message from RPG Shopkeeper!",
    from_=from_number,
    to=to_number
)

print(f"✅ SMS sent! SID: {message.sid}")
