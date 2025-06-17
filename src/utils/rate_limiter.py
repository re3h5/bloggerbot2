"""
Rate limiter utility to prevent hitting API rate limits.
"""
import time
import logging
import os
import json
from datetime import datetime, timedelta

class RateLimiter:
    """
    Simple rate limiter to prevent hitting API rate limits.
    Tracks API calls in a local file and enforces limits.
    """
    
    def __init__(self, name, max_calls_per_day=9000, max_calls_per_minute=50):
        """
        Initialize the rate limiter.
        
        Args:
            name: Name of the API (used for the tracking file)
            max_calls_per_day: Maximum calls allowed per day
            max_calls_per_minute: Maximum calls allowed per minute
        """
        self.name = name
        self.max_calls_per_day = max_calls_per_day
        self.max_calls_per_minute = max_calls_per_minute
        
        # Create rate limiting directory if it doesn't exist
        self.rate_limit_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'rate_limits')
        os.makedirs(self.rate_limit_dir, exist_ok=True)
        
        # File to track API calls
        self.tracking_file = os.path.join(self.rate_limit_dir, f"{name}_api_calls.json")
        
        # Initialize tracking data
        self.tracking_data = self._load_tracking_data()
    
    def _load_tracking_data(self):
        """Load tracking data from file or create default structure."""
        try:
            if os.path.exists(self.tracking_file):
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    "daily": {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "count": 0
                    },
                    "minute": {
                        "timestamp": int(time.time()),
                        "count": 0
                    }
                }
        except Exception as e:
            logging.warning(f"Error loading rate limit data: {str(e)}. Creating new tracking data.")
            return {
                "daily": {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "count": 0
                },
                "minute": {
                    "timestamp": int(time.time()),
                    "count": 0
                }
            }
    
    def _save_tracking_data(self):
        """Save tracking data to file."""
        try:
            with open(self.tracking_file, 'w') as f:
                json.dump(self.tracking_data, f)
        except Exception as e:
            logging.error(f"Error saving rate limit data: {str(e)}")
    
    def check_rate_limit(self):
        """
        Check if we're within rate limits.
        
        Returns:
            tuple: (can_proceed, wait_time_seconds)
                - can_proceed: True if within limits, False otherwise
                - wait_time_seconds: How long to wait before trying again (0 if can proceed)
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = int(time.time())
        
        # Reset daily counter if date changed
        if self.tracking_data["daily"]["date"] != current_date:
            self.tracking_data["daily"] = {
                "date": current_date,
                "count": 0
            }
        
        # Reset minute counter if more than a minute has passed
        if current_time - self.tracking_data["minute"]["timestamp"] >= 60:
            self.tracking_data["minute"] = {
                "timestamp": current_time,
                "count": 0
            }
        
        # Check daily limit
        if self.tracking_data["daily"]["count"] >= self.max_calls_per_day:
            # Calculate time until next day
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
            wait_seconds = (tomorrow - datetime.now()).total_seconds()
            return False, int(wait_seconds)
        
        # Check minute limit
        if self.tracking_data["minute"]["count"] >= self.max_calls_per_minute:
            # Calculate time until next minute
            wait_seconds = 60 - (current_time - self.tracking_data["minute"]["timestamp"])
            return False, max(1, wait_seconds)
        
        return True, 0
    
    def increment(self):
        """
        Increment the API call counters.
        Should be called after a successful API call.
        """
        self.tracking_data["daily"]["count"] += 1
        self.tracking_data["minute"]["count"] += 1
        self._save_tracking_data()
    
    def wait_if_needed(self):
        """
        Check rate limits and wait if necessary.
        
        Returns:
            bool: True if we can proceed, False if we've hit a daily limit
        """
        can_proceed, wait_seconds = self.check_rate_limit()
        
        if not can_proceed:
            if wait_seconds > 3600:  # More than an hour wait
                logging.warning(f"{self.name} API daily rate limit reached. Try again tomorrow.")
                return False
            
            logging.info(f"{self.name} API rate limit reached. Waiting {wait_seconds} seconds...")
            time.sleep(wait_seconds)
            # Check again after waiting
            return self.wait_if_needed()
        
        # We can proceed, increment counters
        self.increment()
        return True
