from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pyngrok import ngrok
from whatsapp_router import handle_whatsapp_command, sender_to_player_id
import logging
import os

# 🔧 Proper logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    # ✅ Log incoming request
    app.logger.debug(f"RAW incoming: {dict(request.form)}")

    incoming_msg = request.form.get('Body', '').strip()
    sender = request.form.get('From')

    app.logger.info(f"[RECEIVED] From {sender}: {incoming_msg}")

    try:
        response_text = handle_whatsapp_command(sender=sender, text=incoming_msg)

    except Exception as e:
        app.logger.error(f"❌ Failed to handle message: {e}")
        response_text = "Oops! Something went wrong. Please try again."

    resp = MessagingResponse()
    resp.message(response_text)

    return str(resp)

if __name__ == "__main__":
    port = 5000

    # ✅ Only connect ngrok tunnel in the reloader process
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        public_url = ngrok.connect(port)
        app.logger.info(f"🚀 Ngrok tunnel available at: {public_url}")
        app.logger.info(f"🔗 Set your Twilio webhook to: {public_url}/whatsapp")

    # 🛠️ Enable debug mode safely
    app.run(port=port, debug=True)
