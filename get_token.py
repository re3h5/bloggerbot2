import os
import logging
from google_auth_oauthlib.flow import InstalledAppFlow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Only request the scopes we need for reading and writing blog posts
SCOPES = ['https://www.googleapis.com/auth/blogger']  # This is the correct scope for full access

def get_blogger_token():
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.abspath(__file__))
        
        # Define paths for credentials and token
        credentials_path = os.path.join(project_root, 'config', 'credentials.json')
        token_path = os.path.join(project_root, 'config', 'token.json')
        
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(credentials_path), exist_ok=True)

        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"credentials.json not found. Please download it from Google Cloud Console "
                f"and save it as {credentials_path}"
            )

        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        # Use a specific port and redirect URI that matches Google Cloud Console
        creds = flow.run_local_server(
            port=8080,
            redirect_uri_trailing_slash=False,
            host='localhost'
        )

        # Save token as JSON
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

        logging.info(f"✅ Token saved to {token_path}")
        return True

    except Exception as e:
        logging.error(f"❌ Error during authentication: {str(e)}")
        return False

if __name__ == "__main__":
    get_blogger_token()
