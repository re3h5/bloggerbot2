"""Configuration utilities for the Blogger Bot."""
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# API Keys and IDs
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
BLOGGER_ID = os.getenv('BLOGGER_ID')

def load_blogger_token(token_file='config/token.json'):
    """Load the Blogger OAuth token from the token file."""
    try:
        # Get the project root directory (where src folder is located)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        token_path = os.path.join(project_root, token_file)
        
        if os.path.exists(token_path):
            with open(token_path, 'r') as f:
                return json.load(f)
        else:
            print(f"Token file not found at: {token_path}")
    except Exception as e:
        print(f"Error loading token: {str(e)}")
    return None
