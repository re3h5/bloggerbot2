"""
Email Bot - Sends blog posts via Gmail instead of posting to Blogger
Maintains all human-like behavior and scheduling features
"""

import logging
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import os
import sys

# Add src to path for imports
sys.path.append(os.path.dirname(__file__))

from services.content_generator import ContentGeneratorService
from services.posting_scheduler import PostingScheduler
from services.content_diversity import ContentDiversityService
from services.gmail_service import GmailService

class EmailBot:
    """
    Email Bot that generates content and sends it via Gmail
    Maintains human-like behavior and posting patterns
    """
    
    def __init__(self, config_dir: str = "config", use_gmail_api: bool = False):
        self.config_dir = config_dir
        self.use_gmail_api = use_gmail_api
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.content_generator = ContentGeneratorService()
        self.posting_scheduler = PostingScheduler(config_dir)
        self.content_diversity = ContentDiversityService(config_dir)
        self.gmail_service = GmailService(use_api=use_gmail_api)
        
        # Load email configuration
        self.email_config = self._load_email_config()
        
        self.logger.info("Email Bot initialized successfully")
        
    def _load_email_config(self) -> Dict[str, Any]:
        """Load email-specific configuration"""
        config_path = os.path.join(self.config_dir, "email_config.json")
        
        default_config = {
            "default_recipients": [],
            "email_types": {
                "newsletter": {"weight": 40, "subject_prefix": "📧"},
                "blog_post": {"weight": 35, "subject_prefix": "📝"},
                "digest": {"weight": 15, "subject_prefix": "📰"},
                "announcement": {"weight": 10, "subject_prefix": "📢"}
            },
            "sending_preferences": {
                "preferred_hours": [9, 10, 11, 14, 15, 16, 17, 18],
                "avoid_weekends": False,
                "max_daily_emails": 4,
                "min_delay_between_emails": 3600  # 1 hour in seconds
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                # Create default config
                os.makedirs(self.config_dir, exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
                
        except Exception as e:
            self.logger.error(f"Error loading email config: {str(e)}")
            return default_config
    
    def _save_email_config(self):
        """Save email configuration"""
        try:
            config_path = os.path.join(self.config_dir, "email_config.json")
            with open(config_path, 'w') as f:
                json.dump(self.email_config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving email config: {str(e)}")
    
    def _select_email_type(self) -> str:
        """Select email type based on weights"""
        email_types = self.email_config["email_types"]
        
        # Create weighted list
        weighted_types = []
        for email_type, config in email_types.items():
            weight = config.get("weight", 25)
            weighted_types.extend([email_type] * weight)
        
        return random.choice(weighted_types)
    
    def _human_like_delay(self, min_seconds: int = 30, max_seconds: int = 300):
        """Add human-like delay between operations"""
        delay = random.randint(min_seconds, max_seconds)
        self.logger.info(f"Taking a {delay}s break (human-like behavior)...")
        time.sleep(delay)
    
    def _should_send_email_now(self) -> tuple[bool, str]:
        """Check if we should send an email now based on schedule and limits"""
        
        # Check posting schedule
        should_post, reason = self.posting_scheduler.should_post_now()
        if not should_post:
            return False, f"Posting scheduler says no: {reason}"
        
        # Check email-specific preferences
        current_hour = datetime.now().hour
        preferred_hours = self.email_config["sending_preferences"]["preferred_hours"]
        
        if preferred_hours and current_hour not in preferred_hours:
            return False, f"Current hour ({current_hour}) not in preferred sending hours {preferred_hours}"
        
        # Check if it's weekend and we avoid weekends
        if self.email_config["sending_preferences"]["avoid_weekends"]:
            if datetime.now().weekday() >= 5:  # Saturday = 5, Sunday = 6
                return False, "Avoiding weekend sending"
        
        return True, "All checks passed"
    
    def generate_and_send_email(self, force_send: bool = False, 
                               recipients: Optional[List[str]] = None,
                               email_type: Optional[str] = None) -> bool:
        """Generate content and send it via email"""
        
        try:
            # Check if we should send now (unless forced)
            if not force_send:
                should_send, reason = self._should_send_email_now()
                if not should_send:
                    self.logger.info(f"Not sending email now: {reason}")
                    return False
            
            self.logger.info("Starting email generation and sending process...")
            
            # Human-like delay before starting
            self._human_like_delay(30, 120)
            
            # Select email type
            if not email_type:
                email_type = self._select_email_type()
            
            self.logger.info(f"Selected email type: {email_type}")
            
            # Generate content based on diversity recommendations
            diversity_report = self.content_diversity.get_diversity_report()
            
            # Generate headline
            self.logger.info("Generating email subject/headline...")
            self._human_like_delay(15, 60)
            
            headline = self.content_generator.generate_headline(
                style=email_type,
                avoid_topics=diversity_report.get('overused_topics', [])
            )
            
            if not headline:
                self.logger.error("Failed to generate headline")
                return False
            
            self.logger.info(f"Generated headline: {headline}")
            
            # Human-like delay between headline and content
            self._human_like_delay(30, 90)
            
            # Generate content
            self.logger.info("Generating email content...")
            content = self.content_generator.generate_blog_post(
                headline=headline,
                style=email_type,
                avoid_keywords=diversity_report.get('overused_keywords', [])
            )
            
            if not content:
                self.logger.error("Failed to generate content")
                return False
            
            self.logger.info(f"Generated content ({len(content)} characters)")
            
            # Human-like delay before sending
            self._human_like_delay(20, 80)
            
            # Send email
            self.logger.info("Sending email...")
            success = self.gmail_service.send_blog_post_email(
                title=headline,
                content=content,
                recipients=recipients,
                email_type=email_type
            )
            
            if success:
                self.logger.info(f"Email sent successfully! Subject: {headline}")
                
                # Record the posting
                self.posting_scheduler.record_post()
                
                # Update content diversity
                self.content_diversity.add_content(headline, content, email_type)
                
                # Human-like delay after successful send
                self._human_like_delay(60, 180)
                
                return True
            else:
                self.logger.error("Failed to send email")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in generate_and_send_email: {str(e)}")
            return False
    
    def run_email_campaign(self, max_emails: int = 1, force_send: bool = False) -> Dict[str, Any]:
        """Run an email campaign with multiple emails"""
        
        results = {
            'emails_sent': 0,
            'emails_failed': 0,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'details': []
        }
        
        self.logger.info(f"Starting email campaign (max {max_emails} emails)")
        
        for i in range(max_emails):
            self.logger.info(f"Email {i+1}/{max_emails}")
            
            try:
                success = self.generate_and_send_email(force_send=force_send)
                
                if success:
                    results['emails_sent'] += 1
                    results['details'].append({
                        'email_number': i+1,
                        'status': 'success',
                        'timestamp': datetime.now().isoformat()
                    })
                    self.logger.info(f"Email {i+1} sent successfully")
                else:
                    results['emails_failed'] += 1
                    results['details'].append({
                        'email_number': i+1,
                        'status': 'failed',
                        'timestamp': datetime.now().isoformat()
                    })
                    self.logger.warning(f"Email {i+1} failed to send")
                
                # Delay between emails (except for the last one)
                if i < max_emails - 1:
                    delay = random.randint(1800, 7200)  # 30 minutes to 2 hours
                    self.logger.info(f"Waiting {delay//60} minutes before next email...")
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"Error sending email {i+1}: {str(e)}")
                results['emails_failed'] += 1
                results['details'].append({
                    'email_number': i+1,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        results['end_time'] = datetime.now().isoformat()
        
        self.logger.info(f"Email campaign completed: {results['emails_sent']} sent, {results['emails_failed']} failed")
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        
        # Test Gmail connection
        gmail_connected = self.gmail_service.test_connection()
        
        # Get posting schedule status
        schedule_status = self.posting_scheduler.get_status()
        
        # Get diversity report
        diversity_report = self.content_diversity.get_diversity_report()
        
        return {
            'bot_type': 'EmailBot',
            'gmail_connected': gmail_connected,
            'gmail_method': 'API' if self.use_gmail_api else 'SMTP',
            'schedule_status': schedule_status,
            'diversity_report': diversity_report,
            'email_config': self.email_config,
            'last_check': datetime.now().isoformat()
        }
    
    def test_email_sending(self, test_recipients: Optional[List[str]] = None) -> bool:
        """Send a test email"""
        
        test_subject = f"Test Email from EmailBot - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        test_content = """
        This is a test email from your EmailBot!
        
        If you're receiving this, your email configuration is working correctly.
        
        Key features:
        - Gmail integration (SMTP or API)
        - Human-like sending patterns
        - Content diversity tracking
        - Multiple email templates
        - Automated scheduling
        
        Your EmailBot is ready to send automated emails!
        """
        
        return self.gmail_service.send_blog_post_email(
            title=test_subject,
            content=test_content,
            recipients=test_recipients,
            email_type="announcement"
        )
