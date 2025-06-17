"""
Logging configuration for the Blogger Bot.
"""
import logging
import os
import sys
from datetime import datetime

def setup_logger():
    """Configure the logger for the application."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a custom formatter that handles emoji encoding issues
    class WindowsSafeFormatter(logging.Formatter):
        def __init__(self, fmt=None, datefmt=None):
            super().__init__(fmt, datefmt)
        
        def format(self, record):
            # Format the message
            result = super().format(record)
            # Replace emojis with text equivalents for Windows console
            if sys.platform == 'win32':
                # Replace common emojis with text versions
                emoji_replacements = {
                    '🤖': '[BOT]',
                    '🧠': '[BRAIN]',
                    '📊': '[STATS]',
                    '✏️': '[WRITING]',
                    '✍️': '[WRITING]',
                    '✨': '[SPARKLES]',
                    '📝': '[CONTENT]',
                    '✅': '[SUCCESS]',
                    '🖼️': '[IMAGE]',
                    '🌄': '[PICTURE]',
                    '📤': '[POSTING]',
                    '🎉': '[CELEBRATION]',
                    '❌': '[ERROR]',
                    '⚠️': '[WARNING]',
                    '🔑': '[KEY]',
                    '👤': '[USER]',
                    '✔': '[CHECK]'
                }
                for emoji, replacement in emoji_replacements.items():
                    result = result.replace(emoji, replacement)
            return result
    
    # Create formatter
    formatter = WindowsSafeFormatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler
    file_handler = logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'blogger_bot.log'))
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add our handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger
