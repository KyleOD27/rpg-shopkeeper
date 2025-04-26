# sms_webhook.py

from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import logging
import os
from dotenv import load_dotenv
from integrations.sms.sms_router import handle_sms_command
from app.config import RuntimeFlags  # ✅ Import runtime debug flag
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import logging

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

# 🐛 Use DEBUG log level if RuntimeFlags.DEBUG_MODE is on
logging.basicConfig(
    level=logging.DEBUG if RuntimeFlags.DEBUG_MODE else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Still print to console
        logging.FileHandler("sms_debug.log", mode="a")  # Also write to file
    ]
)

@app.route("/sms", methods=["POST"])
def sms():
    try:
        # --- Parse incoming form data ---
        form_data = request.form.to_dict()
        app.logger.debug(f"📨 Full form data received: {form_data}")

        sender = form_data.get("From", "").strip()
        body = form_data.get("Body", "").strip()

        if not sender or not body:
            app.logger.warning(f"⚠️ Missing sender or body! Sender: '{sender}', Body: '{body}'")
            return Response("<Response><Message>Invalid message received.</Message></Response>", mimetype="application/xml")

        app.logger.info(f"📩 SMS received from {sender}: '{body}' (length: {len(body)})")

        # --- Try handling the SMS command ---
        try:
            reply = handle_sms_command(sender=sender, text=body)
        except Exception as e:
            app.logger.error("❌ Error inside handle_sms_command", exc_info=True)
            reply = "Oops! Something went wrong talking to the shopkeeper. Please tell the Game Master."

        # --- Respond to Twilio ---
        resp = MessagingResponse()
        resp.message(reply)
        app.logger.info(f"📤 Responding to {sender} with: '{reply}'")

        return Response(str(resp), mimetype="application/xml")

    except Exception as e:
        app.logger.error("❌ Top-level error in /sms route", exc_info=True)
        return Response("<Response><Message>Major error occurred. Please try again later.</Message></Response>", mimetype="application/xml")



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

    app.logger.info(f"🚡 Starting Flask server on port {port}")
    app.run(port=port, debug=RuntimeFlags.DEBUG_MODE, host="0.0.0.0")
