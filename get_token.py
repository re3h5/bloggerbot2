import os
import json
import logging
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import socket
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Use only the necessary scope for Blogger API
# This is the most permissive scope that allows all Blogger operations
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

        creds = None
        # Check if token file exists and try to load credentials
        if os.path.exists(token_path):
            try:
                with open(token_path, 'r') as token_file:
                    token_data = json.load(token_file)
                    creds = Credentials.from_authorized_user_info(token_data, SCOPES)
                    
                # If credentials exist but are expired, try to refresh them
                if creds and creds.expired and creds.refresh_token:
                    logging.info("Token expired. Attempting to refresh...")
                    try:
                        creds.refresh(Request())
                        logging.info("✅ Token refreshed successfully")
                        
                        # Save the refreshed token
                        token_data = json.loads(creds.to_json())
                        token_data["account"] = token_data.get("id_token", {}).get("email", "unknown")
                        
                        with open(token_path, 'w', encoding='utf-8') as token_file:
                            json.dump(token_data, token_file, indent=2, ensure_ascii=False)
                            
                        logging.info(f"✅ Refreshed token saved to {token_path}")
                        return True
                    except Exception as refresh_error:
                        logging.warning(f"Failed to refresh token: {str(refresh_error)}")
                        logging.info("Will proceed with new authentication flow")
                        creds = None
            except (json.JSONDecodeError, ValueError) as e:
                logging.warning(f"Invalid token file: {str(e)}. Will create a new one.")
                creds = None

        # If no valid credentials, start new OAuth flow
        if not creds:
            port = 8080

            # Kill any existing process using port 8080
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] in ['http.server', 'python.exe', 'python']:
                        for conn in psutil.net_connections(kind='tcp'):
                            if conn.status == 'LISTEN' and conn.laddr.port == port:
                                logging.info(f"Killing process {proc.info['pid']} using port {port}")
                                proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Try to find an available port
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.bind(('localhost', port))
                    sock.close()
                    break
                except socket.error:
                    logging.warning(f"Port {port} is in use. Trying port {port + 1}")
                    port += 1
                    if attempt == max_attempts - 1:
                        logging.error(f"Could not find an available port after {max_attempts} attempts")
                        return False

            try:
                # Start the OAuth flow with the available port
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(
                    port=port, 
                    redirect_uri_trailing_slash=False, 
                    host='localhost',
                    authorization_prompt_message="Please authorize the Blogger Bot to access your Blogger account"
                )

                # Parse the creds into dict to inspect & enrich
                token_data = json.loads(creds.to_json())
                token_data["account"] = creds.id_token.get("email") if creds.id_token else "unknown"

                if "refresh_token" not in token_data or not token_data["refresh_token"]:
                    logging.warning("⚠️ No refresh_token found. This may cause future failures.")
                    logging.warning("⚠️ Try revoking access at https://myaccount.google.com/permissions and run this script again.")
                else:
                    logging.info("🔑 Refresh token included ✔")

                # Save as indented UTF-8 JSON for GitHub copy-pasting
                with open(token_path, 'w', encoding='utf-8') as token_file:
                    json.dump(token_data, token_file, indent=2, ensure_ascii=False)

                logging.info(f"✅ Token saved to {token_path}")
                logging.info(f"👤 Authenticated Google Account: {token_data['account']}")
                
                # Verify token works by testing a simple API call
                try:
                    from googleapiclient.discovery import build
                    service = build('blogger', 'v3', credentials=creds)
                    user = service.users().get(userId='self').execute()
                    logging.info(f"✅ API connection verified. User ID: {user.get('id')}")
                except Exception as api_error:
                    logging.warning(f"⚠️ Token generated but API test failed: {str(api_error)}")
                    logging.warning("The token may still work for posting. Check your API quotas and permissions.")
                
                return True
                
            except Exception as auth_error:
                logging.error(f"❌ Authentication flow error: {str(auth_error)}")
                return False

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
