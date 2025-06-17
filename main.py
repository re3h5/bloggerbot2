#!/usr/bin/env python3
"""
BloggerBot - AI-powered blog post generator and publisher.
This script runs the BloggerBot to generate and publish a blog post based on trending topics.
"""
import os
import sys
import logging
from src.blogger_bot import BloggerBot
from src.utils.logger import setup_logger
from src.utils.config import OPENROUTER_API_KEY, BLOGGER_ID

def main():
    """Main function to run the BloggerBot."""
    # Setup logger
    setup_logger()
    
    # Check for required environment variables
    if not OPENROUTER_API_KEY or not BLOGGER_ID:
        missing_vars = []
        if not OPENROUTER_API_KEY:
            missing_vars.append('OPENROUTER_API_KEY')
        if not BLOGGER_ID:
            missing_vars.append('BLOGGER_ID')
        
        logging.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file or environment.")
        sys.exit(1)
    
    # Run the BloggerBot
    logging.info("🤖 Starting Blogger Bot")
    bot = BloggerBot()
    success = bot.run()
    
    if success:
        print(f"✅ Blog post successfully published: {success}")
        sys.exit(0)
    else:
        print("❌ Failed to publish blog post. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
