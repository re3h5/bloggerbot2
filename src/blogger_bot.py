"""
Main BloggerBot class that orchestrates the blog post generation and publishing process.
"""
import logging
import time
from src.services.trending_topics import TrendingTopicsService
from src.services.content_generator import ContentGeneratorService
from src.services.image_service import ImageService
from src.services.blogger_service import BloggerService
from src.services.monetization import MonetizationService
from src.utils.logger import setup_logger

class BloggerBot:
    """
    BloggerBot class that orchestrates the blog post generation and publishing process.
    """
    
    def __init__(self):
        """Initialize the BloggerBot with all required services."""
        # Set up logging
        setup_logger()
        
        # Initialize services
        self.trending_service = TrendingTopicsService()
        self.content_service = ContentGeneratorService()
        self.image_service = ImageService()
        self.blogger_service = BloggerService()
        self.monetization_service = MonetizationService()
        
        logging.info("🤖 Starting Blogger Bot")
    
    def run(self):
        """Run the blogger bot to create and publish a blog post."""
        try:
            # Get trending topic
            topic = self.trending_service.get_trending_topic()
            logging.info(f"📊 Selected trending topic: {topic}")
            
            # Generate headline
            headline = self.content_service.generate_headline(topic)
            logging.info(f"✍️ Generated headline: {headline}")
            
            # Generate blog post content
            content = self.content_service.generate_blog_post(topic, headline)
            content_length = len(content)
            logging.info(f"📝 Generated blog post content of length: {content_length} characters")
            
            # Add monetization elements (ads, affiliate links, email signup)
            content = self.monetization_service.add_monetization_elements(content, topic)
            content = self.monetization_service.optimize_for_adsense(content)
            logging.info(f"💰 Added monetization elements to content")
            
            # Get image for the blog post
            image_result = self.image_service.generate_image(topic)
            if image_result:
                logging.info(f"🖼️ Successfully fetched image for topic: {topic}")
            else:
                logging.warning(f"⚠️ Could not fetch image for topic: {topic}")
            
            # Check if Blogger service is initialized properly
            if not self.blogger_service.service:
                logging.error("❌ Blogger service not initialized properly. Check your credentials and token.")
                print("❌ Blogger service not initialized. Run 'python src/get_token.py' to refresh your token.")
                return False
            
            # Post to Blogger
            logging.info(f"[POSTING] Posting to Blogger...")
            post_url = self.blogger_service.post_to_blogger(headline, content, image_result)
            
            if post_url:
                logging.info(f"✅ Successfully published blog post: {post_url}")
                print(f"✅ Blog post published successfully: {post_url}")
                return True
            else:
                logging.error(f"❌ Failed to publish blog post")
                print("❌ Failed to publish blog post. Check the logs for details.")
                # Provide more helpful error information
                print("   Possible issues:")
                print("   1. API rate limit reached - wait a while before trying again")
                print("   2. Token expired - run 'python src/get_token.py' to refresh")
                print("   3. Permission issues - check your OAuth scopes and Blogger ID")
                return False
                
        except Exception as e:
            logging.error(f"❌ Error in BloggerBot: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return False
