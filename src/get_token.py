"""
Script to obtain or refresh OAuth token for Blogger API.
Run this script to authenticate with Google and get a new token.
"""
import logging
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import our modules
from utils.logger import setup_logger
from utils.token_manager import get_blogger_token

def main():
    # Setup logger
    setup_logger()
    
    # Get token
    logging.info("🔑 Starting token generation process...")
    creds = get_blogger_token()
    
    if creds:
        logging.info("✅ Token generation successful! You can now run the bot.")
        print("✅ Authentication successful! Token saved to config/token.json")
    else:
        logging.error("❌ Token generation failed.")
        print("❌ Authentication failed. Check logs for details.")

if __name__ == "__main__":
    main()
