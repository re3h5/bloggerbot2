import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set")

# Blogger Configuration
BLOGGER_TOKEN_PATH = 'token.json'
BLOGGER_CREDENTIALS_PATH = 'credentials.json'
BLOGGER_ID = os.getenv('BLOGGER_ID')
if not BLOGGER_ID:
    raise ValueError("BLOGGER_ID environment variable is not set")

# Load Blogger token if exists
def load_blogger_token():
    try:
        if os.path.exists(BLOGGER_TOKEN_PATH):
            with open(BLOGGER_TOKEN_PATH, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        raise ValueError(f"Error loading Blogger token: {str(e)}")
