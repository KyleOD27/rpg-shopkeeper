from twilio.rest import Client
import os
from dotenv import load_dotenv
load_dotenv()
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
from_number = os.getenv('FROM_SMS_NUMBER')
to_number = os.getenv('TO_SMS_NUMBER')
client = Client(account_sid, auth_token)
message = client.messages.create(body=
    '📨 sms test message from RPG Shopkeeper!', from_=from_number, to=to_number)
print(f'✅ sms sent! SID: {message.sid}')
