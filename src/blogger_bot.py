"""
Main BloggerBot class that orchestrates the blog post generation and publishing process.
"""
import logging
import time
import random
from src.services.trending_topics import TrendingTopicsService
from src.services.content_generator import ContentGeneratorService
from src.services.image_service import ImageService
from src.services.blogger_service import BloggerService
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
        self.blogger_service = BloggerService()
        self.monetization_service = MonetizationService()
        
        # Initialize new human-like behavior services
        self.scheduler = PostingScheduler()
        self.diversity_service = ContentDiversityService()
        
        logging.info("Starting Blogger Bot with human-like behavior patterns")
    
    def run(self):
        """Run the blogger bot to create and publish a blog post with human-like behavior."""
        try:
            # Check if we should post now
            can_post, reason = self.scheduler.can_post_now()
            if not can_post:
                logging.info(f"[SKIP] Skipping post: {reason}")
                print("[SKIP] Not posting now: {reason}")
                next_time = self.scheduler.get_next_posting_time()
                print(f"Next suggested posting time: {next_time.strftime('%Y-%m-%d %H:%M')}")
                return False
            
            # Random chance to skip posting (human inconsistency)
            if self.scheduler.should_skip_posting_today():
                logging.info("Randomly skipping post today for human-like inconsistency")
                print("Skipping post today to maintain natural posting patterns")
                return False
            
            # Add initial human-like delay
            self.scheduler.add_human_like_delay()
            
            # Get trending topic
            topic = self.trending_service.get_trending_topic()
            logging.info(f"Selected trending topic: {topic}")
            
            # Check topic diversity
            is_similar, similarity_reason = self.diversity_service.is_topic_too_similar(topic)
            if is_similar:
                logging.info(f"Topic too similar: {similarity_reason}")
                # Try to get a more diverse topic
                diverse_topic = self.diversity_service.suggest_diverse_topic(topic)
                if diverse_topic != topic:
                    topic = diverse_topic
                    logging.info(f"Using diverse topic instead: {topic}")
            
            # Generate headline with human-like delay
            time.sleep(random.uniform(10, 30))  # Think time before generating headline
            headline = self.content_service.generate_headline(topic)
            logging.info(f"Generated headline: {headline}")
            
            # Generate blog post content with another delay
            time.sleep(random.uniform(15, 45))  # Think time before generating content
            content = self.content_service.generate_blog_post(topic, headline)
            content_length = len(content)
            logging.info(f"Generated blog post content of length: {content_length} characters")
            
            # Check content diversity
            diversity_check = self.diversity_service.check_content_diversity(content, topic)
            logging.info(f"Content diversity score: {diversity_check['overall_score']}/100")
            
            if diversity_check['overall_score'] < 60:
                logging.warning(f"Low diversity score. Issues: {diversity_check['issues']}")
                # Could regenerate content here if score is too low
            
            # Add monetization elements (ads, affiliate links, email signup)
            content = self.monetization_service.add_monetization_elements(content, topic)
            content = self.monetization_service.optimize_for_adsense(content)
            logging.info(f"Added monetization elements to content")
            
            # Human-like delay before image processing
            time.sleep(random.uniform(20, 60))
            
            # Get image for the blog post
            image_result = self.image_service.generate_image(topic)
            if image_result:
                logging.info(f"Successfully fetched image for topic: {topic}")
            else:
                logging.warning(f"Could not fetch image for topic: {topic}")
            
            # Check if Blogger service is initialized properly
            if not self.blogger_service.service:
                logging.error("Blogger service not initialized properly. Check your credentials and token.")
                print("Blogger service not initialized. Run 'python src/get_token.py' to refresh your token.")
                self.scheduler.record_post(topic, False)
                return False
            
            # Final human-like delay before posting
            self.scheduler.add_human_like_delay()
            
            # Post to Blogger
            logging.info("[POSTING] Posting to Blogger with human-like behavior...")
            post_url = self.blogger_service.post_to_blogger(headline, content, image_result)
            
            success = bool(post_url)
            
            # Record the posting attempt
            self.scheduler.record_post(topic, success, post_url)
            self.diversity_service.record_content(topic, content, success)
            
            if success:
                logging.info(f"Successfully published blog post: {post_url}")
                print(f"Blog post published successfully: {post_url}")
                
                # Show posting statistics
                stats = self.scheduler.get_posting_stats()
                print(f"Posting stats - Daily: {stats['daily_posts']}, Weekly: {stats['weekly_posts']}")
                print(f"Success rate: {stats['success_rate']:.1%}")
                
                diversity_stats = self.diversity_service.get_diversity_stats()
                print(f"Content diversity score: {diversity_stats.get('diversity_score', 'N/A'):.1f}/100")
                
                return True
            else:
                logging.error(f"Failed to publish blog post")
                print("Failed to publish blog post. Check the logs for details.")
                # Provide more helpful error information
                print("   Possible issues:")
                print("   1. API rate limit reached - wait a while before trying again")
                print("   2. Token expired - run 'python src/get_token.py' to refresh")
                print("   3. Permission issues - check your OAuth scopes and Blogger ID")
                print("   4. Content flagged as spam - check content quality")
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
