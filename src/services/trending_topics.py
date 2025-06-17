"""
Service for fetching trending topics from various sources.
"""
import random
import logging
import requests
import time
import pandas as pd
import warnings
from pytrends.request import TrendReq
from src.utils.config import OPENROUTER_API_KEY

# Suppress pandas FutureWarning from pytrends
warnings.filterwarnings('ignore', category=FutureWarning, module='pytrends')

class TrendingTopicsService:
    """Service for fetching trending topics from various sources."""
    
    def __init__(self):
        # Default topics to use as final fallback
        self.default_topics = [
            "Digital Marketing Strategies",
            "Renewable Energy Solutions",
            "Remote Work Best Practices",
            "Financial Planning Strategies",
            "Smart Home Technology",
            "Travel Destinations 2025",
            "Fitness and Nutrition Trends",
            "Personal Development Tips",
            "Photography Techniques",
            "Cooking and Recipe Ideas"
        ]
    
    def get_trending_topic(self):
        """
        Get a trending topic using multiple methods with fallbacks.
        Returns a single trending topic as a string.
        """
        # Try Google Trends methods first
        try:
            # Use multiple working Google Trends approaches
            pytrends = TrendReq(hl='en-US', tz=360)
            
            # Method 1: Try Google Trends interest over time with rotating categories
            try:
                all_categories = [
                    'technology', 'health', 'business', 'entertainment', 'sports',
                    'science', 'education', 'travel', 'food', 'fashion',
                    'finance', 'politics', 'environment', 'lifestyle', 'culture',
                    'cryptocurrency', 'btc', 'eth'
                ]
                # Select 5 random categories each time for variety
                selected_categories = random.sample(all_categories, 5)
                
                pytrends.build_payload(selected_categories, timeframe='now 1-d')
                interest_data = pytrends.interest_over_time()
                
                if not interest_data.empty:
                    # Get category with highest interest
                    highest_category = interest_data.mean().idxmax()
                    topic = highest_category.capitalize() + " Trends 2025"
                    logging.info(f"Found trending category from Google Trends: {topic}")
                    return topic
            except Exception as e:
                logging.info(f"Google Trends interest_over_time method failed: {str(e)}")
            
            # Method 2: Try Google Trends suggestions API
            try:
                suggestions = pytrends.suggestions(keyword='trending')
                if suggestions and len(suggestions) > 0:
                    # Get a random suggestion from the list
                    suggestion = random.choice(suggestions[:5])  # Top 5 suggestions
                    if 'title' in suggestion:
                        topic = suggestion['title']
                        logging.info(f"Found suggested topic from Google Trends: {topic}")
                        return topic
                    else:
                        logging.info(f"Google Trends suggestions method failed: No title found in suggestion")
                else:
                    logging.info(f"Google Trends suggestions method failed: No suggestions found")
            except Exception as e:
                logging.info(f"Google Trends suggestions method failed: {str(e)}")
                
        except Exception as e:
            logging.info(f"All Google Trends methods failed: {str(e)}")
        
        # Method 3: Try AI-generated trending topic as second fallback
        try:
            ai_topic = self.get_ai_trending_topic()
            if ai_topic:
                logging.info(f"Using AI-suggested trending topic: {ai_topic}")
                return ai_topic
        except Exception as e:
            logging.info(f"AI trending topic generation failed: {str(e)}")
        
        # Method 4: Use curated tech keywords as third fallback
        try:
            trending_keywords = ["AI", "Machine Learning", "Blockchain", "Cybersecurity", "Sustainability"]
            topic = random.choice(trending_keywords)
            logging.info(f"Using curated tech topic: {topic}")
            return topic
        except Exception as e:
            logging.info(f"Curated tech topics method failed: {str(e)}")
        
        # Method 5: If all else fails, fall back to default topics
        topic = random.choice(self.default_topics)
        logging.info(f"Using default topic: {topic}")
        return topic
    
    def get_ai_trending_topic(self, max_retries=2):
        """Get trending topic suggestions from AI when Google Trends fails."""
        system_message = (
            "You are a trend forecasting expert with deep knowledge of current global trends. "
            "Your job is to suggest a single trending topic that would make for an engaging blog post. "
            "Focus on topics that are currently popular or emerging in technology, culture, business, "
            "health, or lifestyle."
        )
        
        prompt = (
            "Suggest ONE trending topic for a blog post today. \n\n"
            "Requirements:\n"
            "1. The topic should be currently trending or emerging\n"
            "2. It should be specific enough to write about (not too broad)\n"
            "3. It should be interesting to a general audience\n"
            "4. Return ONLY the topic name with no additional text, quotes, or formatting\n"
            "5. Keep it under 5 words if possible"
        )

        for attempt in range(max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/blog-bot",
                }
                
                payload = {
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 50
                }
                
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
                    topic = response_data["choices"][0]["message"]["content"].strip()
                    # Clean up the topic (remove quotes, periods, etc.)
                    topic = topic.strip('"\'\n.')
                    return topic
                
            except Exception as e:
                logging.warning(f"Error getting AI trending topic (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(2)
        
        return None
