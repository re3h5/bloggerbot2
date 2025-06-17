"""
Configuration module for the Blogger Bot.
Handles environment variables and credentials.
"""
import os
import json
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# API Keys and IDs
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
BLOGGER_ID = os.getenv('BLOGGER_ID')
PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY')  # Optional for image generation

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
CREDENTIALS_PATH = os.path.join(CONFIG_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(CONFIG_DIR, 'token.json')

def load_token():
    """Load OAuth token from file."""
    try:
        with open(TOKEN_PATH, 'r') as token_file:
            return json.load(token_file)
    except FileNotFoundError:
        logging.error(f"Token file not found at {TOKEN_PATH}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in token file at {TOKEN_PATH}")
        return None
