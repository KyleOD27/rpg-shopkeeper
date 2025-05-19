# RunApp/run_whatsapp_safe.py
import datetime, csv, traceback, sys, os, subprocess
from pathlib import Path

from pyngrok import ngrok           # pip install pyngrok
from integrations.whatsapp.whatsapp_webhook import start_whatsapp_server

LOG_PATH = Path(__file__).with_name("error_log.csv")
PORT     = int(os.getenv("WHATSAPP_PORT", 5000))   # Flask default
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")

def _log_crash(exc: Exception, tb: str) -> None:
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    new_file = not LOG_PATH.exists()
    with LOG_PATH.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["timestamp", "exc_type", "message", "traceback"])
        w.writerow([ts, type(exc).__name__, str(exc), tb])

def _start_tunnel() -> str:
    auth_token = os.getenv("NGROK_AUTHTOKEN")
    if auth_token:
        ngrok.set_auth_token(auth_token)

    domain = "patient-cheerful-oryx.ngrok-free.app"
    tunnel  = ngrok.connect(PORT, "http", domain=domain)  # <-- new arg
    public_url = f"https://{domain}"
    return public_url

def _update_twilio_webhook(url: str) -> None:
    """Point Twilio’s WhatsApp sandbox (or your prod number) at our new URL."""
    if not (TWILIO_SID and TWILIO_AUTH):
        print("[WARN] Twilio credentials not set; skipping automatic webhook update.")
        return
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_AUTH)
        sandbox = client.messages \
            .services("MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")  # or your MessagingService SID
        sandbox.update(inbound_request_url=f"{url}/whatsapp/webhook")
        print("[INFO] Twilio webhook updated.")
    except Exception as exc:
        print(f"[WARN] Twilio update failed: {exc}")

def run():
    try:
        public_url = _start_tunnel()
        _update_twilio_webhook(public_url)
        start_whatsapp_server()          # your real entry point
    except Exception as exc:
        tb = traceback.format_exc()
        print("\n=========== CRASH ===========")
        print(tb)
        _log_crash(exc, tb)
        input("\nPress <Enter> to close…")
        sys.exit(1)

if __name__ == "__main__":
    run()
