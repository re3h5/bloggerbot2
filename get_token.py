import os
import json
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
import socket
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

SCOPES = ['https://www.googleapis.com/auth/blogger']

def get_blogger_token():
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(project_root, 'config', 'credentials.json')
        token_path = os.path.join(project_root, 'config', 'token.json')

        os.makedirs(os.path.dirname(credentials_path), exist_ok=True)

        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"credentials.json not found. Please download it from Google Cloud Console "
                f"and save it as {credentials_path}"
            )

        port = 8080

        # Kill any existing process using port 8080
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'http.server' or proc.info['name'] == 'python.exe':
                for conn in psutil.net_connections(kind='tcp'):
                    if conn.status == 'LISTEN' and conn.laddr.port == port:
                        logging.info(f"Killing process {proc.info['pid']} using port {port}")
                        proc.terminate()

        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', port))
                sock.close()
                break
            except socket.error:
                logging.error(f"Socket error: unable to bind to port {port}")
                return False

        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=port, redirect_uri_trailing_slash=False, host='localhost')

        # Parse the creds into dict to inspect & enrich
        token_data = json.loads(creds.to_json())
        token_data["account"] = creds.id_token.get("email") if creds.id_token else "unknown"

        if "refresh_token" not in token_data or not token_data["refresh_token"]:
            logging.warning("⚠️ No refresh_token found. This may cause future failures on GitHub.")
        else:
            logging.info("🔑 Refresh token included ✔")

        # Save as indented UTF-8 JSON for GitHub copy-pasting
        with open(token_path, 'w', encoding='utf-8') as token_file:
            json.dump(token_data, token_file, indent=2, ensure_ascii=False)

        logging.info(f"✅ Token saved to {token_path}")
        logging.info(f"👤 Authenticated Google Account: {token_data['account']}")
        return True

    except FileNotFoundError as e:
        logging.error(f"❌ {str(e)}")
        return False
    except socket.error as e:
        logging.error(f"❌ Socket error: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"❌ Error during authentication: {str(e)}")
        return False

if __name__ == "__main__":
    get_blogger_token()
