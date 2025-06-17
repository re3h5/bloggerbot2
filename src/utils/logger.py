"""Logging configuration for the Blogger Bot."""
import logging
import sys

def setup_logging():
    """Configure logging with UTF-8 encoding for both file and console output."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('blogger_bot.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)
