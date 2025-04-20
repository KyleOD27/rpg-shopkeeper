from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import logging
import os
from dotenv import load_dotenv
from SMS.sms_router import handle_sms_command

# 🌱 Load environment variables
load_dotenv()
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TO_NUMBER = os.getenv("TO_SMS_NUMBER")
FROM_NUMBER = os.getenv("FROM_SMS_NUMBER")
MESSAGING_SERVICE_SID = os.getenv("MESSAGING_SERVICE_SID")
NGROK_URL = os.getenv("NGROK_URL")

# 📦 Setup
app = Flask(__name__)
client = Client(ACCOUNT_SID, AUTH_TOKEN)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

@app.route("/sms", methods=["POST"])
def sms():
    try:
        form_data = request.form.to_dict()
        app.logger.debug(f"📨 Raw form data: {form_data}")

        sender = form_data.get("From", "")
        body = form_data.get("Body", "").strip()
        app.logger.info(f"📩 Received SMS from {sender}: {body}")

        # 🧙 Route to RPG Shopkeeper logic
        reply = handle_sms_command(sender=sender, text=body)
        app.logger.info(f"📤 Responding with: {reply}")

        resp = MessagingResponse()
        resp.message(reply)
        return Response(str(resp), mimetype="application/xml")

    except Exception as e:
        app.logger.error("❌ Error in /sms route", exc_info=True)
        return Response("<Response><Message>Oops! Something broke.</Message></Response>", mimetype="application/xml")

def send_startup_sms():
    try:
        params = {
            "body": "📦 Shopkeeper is online!",
            "to": TO_NUMBER
        }

        if MESSAGING_SERVICE_SID:
            params["messaging_service_sid"] = MESSAGING_SERVICE_SID
        elif FROM_NUMBER:
            params["from_"] = FROM_NUMBER
        else:
            raise ValueError("❌ FROM_SMS_NUMBER or MESSAGING_SERVICE_SID required")

        message = client.messages.create(**params)
        app.logger.info(f"✅ Startup SMS sent: SID {message.sid}")

    except Exception as e:
        app.logger.warning(f"⚠️ Could not send startup SMS: {e}")

def start_sms_server():
    port = 5000
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        app.logger.info(f"🔗 Ensure Twilio webhook points to: {NGROK_URL}/sms")
        send_startup_sms()

    app.logger.info(f"🛡️ Starting Flask server on port {port}")
    app.run(port=port, debug=True, host="0.0.0.0")

