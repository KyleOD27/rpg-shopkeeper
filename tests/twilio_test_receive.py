from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import sys
app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return '✅ Flask app is running!'


@app.route('/sms', methods=['POST'])
def sms_reply():
    print('📡 Incoming sms webhook hit!', file=sys.stderr)
    print(f'Form data: {request.form}', file=sys.stderr)
    incoming_msg = request.form.get('Body')
    from_number = request.form.get('From')
    print(f'📩 Received sms from {from_number}: {incoming_msg}', file=sys.stderr
        )
    resp = MessagingResponse()
    resp.message('🛒 Thanks for messaging the RPG Shopkeeper!')
    return Response(str(resp), mimetype='application/xml')


if __name__ == '__main__':
    app.run(debug=True)
