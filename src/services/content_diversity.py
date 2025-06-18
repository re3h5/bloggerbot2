"""
Service for ensuring content diversity and preventing repetitive patterns.
"""
import logging
import json
import os
import hashlib
import random
from datetime import datetime, timedelta
from typing import List, Dict, Set
from collections import Counter

class ContentDiversityService:
    """Service to ensure content diversity and prevent spam-like repetition."""
    
    def __init__(self, config_file: str = "config/content_diversity.json"):
        self.config_file = config_file
        self.content_history = self._load_content_history()
        
        # Diversity thresholds
        self.min_topic_gap = 5  # Minimum posts between similar topics
        self.max_keyword_reuse = 3  # Max times a keyword can be used per week
        self.min_content_similarity = 0.7  # Minimum similarity threshold to flag
        
        # Topic categories for better diversity
        self.topic_categories = {
            'technology': ['AI', 'software', 'programming', 'tech', 'digital', 'innovation'],
            'business': ['marketing', 'startup', 'entrepreneur', 'finance', 'strategy'],
            'lifestyle': ['health', 'fitness', 'travel', 'food', 'wellness', 'productivity'],
            'education': ['learning', 'skills', 'training', 'development', 'course'],
            'entertainment': ['movies', 'games', 'music', 'books', 'culture'],
            'news': ['trends', 'current', 'breaking', 'update', 'latest']
        }
        
        # Writing variety templates
        self.content_angles = [
            "how-to guide",
            "trend analysis",
            "comparison review",
            "beginner's guide",
            "expert tips",
            "case study",
            "myth busting",
            "future predictions",
            "problem solving",
            "best practices"
        ]
    
    def _load_content_history(self) -> List[Dict]:
        """Load content history from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logging.warning("Could not load content history, starting fresh")
        return []
    
    def _save_content_history(self):
        """Save content history to file."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.content_history, f, indent=2)
    
    def _get_content_hash(self, content: str) -> str:
        """Generate a hash for content similarity checking."""
        # Remove HTML tags and normalize text for comparison
        import re
        clean_content = re.sub(r'<[^>]+>', '', content.lower())
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        return hashlib.md5(clean_content.encode()).hexdigest()
    
    def _extract_keywords(self, content: str) -> Set[str]:
        """Extract keywords from content for diversity tracking."""
        import re
        # Simple keyword extraction - remove HTML and get significant words
        clean_content = re.sub(r'<[^>]+>', '', content.lower())
        words = re.findall(r'\b[a-z]{4,}\b', clean_content)
        
        # Filter out common words
        stop_words = {
            'this', 'that', 'with', 'have', 'will', 'from', 'they', 'know',
            'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when',
            'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over',
            'such', 'take', 'than', 'them', 'well', 'were', 'what', 'your'
        }
        
        keywords = set(word for word in words if word not in stop_words)
        return keywords
    
    def _categorize_topic(self, topic: str) -> str:
        """Categorize a topic into predefined categories."""
        topic_lower = topic.lower()
        
        for category, keywords in self.topic_categories.items():
            if any(keyword in topic_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def is_topic_too_similar(self, new_topic: str) -> tuple[bool, str]:
        """Check if the new topic is too similar to recent posts."""
        if not self.content_history:
            return False, "No previous content to compare"
        
        new_category = self._categorize_topic(new_topic)
        
        # Check recent posts for same category
        recent_posts = self.content_history[-self.min_topic_gap:]
        same_category_count = sum(
            1 for post in recent_posts 
            if self._categorize_topic(post['topic']) == new_category
        )
        
        if same_category_count >= 2:
            return True, f"Too many recent posts in '{new_category}' category"
        
        # Check for exact topic similarity
        for post in recent_posts:
            similarity = self._calculate_topic_similarity(new_topic, post['topic'])
            if similarity > 0.8:
                return True, f"Topic too similar to recent post: {post['topic']}"
        
        return False, "Topic is sufficiently different"
    
    def _calculate_topic_similarity(self, topic1: str, topic2: str) -> float:
        """Calculate similarity between two topics."""
        words1 = set(topic1.lower().split())
        words2 = set(topic2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def suggest_diverse_topic(self, original_topic: str) -> str:
        """Suggest a more diverse topic if the original is too similar."""
        category = self._categorize_topic(original_topic)
        
        # Find underrepresented categories
        recent_categories = [
            self._categorize_topic(post['topic']) 
            for post in self.content_history[-10:]
        ]
        category_counts = Counter(recent_categories)
        
        # Find least used category
        all_categories = list(self.topic_categories.keys())
        underused_categories = [
            cat for cat in all_categories 
            if category_counts.get(cat, 0) < 2
        ]
        
        if underused_categories:
            suggested_category = random.choice(underused_categories)
            angle = random.choice(self.content_angles)
            
            # Create a diverse topic suggestion
            category_keywords = self.topic_categories[suggested_category]
            main_keyword = random.choice(category_keywords)
            
            diverse_topic = f"{angle.title()}: {main_keyword.title()} Trends"
            logging.info(f"🎯 Suggesting diverse topic: {diverse_topic} (category: {suggested_category})")
            return diverse_topic
        
        return original_topic
    
    def check_content_diversity(self, content: str, topic: str) -> Dict:
        """Comprehensive diversity check for new content."""
        diversity_score = {
            'overall_score': 100,
            'issues': [],
            'suggestions': []
        }
        
        # Check topic similarity
        is_similar, reason = self.is_topic_too_similar(topic)
        if is_similar:
            diversity_score['overall_score'] -= 30
            diversity_score['issues'].append(f"Topic similarity: {reason}")
            diversity_score['suggestions'].append("Consider a different topic category")
        
        # Check keyword overuse
        content_keywords = self._extract_keywords(content)
        week_ago = datetime.now() - timedelta(days=7)
        recent_keywords = set()
        
        for post in self.content_history:
            if datetime.fromisoformat(post['timestamp']) > week_ago:
                recent_keywords.update(post.get('keywords', []))
        
        overused_keywords = content_keywords.intersection(recent_keywords)
        if len(overused_keywords) > 5:
            diversity_score['overall_score'] -= 20
            diversity_score['issues'].append(f"Keyword overuse: {len(overused_keywords)} repeated keywords")
            diversity_score['suggestions'].append("Use more varied vocabulary and synonyms")
        
        # Check content length diversity
        content_length = len(content)
        recent_lengths = [
            post['content_length'] for post in self.content_history[-5:]
            if 'content_length' in post
        ]
        
        if recent_lengths:
            avg_length = sum(recent_lengths) / len(recent_lengths)
            if abs(content_length - avg_length) < 200:
                diversity_score['overall_score'] -= 10
                diversity_score['issues'].append("Content length too similar to recent posts")
                diversity_score['suggestions'].append("Vary content length more significantly")
        
        return diversity_score
    
    def record_content(self, topic: str, content: str, success: bool):
        """Record new content for diversity tracking."""
        content_record = {
            'timestamp': datetime.now().isoformat(),
            'topic': topic,
            'category': self._categorize_topic(topic),
            'content_hash': self._get_content_hash(content),
            'content_length': len(content),
            'keywords': list(self._extract_keywords(content)),
            'success': success
        }
        
        self.content_history.append(content_record)
        
        # Keep only last 50 records to prevent file from growing too large
        if len(self.content_history) > 50:
            self.content_history = self.content_history[-50:]
        
        self._save_content_history()
        logging.info(f"📝 Recorded content diversity data for: {topic}")
    
    def get_diversity_stats(self) -> Dict:
        """Get statistics about content diversity."""
        if not self.content_history:
            return {'message': 'No content history available'}
        
        # Category distribution
        categories = [post['category'] for post in self.content_history[-20:]]
        category_dist = Counter(categories)
        
        # Recent keyword usage
        week_ago = datetime.now() - timedelta(days=7)
        recent_keywords = []
        for post in self.content_history:
            if datetime.fromisoformat(post['timestamp']) > week_ago:
                recent_keywords.extend(post.get('keywords', []))
        
        keyword_freq = Counter(recent_keywords)
        
        return {
            'total_posts': len(self.content_history),
            'category_distribution': dict(category_dist),
            'most_common_keywords': keyword_freq.most_common(10),
            'diversity_score': self._calculate_overall_diversity_score(),
            'recommendations': self._get_diversity_recommendations()
        }
    
    def _calculate_overall_diversity_score(self) -> float:
        """Calculate overall diversity score (0-100)."""
        if len(self.content_history) < 5:
            return 100.0  # Not enough data to judge
        
        recent_posts = self.content_history[-10:]
        
        # Category diversity
        categories = [post['category'] for post in recent_posts]
        unique_categories = len(set(categories))
        category_score = min(unique_categories / 5 * 100, 100)
        
        # Topic similarity score
        topics = [post['topic'] for post in recent_posts]
        similarity_penalties = 0
        for i, topic1 in enumerate(topics):
            for topic2 in topics[i+1:]:
                if self._calculate_topic_similarity(topic1, topic2) > 0.7:
                    similarity_penalties += 1
        
        similarity_score = max(100 - (similarity_penalties * 20), 0)
        
        # Overall score
        return (category_score + similarity_score) / 2
    
    def _get_diversity_recommendations(self) -> List[str]:
        """Get recommendations for improving content diversity."""
        recommendations = []
        
        if len(self.content_history) < 5:
            return ["Continue creating content to build diversity metrics"]
        
        recent_posts = self.content_history[-10:]
        categories = [post['category'] for post in recent_posts]
        category_counts = Counter(categories)
        
        # Check for over-represented categories
        for category, count in category_counts.items():
            if count > 3:
                recommendations.append(f"Reduce posts in '{category}' category")
        
        # Check for under-represented categories
        all_categories = set(self.topic_categories.keys())
        used_categories = set(categories)
        unused_categories = all_categories - used_categories
        
        if unused_categories:
            recommendations.append(f"Consider topics in: {', '.join(unused_categories)}")
        
        # Check content length variety
        lengths = [post['content_length'] for post in recent_posts]
        if max(lengths) - min(lengths) < 500:
            recommendations.append("Vary content length more (short vs. long-form)")
        
        return recommendations or ["Content diversity looks good!"]
