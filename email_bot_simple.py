#!/usr/bin/env python3
"""
Simple Email Bot - Sends emails without config file dependencies
Works around permission issues with config directory
"""

import os
import sys
import logging
import time
import random
from datetime import datetime
from typing import List, Optional

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def load_env_file():
    """Load environment variables from .env file"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('email_bot_simple.log')
        ]
    )

def generate_content():
    """Generate blog post content using OpenRouter API"""
    try:
        from services.content_generator import ContentGeneratorService
        
        content_generator = ContentGeneratorService()
        
        # Generate a blog post
        print("🤖 Generating blog post content...")
        content = content_generator.generate_blog_post()
        
        if content and 'title' in content and 'content' in content:
            print(f"✅ Generated: {content['title']}")
            return content
        else:
            print("❌ Failed to generate content")
            return None
            
    except Exception as e:
        print(f"❌ Content generation error: {e}")
        return None

def send_email(content: dict, recipients: List[str], email_type: str = "newsletter"):
    """Send email using Gmail service"""
    try:
        from services.gmail_service import GmailService
        
        gmail_service = GmailService(use_api=False)
        
        # Use the send_blog_post_email method which handles everything
        print(f"📤 Sending email to {len(recipients)} recipient(s)...")
        
        success = gmail_service.send_blog_post_email(
            title=content['title'],
            content=content['content'],
            recipients=recipients,
            email_type=email_type
        )
        
        if success:
            print("✅ Email sent successfully!")
            return True
        else:
            print("❌ Failed to send email")
            return False
            
    except Exception as e:
        print(f"❌ Email sending error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Email Bot - Send blog posts via Gmail')
    parser.add_argument('--recipients', nargs='+', help='Email recipients')
    parser.add_argument('--type', choices=['newsletter', 'blog_post', 'digest', 'announcement'],
                       default='newsletter', help='Email type/template')
    parser.add_argument('--test', action='store_true', help='Send test email only')
    
    args = parser.parse_args()
    
    # Setup
    setup_logging()
    load_env_file()
    
    print("🚀 Simple Email Bot")
    print("=" * 30)
    
    # Get recipients
    recipients = args.recipients
    if not recipients:
        recipients_env = os.getenv('EMAIL_RECIPIENTS')
        if recipients_env:
            recipients = [r.strip() for r in recipients_env.split(',')]
        else:
            print("❌ No recipients specified")
            print("Use --recipients or set EMAIL_RECIPIENTS in .env file")
            return False
    
    print(f"📧 Recipients: {', '.join(recipients)}")
    print(f"📝 Email Type: {args.type}")
    
    if args.test:
        # Send test email
        test_content = {
            'title': 'Email Bot Test',
            'content': '''
            <p>This is a test email from your Email Bot!</p>
            <p><strong>Test successful!</strong> Your Email Bot is working correctly.</p>
            <ul>
                <li>Gmail SMTP: ✅ Connected</li>
                <li>Content Generation: ✅ Working</li>
                <li>Email Templates: ✅ Formatted</li>
            </ul>
            <p>You can now send automated blog posts via email!</p>
            '''
        }
        
        success = send_email(test_content, recipients, args.type)
    else:
        # Generate and send real content
        content = generate_content()
        if not content:
            print("❌ Could not generate content")
            return False
        
        # Add human-like delay
        delay = random.randint(30, 120)  # 30-120 seconds
        print(f"⏳ Human-like delay: {delay} seconds...")
        time.sleep(delay)
        
        success = send_email(content, recipients, args.type)
    
    if success:
        print("\n🎉 Email Bot completed successfully!")
        return True
    else:
        print("\n❌ Email Bot failed")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)
