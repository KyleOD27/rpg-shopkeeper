# app/utils/twilio_webhook_sync.py
import os, logging
from urllib.parse import urljoin
from twilio.rest import Client

def sync_service_webhook(service_sid: str, base_url: str, path: str):
    url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))

    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

    # 🔻 USE THE v1 ENDPOINT (recommended by Twilio SDK 9.x)
    svc = client.messaging.v1.services(service_sid).update(
        inbound_request_url=url,
        inbound_method="POST"
    )
    logging.info(f"🔄  Twilio webhook set to {svc.inbound_request_url}")
