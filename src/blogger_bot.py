"""
Main BloggerBot class that orchestrates the blog post generation and publishing process.
"""
import logging
import time
import random
from src.services.trending_topics import TrendingTopicsService
from src.services.content_generator import ContentGeneratorService
from src.services.image_service import ImageService
from .services.email_bot_manager import EmailBotManager
from src.services.monetization import MonetizationService
from src.services.posting_scheduler import PostingScheduler
from src.services.content_diversity import ContentDiversityService
from src.utils.logger import setup_logger

class BloggerBot:
    """
    BloggerBot class that orchestrates the blog post generation and publishing process
    with human-like behavior and spam prevention.
    """
    
    def __init__(self):
        """Initialize the BloggerBot with all required services."""
        # Set up logging
        setup_logger()
        
        # Initialize services
        self.trending_service = TrendingTopicsService()
        self.content_service = ContentGeneratorService()
        self.image_service = ImageService()
        self.email_manager = EmailBotManager()  # Replace blogger service with email manager
        self.monetization_service = MonetizationService()
        
        # Initialize new human-like behavior services
        self.scheduler = PostingScheduler()
        self.diversity_service = ContentDiversityService()
        
        logging.info("Starting Blogger Bot with human-like behavior patterns and email-based posting")
    
    def run(self):
        """Run the blogger bot to create and publish a blog post with human-like behavior."""
        try:
            # Check if we should post now
            can_post, reason = self.scheduler.can_post_now()
            if not can_post:
                logging.info(f"[SKIP] Skipping post: {reason}")
                print(f"[SKIP] Not posting now: {reason}")
                next_time = self.scheduler.get_next_posting_time()
                print(f"Next suggested posting time: {next_time.strftime('%Y-%m-%d %H:%M')}")
                return False
            
            # Random chance to skip posting (human inconsistency)
            if not self.scheduler.force_post and self.scheduler.should_skip_posting_today():
                logging.info("Randomly skipping post today for human-like inconsistency")
                print("Skipping post today to maintain natural posting patterns")
                return False
            
            # Add initial human-like delay
            self.scheduler.add_human_like_delay()
            
            # Get trending topic
            topic = self.trending_service.get_trending_topic()
            logging.info(f"Selected trending topic: {topic}")
            
            # Check topic diversity
            if not self.scheduler.force_post:
                is_similar, similarity_reason = self.diversity_service.is_topic_too_similar(topic)
                if is_similar:
                    logging.info(f"Topic too similar: {similarity_reason}")
                    # Try to get a more diverse topic
                    diverse_topic = self.diversity_service.suggest_diverse_topic(topic)
                    if diverse_topic != topic:
                        topic = diverse_topic
                        logging.info(f"Using diverse topic instead: {topic}")
            
            # Generate headline with human-like delay
            if not self.scheduler.force_post:
                time.sleep(random.uniform(10, 30))  # Think time before generating headline
            headline = self.content_service.generate_headline(topic)
            logging.info(f"Generated headline: {headline}")
            
            # Generate blog post content with another delay
            if not self.scheduler.force_post:
                time.sleep(random.uniform(15, 45))  # Think time before generating content
            content = self.content_service.generate_blog_post(topic, headline)
            content_length = len(content)
            logging.info(f"Generated blog post content of length: {content_length} characters")
            
            # Check content diversity
            if not self.scheduler.force_post:
                diversity_check = self.diversity_service.check_content_diversity(content, topic)
                logging.info(f"Content diversity score: {diversity_check['overall_score']}/100")
                
                if diversity_check['overall_score'] < 60:
                    logging.warning(f"Low diversity score. Issues: {diversity_check['issues']}")
            
            # Add monetization elements (ads, affiliate links, email signup)
            content = self.monetization_service.add_monetization_elements(content, topic)
            content = self.monetization_service.optimize_for_adsense(content)
            logging.info(f"Added monetization elements to content")
            
            # Human-like delay before image processing
            if not self.scheduler.force_post:
                time.sleep(random.uniform(20, 60))
            
            # Get image for the blog post
            image_result = self.image_service.generate_image(topic)
            if image_result:
                logging.info(f"Successfully fetched image for topic: {topic}")
            else:
                logging.warning(f"Could not fetch image for topic: {topic}")
            
            # Final human-like delay before posting
            self.scheduler.add_human_like_delay()
            
            # Post to Blogger via Email
            logging.info("[POSTING] Sending blog post via email...")
            success = self.email_manager.send_blog_post(
                title=headline,
                content=content,
                images=[image_result] if image_result else None
            )
            
            # Record the posting attempt
            self.scheduler.record_post(topic, success)
            self.diversity_service.record_content(topic, content, success)
            
            if success:
                logging.info(f"Successfully sent blog post via email: {headline}")
                print(f"Blog post sent via email successfully!")
                
                # Show posting statistics
                stats = self.scheduler.get_posting_stats()
                print(f"Posting stats - Daily: {stats['daily_posts']}, Weekly: {stats['weekly_posts']}")
                print(f"Success rate: {stats['success_rate']:.1%}")
                
                diversity_stats = self.diversity_service.get_diversity_stats()
                print(f"Content diversity score: {diversity_stats.get('diversity_score', 'N/A'):.1f}/100")
                
                return True
            else:
                logging.error(f"Failed to send blog post via email")
                print("Failed to send blog post via email. Check the logs for details.")
                # Provide more helpful error information
                print("   Possible issues:")
                print("   1. Email configuration incorrect - check credentials.json")
                print("   2. SMTP connection failed - check your internet connection")
                print("   3. Invalid recipient email - verify email address")
                print("   4. Authentication failed - verify sender email and password")
                return False
                
        except Exception as e:
            logging.error(f"Error in BloggerBot: {str(e)}")
            print(f"Error: {str(e)}")
            
            # Record failed attempt
            topic = getattr(self, '_current_topic', 'unknown')
            self.scheduler.record_post(topic, False)
            
            return False
    
    def get_bot_status(self):
        """Get comprehensive bot status and recommendations."""
        posting_stats = self.scheduler.get_posting_stats()
        diversity_stats = self.diversity_service.get_diversity_stats()
        
        status = {
            'can_post_now': self.scheduler.can_post_now(),
            'next_posting_time': posting_stats['next_posting_time'],
            'posting_pattern': posting_stats['current_pattern'],
            'recent_performance': {
                'daily_posts': posting_stats['daily_posts'],
                'weekly_posts': posting_stats['weekly_posts'],
                'success_rate': posting_stats['success_rate']
            },
            'content_diversity': {
                'score': diversity_stats.get('diversity_score', 0),
                'recommendations': diversity_stats.get('recommendations', [])
            }
        }
        
        return status
