"""
Flask endpoint Twilio will call for every inbound WhatsApp message.
Behaviour mirrors sms_webhook.py but lives on /whatsapp instead of /sms.
"""
import logging, os
from dotenv import load_dotenv
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from integrations.whatsapp.whatsapp_router import handle_whatsapp_command
from app.config import RuntimeFlags
from integrations.sharedutils.twilio_webhook_sync import sync_service_webhook
load_dotenv()
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TO_WHATSAPP_NUMBER = os.getenv('TO_WHATSAPP_NUMBER')
FROM_WHATSAPP_NUMBER = os.getenv('FROM_WHATSAPP_NUMBER')
WHATSAPP_SERVICE_SID = os.getenv('WHATSAPP_MESSAGING_SERVICE_SID')
NGROK_URL = os.getenv('NGROK_URL')
if WHATSAPP_SERVICE_SID and NGROK_URL:
    sync_service_webhook(WHATSAPP_SERVICE_SID, NGROK_URL, '/whatsapp')
app = Flask(__name__)
client = Client(ACCOUNT_SID, AUTH_TOKEN)
logging.basicConfig(level=logging.DEBUG if RuntimeFlags.DEBUG_MODE else
    logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler(
    'whatsapp_debug.log', mode='a')])


@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    try:
        form_data = request.form.to_dict()
        app.logger.debug(f'📨 WhatsApp form data: {form_data}')
        sender = form_data.get('From', '').strip()
        body = form_data.get('Body', '').strip()
        if not sender or not body:
            app.logger.warning('⚠️ Missing sender or body')
            return Response(
                '<Response><Message>Invalid WhatsApp message.</Message></Response>'
                , mimetype='application/xml')
        app.logger.info(f"📩 WA message from {sender}: '{body}'")
        try:
            reply = handle_whatsapp_command(sender=sender, text=body)
        except Exception:
            app.logger.exception('❌ Error in handle_whatsapp_command')
            reply = (
                'Oops! Something went wrong talking to the shopkeeper. Please tell the Game Master.'
                )
        resp = MessagingResponse()
        resp.message(reply)
        app.logger.info(f"📤 Replying to {sender}: '{reply}'")
        return Response(str(resp), mimetype='application/xml')
    except Exception:
        app.logger.exception('❌ Top-level /whatsapp failure')
        return Response(
            '<Response><Message>Major WhatsApp error. Try later.</Message></Response>'
            , mimetype='application/xml')


def send_startup_whatsapp():
    try:
        params = {'body': 'Shopkeeper is online', 'to': TO_WHATSAPP_NUMBER}
        if WHATSAPP_SERVICE_SID:
            params['messaging_service_sid'] = WHATSAPP_SERVICE_SID
        elif FROM_WHATSAPP_NUMBER:
            params['from_'] = FROM_WHATSAPP_NUMBER
        else:
            raise ValueError(
                'FROM_WHATSAPP_NUMBER or WHATSAPP_MESSAGING_SERVICE_SID required'
                )
        msg = client.messages.create(**params)
        app.logger.info(f'✅ Startup WhatsApp sent (SID {msg.sid})')
    except Exception as exc:
        app.logger.warning(f'⚠️ Could not send startup WhatsApp: {exc}')


def start_whatsapp_server():
    port = 5001
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        app.logger.info(
            f'🔗 Ensure Twilio webhook points to: {NGROK_URL}/whatsapp')
        send_startup_whatsapp()
    app.logger.info(f'🚡 WhatsApp Flask server on port {port}')
    app.run(port=port, debug=RuntimeFlags.DEBUG_MODE, host='0.0.0.0')
