#!/usr/bin/env python3
"""
BloggerBot - AI-powered blog post generator and publisher.
This script runs the BloggerBot to generate and publish a blog post based on trending topics.
"""
import os
import sys
import logging
from dotenv import load_dotenv
from src.blogger_bot import BloggerBot

def main():
    """Main function to run the BloggerBot."""
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ['OPENROUTER_API_KEY', 'BLOGGER_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file or environment.")
        sys.exit(1)
    
    # Run the BloggerBot
    bot = BloggerBot()
    success = bot.run()
    
    if success:
        print("✅ Blog post successfully published")
        sys.exit(0)
    else:
        # The error message is already printed by the BloggerBot class
        sys.exit(1)

if __name__ == "__main__":
    main()
