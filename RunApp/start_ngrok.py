from pyngrok import conf, ngrok
from integrations.sms.sms_webhook import start_sms_server
import webbrowser
import pyperclip


def main():
    conf.get_default().ngrok_path = 'C:\\ngrok.exe'
    url = ngrok.connect(5000, domain='patient-cheerful-oryx.ngrok-free.app')
    print(f'🔗 Public URL: {url}')
    with open('../ngrok_url.txt', 'w') as f:
        f.write(str(url))
    try:
        pyperclip.copy(str(url))
        print('📋 Public URL copied to clipboard.')
    except Exception as e:
        print('⚠️ Could not copy to clipboard:', e)
    webbrowser.open(str(url))
    start_sms_server()


if __name__ == '__main__':
    main()
