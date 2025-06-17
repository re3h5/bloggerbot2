"""
Service for keyword research and topic diversification.
"""
import random
import json
import os
from datetime import datetime, timedelta
import logging

class KeywordResearchService:
    """Service for researching keywords and diversifying topics."""
    
    def __init__(self):
        self.used_topics_file = "analytics/used_topics.json"
        self.ensure_topics_file()
        
        # High-value, low-competition keywords by category
        self.keyword_categories = {
            "technology": {
                "primary": ["AI tools", "productivity apps", "tech trends 2025", "software reviews"],
                "long_tail": ["best AI tools for small business", "how to choose productivity software", "latest tech trends for entrepreneurs", "free software alternatives"],
                "commercial": ["buy tech gadgets", "software deals", "tech product reviews", "gadget comparisons"]
            },
            "business": {
                "primary": ["startup tips", "business growth", "marketing strategies", "entrepreneurship"],
                "long_tail": ["how to start online business", "small business marketing ideas", "entrepreneur success stories", "business automation tools"],
                "commercial": ["business software", "marketing tools", "startup resources", "business courses"]
            },
            "health": {
                "primary": ["wellness tips", "fitness routines", "healthy lifestyle", "mental health"],
                "long_tail": ["home workout routines for beginners", "healthy meal prep ideas", "stress management techniques", "sleep improvement tips"],
                "commercial": ["fitness equipment", "health supplements", "wellness products", "fitness apps"]
            },
            "finance": {
                "primary": ["personal finance", "investment tips", "money management", "financial planning"],
                "long_tail": ["how to save money fast", "investment strategies for beginners", "budgeting tips for families", "passive income ideas"],
                "commercial": ["financial software", "investment platforms", "budgeting apps", "financial courses"]
            },
            "lifestyle": {
                "primary": ["home improvement", "travel tips", "cooking recipes", "fashion trends"],
                "long_tail": ["DIY home projects on budget", "travel hacks for families", "easy healthy recipes", "affordable fashion tips"],
                "commercial": ["home decor", "travel gear", "kitchen appliances", "fashion accessories"]
            }
        }
    
    def ensure_topics_file(self):
        """Ensure used topics tracking file exists."""
        os.makedirs("analytics", exist_ok=True)
        
        if not os.path.exists(self.used_topics_file):
            initial_data = {
                "used_topics": [],
                "topic_performance": {},
                "last_reset": datetime.now().isoformat()
            }
            with open(self.used_topics_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
    
    def get_diverse_topic(self, base_topic):
        """Get a diverse, SEO-optimized topic based on the base topic."""
        try:
            # Load used topics
            with open(self.used_topics_file, 'r') as f:
                data = json.load(f)
            
            # Reset used topics weekly to allow repetition
            last_reset = datetime.fromisoformat(data["last_reset"])
            if datetime.now() - last_reset > timedelta(days=7):
                data["used_topics"] = []
                data["last_reset"] = datetime.now().isoformat()
            
            # Categorize the base topic
            category = self._categorize_topic(base_topic.lower())
            
            # Get keyword variations
            keywords = self.keyword_categories.get(category, self.keyword_categories["lifestyle"])
            
            # Select unused topic variation
            all_variations = keywords["primary"] + keywords["long_tail"] + keywords["commercial"]
            unused_variations = [v for v in all_variations if v not in data["used_topics"]]
            
            if not unused_variations:
                # If all used, reset and use any
                unused_variations = all_variations
                data["used_topics"] = []
            
            # Select topic with commercial intent bias (higher earning potential)
            commercial_topics = [t for t in unused_variations if t in keywords["commercial"]]
            long_tail_topics = [t for t in unused_variations if t in keywords["long_tail"]]
            
            # 40% commercial, 40% long-tail, 20% primary
            rand = random.random()
            if rand < 0.4 and commercial_topics:
                selected_topic = random.choice(commercial_topics)
            elif rand < 0.8 and long_tail_topics:
                selected_topic = random.choice(long_tail_topics)
            else:
                selected_topic = random.choice(unused_variations)
            
            # Add year for freshness
            if "2025" not in selected_topic:
                selected_topic += " 2025"
            
            # Track usage
            data["used_topics"].append(selected_topic)
            
            # Save updated data
            with open(self.used_topics_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logging.info(f"🎯 Selected diverse topic: {selected_topic}")
            return selected_topic
            
        except Exception as e:
            logging.error(f"❌ Error getting diverse topic: {str(e)}")
            return base_topic + " 2025"  # Fallback
    
    def _categorize_topic(self, topic):
        """Categorize topic for keyword selection."""
        if any(word in topic for word in ['tech', 'ai', 'software', 'app', 'digital', 'computer']):
            return 'technology'
        elif any(word in topic for word in ['business', 'startup', 'entrepreneur', 'marketing', 'growth']):
            return 'business'
        elif any(word in topic for word in ['health', 'fitness', 'wellness', 'nutrition', 'medical']):
            return 'health'
        elif any(word in topic for word in ['finance', 'money', 'investment', 'budget', 'income']):
            return 'finance'
        else:
            return 'lifestyle'
    
    def get_related_keywords(self, topic):
        """Get related keywords for the topic."""
        category = self._categorize_topic(topic.lower())
        keywords = self.keyword_categories.get(category, self.keyword_categories["lifestyle"])
        
        # Mix of different keyword types
        related = []
        related.extend(random.sample(keywords["primary"], min(2, len(keywords["primary"]))))
        related.extend(random.sample(keywords["long_tail"], min(3, len(keywords["long_tail"]))))
        related.extend(random.sample(keywords["commercial"], min(2, len(keywords["commercial"]))))
        
        return related[:8]  # Return top 8 related keywords
    
    def optimize_topic_for_seo(self, topic):
        """Optimize topic for better SEO performance."""
        # Add power words for better CTR
        power_words = [
            "Ultimate Guide", "Complete", "Essential", "Proven", "Expert", 
            "Advanced", "Beginner's", "Step-by-Step", "Comprehensive", "Latest"
        ]
        
        # Add year for freshness
        current_year = datetime.now().year
        
        # Add commercial intent modifiers
        commercial_modifiers = [
            "Best", "Top", "Reviews", "Comparison", "vs", "Alternatives", 
            "Deals", "Discounts", "Free", "Premium"
        ]
        
        # Randomly enhance the topic
        rand = random.random()
        if rand < 0.3:
            # Add power word
            power_word = random.choice(power_words)
            topic = f"{power_word} {topic}"
        elif rand < 0.6:
            # Add commercial modifier
            commercial = random.choice(commercial_modifiers)
            topic = f"{commercial} {topic}"
        
        # Ensure year is included
        if str(current_year) not in topic:
            topic += f" {current_year}"
        
        return topic
    
    def get_trending_modifiers(self):
        """Get trending modifiers to add to topics."""
        return [
            "in 2025", "for beginners", "step by step", "complete guide",
            "expert tips", "latest trends", "proven strategies", "advanced techniques",
            "comprehensive review", "detailed analysis", "practical guide", "essential tips"
        ]
