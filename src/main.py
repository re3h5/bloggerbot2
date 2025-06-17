"""Main entry point for the Blogger Bot application."""
import time
import schedule
from src.utils.logger import setup_logging
from src.utils.config import BLOGGER_ID
from src.services.blogger_service import BloggerService
from src.services.content_generator import ContentGenerator
from src.services.trending_topics import TrendingTopics

logger = setup_logging()

def job():
    """Run one iteration of the bot's posting process."""
    try:
        # Get trending topic
        topic = TrendingTopics.get_trending_topic()
        logger.info(f"🧠 Trending topic: {topic}")
        
        # Generate content
        content = ContentGenerator.generate_blog_post(topic)
        logger.info(f"📝 Generated content length: {len(content)} characters")
        
        # Post to Blogger
        blogger_service = BloggerService(BLOGGER_ID)
        success = blogger_service.post_to_blogger(topic, content)
        
        if not success:
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during bot execution: {str(e)}")
        return False
    
    return True

def main():
    """Main function to start the bot and schedule regular posts."""
    logger.info("🤖 Starting Blogger Bot")
    
    # Schedule the job to run every hour
    schedule.every(1).hour.do(job)
    
    # Run the job immediately once
    job()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
