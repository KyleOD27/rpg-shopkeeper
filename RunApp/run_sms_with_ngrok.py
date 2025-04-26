# run_sms_with_ngrok.py

from pyngrok import conf, ngrok
from integrations.sms.sms_webhook import start_sms_server
import webbrowser
import pyperclip

def main():
    # Optional if ngrok.exe is not in system PATH
    conf.get_default().ngrok_path = r"C:\ngrok.exe"

    # Start tunnel with fixed domain
    url = ngrok.connect(5000, domain="patient-cheerful-oryx.ngrok-free.app")
    print(f"🔗 Public URL: {url}")

    # Start the Flask SMS server
    start_sms_server()

if __name__ == "__main__":
    main()
