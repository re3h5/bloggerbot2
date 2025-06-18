#!/usr/bin/env python3
"""
Email Poster - Uses BloggerBot's complete posting flow and sends the final content via email
"""

import os
import sys
import logging
import random
from datetime import datetime

# Set console output encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.gmail_service import GmailService
from blogger_bot import BloggerBot

def setup_logging():
    """Setup logging configuration"""
    logger = logging.getLogger('email_poster')
    logger.setLevel(logging.INFO)
    
    # Create console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    
    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(console)
    
    # File handler
    file_handler = logging.FileHandler('email_poster.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def load_env_file():
    """Load environment variables from .env file"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def get_recipients():
    """Get email recipients from environment or use default"""
    recipients_env = os.getenv('EMAIL_RECIPIENTS', '')
    if recipients_env:
        return [r.strip() for r in recipients_env.split(',') if r.strip()]
    return ['bsty202502.terabhai99@blogger.com']  # Default recipient

def generate_and_format_blog_post(force_post=False):
    """Generate a blog post using BloggerBot's complete flow and format it for email"""
    logger = logging.getLogger('email_poster')
    try:
        logger.info("Initializing BloggerBot...")
        bot = BloggerBot()
        
        # Run the complete blogging flow but intercept the final post
        logger.info("Running BloggerBot's complete posting flow...")
        
        # Skip the posting schedule check if force_post is True
        if not force_post:
            can_post, reason = bot.scheduler.can_post_now()
            if not can_post:
                logger.info(f"Skipping post: {reason}")
                return None
        else:
            logger.info("Bypassing posting schedule check (force_post=True)")
            
        # Human-like delay before starting
        bot.scheduler.add_human_like_delay(min_seconds=5, max_seconds=15)
            
        # Get trending topic
        topic = bot.trending_service.get_trending_topic()
        logger.info(f"Selected trending topic: {topic}")
        
        # Human-like delay before generating headline
        bot.scheduler.add_human_like_delay(min_seconds=5, max_seconds=20)
        
        # Generate headline
        headline = bot.content_service.generate_headline(topic)
        logger.info(f"Generated headline: {headline}")
        
        # Human-like delay before generating content
        bot.scheduler.add_human_like_delay(min_seconds=10, max_seconds=30)
        
        # Generate blog post content
        content = bot.content_service.generate_blog_post(topic, headline)
        logger.info(f"Generated blog post with {len(content)} characters")
        
        # Add monetization elements
        content = bot.monetization_service.add_monetization_elements(content, topic)
        content = bot.monetization_service.optimize_for_adsense(content)
        
        # Human-like delay before image generation
        bot.scheduler.add_human_like_delay(min_seconds=5, max_seconds=15)
        
        # Generate and add image (only 70% of the time, like humans might not always include one)
        image_html = ""
        image_url = None
        if random.random() < 0.7:  # 70% chance to include an image
            logger.info("Generating image for the blog post...")
            image_result = bot.image_service.generate_image(topic)
            if image_result and 'url' in image_result:
                image_url = image_result['url']
                # Randomly choose image alignment
                align = random.choice(['left', 'center', 'right'])
                width = random.choice(['80%', '90%', '100%'])
                
                image_html = f'<div style="margin: 20px 0; text-align: {align};">\n'
                image_html += f'    <img src="{image_url}" alt="{headline}" style="max-width: {width}; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">\n'
                if random.random() > 0.3:  # 70% chance to include caption
                    image_html += f'    <p style="margin-top: 10px; font-style: italic; color: #666; text-align: {align};">Featured: {topic}</p>\n'
                image_html += '</div>\n\n'
                logger.info("Successfully generated and added featured image")
        
        # Add random signature
        signatures = [
            "Best regards,\nThe Team",
            "Happy reading!",
            "Until next time,",
            "Warm regards,",
            "Thanks for reading!",
            "Keep exploring!",
            "Your friendly content creator"
        ]
        
        # Format for email with image
        email_content = f"""
        <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h1 style="color: #2c3e50; text-align: center; margin-bottom: 20px;">{headline}</h1>
            {image_html}
            <div style="margin-top: 20px; text-align: justify;">
                {content}
            </div>
            <div style="margin: 30px 0; font-style: italic; color: #555;">
                <p>{random.choice(signatures)}</p>
            </div>
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 0.9em; color: #777; text-align: center;">
                <p>This email was sent by your BloggerBot. <a href="#" style="color: #3498db; text-decoration: none;">Unsubscribe</a> | <a href="#" style="color: #3498db; text-decoration: none;">Preferences</a></p>
                <p style="font-size: 0.8em; color: #999; margin-top: 10px;">{datetime.now().strftime('%B %d, %Y')}</p>
            </div>
        </div>
        """
        
        # Random delay before sending (like a human might do)
        send_delay = random.randint(30, 300)  # 30 seconds to 5 minutes
        logger.info(f"Waiting {send_delay} seconds before sending...")
        time.sleep(send_delay)
        
        return {
            'title': headline,
            'content': email_content,
            'topic': topic,
            'image_url': image_url
        }
        
    except Exception as e:
        logger.error(f"Error in blog post generation: {str(e)}", exc_info=True)
        return None

def send_blog_post_email(blog_post, email_type="newsletter"):
    """Send blog post via email"""
    logger = logging.getLogger('email_poster')
    
    try:
        gmail = GmailService(use_api=False)
        recipients = get_recipients()
        
        logger.info(f"Sending email to {len(recipients)} recipient(s)...")
        
        success = gmail.send_blog_post_email(
            title=blog_post['title'],
            content=blog_post['content'],
            recipients=recipients,
            email_type=email_type
        )
        
        if success:
            logger.info("Blog post email sent successfully!")
        else:
            logger.error("Failed to send blog post email")
            
        return success
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

def main(force_post=False):
    """Main function"""
    # Setup
    logger = setup_logging()
    load_env_file()
    
    logger.info("Starting Email Poster...")
    
    # Generate blog post using BloggerBot's complete flow
    logger.info("Generating blog post using BloggerBot's complete flow...")
    blog_post = generate_and_format_blog_post(force_post=force_post)
    
    if not blog_post:
        logger.error("Failed to generate blog post")
        return False
    
    # Send email
    email_types = ["newsletter", "blog_post", "digest", "announcement"]
    email_type = random.choice(email_types)
    
    logger.info(f"Sending as '{email_type}' email...")
    success = send_blog_post_email(blog_post, email_type)
    
    if success:
        logger.info("Email Poster completed successfully!")
    else:
        logger.error("Email Poster failed")
    
    return success

if __name__ == "__main__":
    import argparse
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Email Poster - Send blog posts via email')
    parser.add_argument('--force', action='store_true', help='Force post regardless of schedule')
    args = parser.parse_args()
    
    try:
        success = main(force_post=args.force)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)