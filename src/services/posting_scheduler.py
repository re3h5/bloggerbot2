"""
Service for managing human-like posting patterns and scheduling.
"""
import logging
import time
import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class PostingScheduler:
    """Service to manage human-like posting patterns and prevent spam detection."""
    
    def __init__(self, config_file: str = "config/posting_schedule.json"):
        self.config_file = config_file
        self.posting_history = self._load_posting_history()
        self.force_post = False  # Add force_post flag
        
        # Human-like posting patterns
        self.min_delay_between_posts = 3600  # 1 hour minimum
        self.max_delay_between_posts = 86400  # 1 day maximum
        self.preferred_posting_hours = list(range(9, 18))  # 9 AM to 6 PM
        self.max_posts_per_day = 4
        self.max_posts_per_week = 27
        
        # Natural posting frequency patterns
        self.posting_patterns = {
            'conservative': {'min_hours': 6, 'max_hours': 12, 'daily_limit': 3},
            'moderate': {'min_hours': 4, 'max_hours': 8, 'daily_limit': 4},
            'active': {'min_hours': 2, 'max_hours': 6, 'daily_limit': 4}
        }
        
        self.current_pattern = 'moderate'  # Default to moderate posting
    
    def _load_posting_history(self) -> List[Dict]:
        """Load posting history from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logging.warning("Could not load posting history, starting fresh")
        return []
    
    def _save_posting_history(self):
        """Save posting history to file."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.posting_history, f, indent=2)
    
    def can_post_now(self) -> tuple[bool, str]:
        """
        Check if it's appropriate to post now based on human-like patterns.
        Returns (can_post, reason)
        """
        # If force_post is True, always allow posting
        if self.force_post:
            return True, "Force posting enabled"
            
        now = datetime.now()
        
        # Check if we've posted too recently
        if self.posting_history:
            last_post = datetime.fromisoformat(self.posting_history[-1]['timestamp'])
            time_since_last = (now - last_post).total_seconds()
            
            pattern = self.posting_patterns[self.current_pattern]
            min_wait = pattern['min_hours'] * 3600
            
            if time_since_last < min_wait:
                wait_time = min_wait - time_since_last
                return False, f"Too soon since last post. Wait {wait_time/3600:.1f} more hours"
        
        # Check daily posting limits
        today_posts = [
            post for post in self.posting_history
            if datetime.fromisoformat(post['timestamp']).date() == now.date()
        ]
        
        pattern = self.posting_patterns[self.current_pattern]
        if len(today_posts) >= pattern['daily_limit']:
            return False, f"Daily posting limit reached ({pattern['daily_limit']} posts)"
        
        # Check weekly posting limits
        week_ago = now - timedelta(days=7)
        week_posts = [
            post for post in self.posting_history
            if datetime.fromisoformat(post['timestamp']) > week_ago
        ]
        
        if len(week_posts) >= self.max_posts_per_week:
            return False, f"Weekly posting limit reached ({self.max_posts_per_week} posts)"
        
        # Check if current time is within preferred hours
        if now.hour not in self.preferred_posting_hours:
            return False, f"Outside preferred posting hours (9 AM - 6 PM)"
        
        return True, "Ready to post"
    
    def get_next_posting_time(self) -> datetime:
        """Calculate the next appropriate time to post."""
        now = datetime.now()
        
        if self.posting_history:
            last_post = datetime.fromisoformat(self.posting_history[-1]['timestamp'])
            pattern = self.posting_patterns[self.current_pattern]
            
            # Add random delay within pattern constraints
            min_hours = pattern['min_hours']
            max_hours = pattern['max_hours']
            
            # Add some randomness to make it more human-like
            random_hours = random.uniform(min_hours, max_hours)
            next_time = last_post + timedelta(hours=random_hours)
        else:
            # First post - schedule for next preferred hour
            next_time = now + timedelta(hours=1)
        
        # Ensure it's within preferred posting hours
        while next_time.hour not in self.preferred_posting_hours:
            next_time += timedelta(hours=1)
        
        return next_time
    
    def add_human_like_delay(self):
        """Add a random delay to simulate human behavior."""
        if not self.force_post:  # Skip delay if force_post is True
            # Random delay between 30 seconds to 5 minutes
            delay = random.uniform(30, 300)
            logging.info(f"[DELAY] Adding human-like delay: {delay:.1f} seconds")
            time.sleep(delay)
    
    def record_post(self, topic: str, success: bool, post_url: Optional[str] = None):
        """Record a posting attempt in the history."""
        post_record = {
            'timestamp': datetime.now().isoformat(),
            'topic': topic,
            'success': success,
            'post_url': post_url,
            'pattern': self.current_pattern
        }
        
        self.posting_history.append(post_record)
        
        # Keep only last 100 posts to prevent file from growing too large
        if len(self.posting_history) > 100:
            self.posting_history = self.posting_history[-100:]
        
        self._save_posting_history()
        logging.info(f"[POST] Recorded post: {topic} - Success: {success}")
    
    def get_posting_stats(self) -> Dict:
        """Get statistics about posting patterns."""
        now = datetime.now()
        
        # Posts in last 24 hours
        day_ago = now - timedelta(days=1)
        daily_posts = [
            post for post in self.posting_history
            if datetime.fromisoformat(post['timestamp']) > day_ago
        ]
        
        # Posts in last 7 days
        week_ago = now - timedelta(days=7)
        weekly_posts = [
            post for post in self.posting_history
            if datetime.fromisoformat(post['timestamp']) > week_ago
        ]
        
        # Success rate
        successful_posts = [post for post in self.posting_history if post['success']]
        success_rate = len(successful_posts) / len(self.posting_history) if self.posting_history else 0
        
        return {
            'total_posts': len(self.posting_history),
            'daily_posts': len(daily_posts),
            'weekly_posts': len(weekly_posts),
            'success_rate': success_rate,
            'current_pattern': self.current_pattern,
            'next_posting_time': self.get_next_posting_time().isoformat()
        }
    
    def adjust_posting_pattern(self, pattern: str):
        """Adjust posting pattern based on success rate or user preference."""
        if pattern in self.posting_patterns:
            self.current_pattern = pattern
            logging.info(f"[PATTERN] Adjusted posting pattern to: {pattern}")
        else:
            logging.warning(f"Unknown posting pattern: {pattern}")
    
    def should_skip_posting_today(self) -> bool:
        """Randomly decide to skip posting to simulate human inconsistency."""
        # 10% chance to skip posting on any given opportunity
        return random.random() < 0.1
