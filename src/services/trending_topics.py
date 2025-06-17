"""Service for fetching trending topics."""
import random
from pytrends.request import TrendReq
from ..utils.logger import setup_logging

logger = setup_logging()

class TrendingTopics:
    DEFAULT_TOPICS = [
        "Latest Technology Trends 2025",
        "Artificial Intelligence Breakthroughs",
        "Sustainable Energy Solutions",
        "Digital Transformation",
        "Future of Work",
        "Cybersecurity Best Practices",
        "Innovation in Healthcare",
        "Space Exploration News",
        "Climate Change Solutions",
        "Blockchain Technology"
    ]

    @staticmethod
    def get_trending_topic():
        """Get a trending topic from Google Trends or fallback to default topics."""
        try:
            pytrends = TrendReq(hl='en-US', tz=360)  # Bangladesh timezone
            trending = pytrends.trending_searches(pn='bangladesh')
            if trending and len(trending) > 0:
                topic = trending[0]
                logger.info(f"Found trending topic: {topic}")
                return topic
        except Exception as e:
            logger.warning(f"Unable to fetch trending topics: {str(e)}")
        
        # Return a random topic from our default list if trending topics fetch failed
        topic = random.choice(TrendingTopics.DEFAULT_TOPICS)
        logger.info(f"Using default topic: {topic}")
        return topic
