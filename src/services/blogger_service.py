"""Service for handling Blogger API operations."""
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ..utils.logger import setup_logging
from ..utils.config import load_blogger_token

logger = setup_logging()

class BloggerService:
    AVAILABLE_LABELS = [
        "Art",
        "Travel",
        "Life Style",
        "Photography",
        "Nature",
        "Food",
        "Adventure"
    ]

    def __init__(self, blog_id):
        self.blog_id = blog_id
        self.token_data = load_blogger_token()

    def classify_topic(self, topic):
        """Classify a topic into one of the available labels based on keywords."""
        topic_lower = topic.lower()
        
        # Keywords mapping for each label
        label_keywords = {
            "Art": ["art", "paint", "draw", "craft", "artist", "creative", "design", "music", "culture"],
            "Travel": ["travel", "destination", "tour", "trip", "explore", "visit", "tourism", "vacation", "journey"],
            "Life Style": ["lifestyle", "life", "living", "wellness", "health", "fashion", "trends", "personal", "self", "work"],
            "Photography": ["photo", "camera", "image", "picture", "photography", "capture", "shot", "photograph"],
            "Nature": ["nature", "environment", "wildlife", "climate", "earth", "eco", "green", "sustainable", "planet"],
            "Food": ["food", "cook", "recipe", "dish", "cuisine", "restaurant", "eat", "meal", "dining"],
            "Adventure": ["adventure", "outdoor", "extreme", "sport", "activity", "expedition", "challenge", "thrill"]
        }

        # Score each label based on keyword matches
        scores = {label: 0 for label in self.AVAILABLE_LABELS}
        for label, keywords in label_keywords.items():
            for keyword in keywords:
                if keyword in topic_lower:
                    scores[label] += 1

        # Get the label with highest score
        best_label = max(scores.items(), key=lambda x: x[1])[0]
        
        # If no good match found (score = 0), default to "Life Style" as it's most general
        if scores[best_label] == 0:
            return "Life Style"
            
        return best_label

    def post_to_blogger(self, title, content, max_retries=3):
        """Post content to Blogger with automatic label classification."""
        if not self.token_data:
            raise ValueError("Blogger token not found. Please run get_token.py first.")

        # Classify the topic into an appropriate label
        label = self.classify_topic(title)
        logger.info(f"📑 Classified topic under label: {label}")

        for attempt in range(max_retries):
            try:
                creds = Credentials.from_authorized_user_info(self.token_data)
                service = build('blogger', 'v3', credentials=creds)
                
                post = {
                    "kind": "blogger#post",
                    "title": title,
                    "content": content,
                    "labels": [label]
                }
                
                result = service.posts().insert(
                    blogId=self.blog_id,
                    body=post,
                    isDraft=False
                ).execute()
                
                logger.info(f"✅ Posted: {title}")
                logger.info(f"Post URL: {result.get('url', 'URL not available')}")
                return True
                
            except HttpError as e:
                if e.resp.status == 401:  # Unauthorized - token might be expired
                    logger.error("❌ Authentication failed. Please refresh the token by running get_token.py")
                    return False
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"HTTP error posting to Blogger (attempt {attempt + 1}): {str(e)}")
                time.sleep(5)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Error posting to Blogger (attempt {attempt + 1}): {str(e)}")
                time.sleep(5)
