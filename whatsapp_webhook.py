from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from pyngrok import ngrok
from whatsapp_router import handle_whatsapp_command
import logging
import os
from dotenv import load_dotenv, set_key, dotenv_values
import time

# 🔧 Logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# 🌱 Load environment variables
env_path = ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    app.logger.debug("📬 Incoming POST to /whatsapp")

    form_data = dict(request.form)
    app.logger.debug(f"📦 Form data received: {form_data}")

    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")

    if not sender:
        app.logger.warning("⚠️ No 'From' field found in request")
    if not incoming_msg:
        app.logger.warning("⚠️ No 'Body' field found in request")

    app.logger.info(f"[RECEIVED] 📲 From {sender}: {incoming_msg}")

    try:
        start_time = time.time()

        app.logger.debug("🧠 Routing to handler...")
        response_text = handle_whatsapp_command(sender=sender, text=incoming_msg)

        duration = time.time() - start_time
        app.logger.info(f"[REPLY] 📤 To {sender} ({duration:.2f}s): {response_text}")

    except Exception as e:
        app.logger.error("❌ Exception occurred in message handling", exc_info=True)
        response_text = "Oops! Something went wrong. Please try again."

    # 💬 Build Twilio response
    try:
        resp = MessagingResponse()
        resp.message(response_text)
        app.logger.debug("✅ TwiML response successfully created.")
        return Response(str(resp), mimetype="application/xml")
    except Exception as e:
        app.logger.critical("💥 Failed to create TwiML response!", exc_info=True)
        return Response("<Response><Message>Internal error occurred.</Message></Response>", mimetype="application/xml")

if __name__ == "__main__":
    port = 5000

    if __name__ == "__main__":
        port = 5000
        static_ngrok_url = os.getenv("NGROK_URL", "https://your-static-url.ngrok-free.app")

        app.logger.info("🌐 Using static ngrok URL:")
        app.logger.info(f"🔗 {static_ngrok_url}/whatsapp")
        app.logger.info(f"🛡️ Starting Flask server on port {port}")

        app.run(port=port, debug=True)

