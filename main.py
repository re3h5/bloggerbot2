import os
import logging
import time
import random
import schedule
import requests
import re
from datetime import datetime
from pytrends.request import TrendReq
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import (
    OPENROUTER_API_KEY,
    BLOGGER_ID,
    load_blogger_token
)

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('blogger_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# OpenRouter configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

class BloggerBot:
    # Available Blogger labels
    AVAILABLE_LABELS = [
        "Art",
        "Travel",
        "Life Style",
        "Photography",
        "Nature",
        "Food",
        "Adventure"
    ]

    def __init__(self):
        self.token_data = load_blogger_token()
        self.blog_id = BLOGGER_ID
        self.last_topics = set()  # Keep track of recently used topics

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

    def get_trending_topic(self):
        # List of engaging topics that are always relevant
        default_topics = [
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
        
        try:
            # Try to get trending topics from pytrends
            pytrends = TrendReq(hl='en-US', tz=360)  # Bangladesh timezone
            trending = pytrends.trending_searches(pn='bangladesh')
            if trending and len(trending) > 0:
                topic = trending[0]
                logging.info(f"Found trending topic: {topic}")
                return topic
        except Exception as e:
            logging.warning(f"Unable to fetch trending topics: {str(e)}")
        
        # Return a random topic from our default list if trending topics fetch failed
        topic = random.choice(default_topics)
        logging.info(f"Using default topic: {topic}")
        return topic
            
            # If trending topics fetch failed, we'll use default topics (handled in except block)

    def generate_blog_post(self, topic, max_retries=3):
        system_message = (
            "You are a professional blog writer and SEO expert. Write engaging, well-researched, "
            "and informative content that is optimized for search engines. Use a conversational "
            "yet professional tone. Format the content with proper HTML tags for better presentation "
            "and SEO optimization."
        )
        
        prompt = (
            f"Write an engaging and SEO-optimized blog post about: {topic}\n\n"
            f"Requirements:\n"
            f"1. Around 800-1000 words for better SEO performance\n"
            f"2. Include a compelling meta description (150-160 characters) at the very top as: <meta-description>Your description here</meta-description>\n"
            f"3. Include 5 relevant keywords/phrases for the topic as: <keywords>keyword1, keyword2, keyword3, keyword4, keyword5</keywords>\n"
            f"4. Include an SEO-optimized title (different from the main topic) as: <seo-title>Your SEO Title Here</seo-title>\n"
            f"5. Include a brief introduction that hooks the reader\n"
            f"6. Use proper heading hierarchy (h2, h3) with keywords in headings\n"
            f"7. Include at least one bulleted or numbered list\n"
            f"8. Use 2-3 subheadings (h2) with the main keyword included naturally\n"
            f"9. Write short paragraphs (3-4 sentences max) for better readability\n"
            f"10. Include a conclusion with a call to action\n"
            f"11. Format with semantic HTML tags for better SEO and readability\n"
        )

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/blog-bot",
            "OR-ORGANIZATION": "github.com/blog-bot"
        }

        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 0.9
        }

        for attempt in range(max_retries):
            try:
                # Use requests library directly instead of OpenAI client
                response = requests.post(
                    OPENROUTER_API_URL,
                    headers=headers,
                    json=data
                )
                
                # Print the raw response for debugging
                logging.info(f"API Response Status: {response.status_code}")
                
                # If there's an error, log the full response
                if response.status_code != 200:
                    logging.error(f"API Error Response: {response.text}")
                    response.raise_for_status()
                
                # Parse the response
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Log successful generation
                logging.info(f"Successfully generated content of length: {len(content)}")
                
                return content
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logging.warning(f"Error generating blog post (attempt {attempt + 1}): {str(e)}")
                time.sleep(5)

    def post_to_blogger(self, title, content, max_retries=3):
        if not self.token_data:
            raise ValueError("Blogger token not found. Please run get_token.py first.")

        # Extract SEO elements from content
        meta_description = ""
        keywords = []
        seo_title = title
        
        # Extract meta description
        meta_desc_match = re.search(r'<meta-description>(.*?)</meta-description>', content)
        if meta_desc_match:
            meta_description = meta_desc_match.group(1).strip()
            content = content.replace(meta_desc_match.group(0), '')
            logging.info(f"📊 Meta Description: {meta_description}")
        
        # Extract keywords
        keywords_match = re.search(r'<keywords>(.*?)</keywords>', content)
        if keywords_match:
            keywords_text = keywords_match.group(1).strip()
            keywords = [k.strip() for k in keywords_text.split(',')]
            content = content.replace(keywords_match.group(0), '')
            logging.info(f"🔑 Keywords: {', '.join(keywords)}")
        
        # Extract SEO title
        seo_title_match = re.search(r'<seo-title>(.*?)</seo-title>', content)
        if seo_title_match:
            seo_title = seo_title_match.group(1).strip()
            content = content.replace(seo_title_match.group(0), '')
            logging.info(f"📰 SEO Title: {seo_title}")
        
        # Classify the topic into an appropriate label
        label = self.classify_topic(title)
        logging.info(f"📑 Classified topic under label: {label}")
        
        # Add all keywords as labels for better categorization
        all_labels = [label] + keywords
        # Remove duplicates and ensure they're all strings
        all_labels = list(set([str(lbl) for lbl in all_labels]))

        for attempt in range(max_retries):
            try:
                creds = Credentials.from_authorized_user_info(self.token_data)
                service = build('blogger', 'v3', credentials=creds)
                
                # Create post with SEO elements
                post = {
                    "kind": "blogger#post",
                    "title": seo_title,  # Use SEO-optimized title
                    "content": content,
                    "labels": all_labels  # Use all labels including keywords
                }
                
                # Add meta description if available
                if meta_description:
                    # Blogger API doesn't directly support meta descriptions,
                    # but we can add it as a custom field or in the content
                    meta_html = f'<div style="display:none"><meta name="description" content="{meta_description}"></div>'
                    post["content"] = meta_html + post["content"]
                
                result = service.posts().insert(
                    blogId=self.blog_id,
                    body=post,
                    isDraft=False
                ).execute()
                
                logging.info(f"✅ Posted: {seo_title}")
                logging.info(f"Post URL: {result.get('url', 'URL not available')}")
                return True
                
            except HttpError as e:
                if e.resp.status == 401:  # Unauthorized - token might be expired
                    logging.error("❌ Authentication failed. Please refresh the token by running get_token.py")
                    return False
                if attempt == max_retries - 1:
                    raise
                logging.warning(f"HTTP error posting to Blogger (attempt {attempt + 1}): {str(e)}")
                time.sleep(5)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logging.warning(f"Error posting to Blogger (attempt {attempt + 1}): {str(e)}")
                time.sleep(5)

    def run(self):
        try:
            topic = self.get_trending_topic()
            logging.info(f"🧠 Trending topic: {topic}")
            
            content = self.generate_blog_post(topic)
            logging.info(f"📝 Generated content length: {len(content)} characters")
            
            # Post to Blogger (label classification is done inside post_to_blogger)
            success = self.post_to_blogger(topic, content)
            if not success:
                return False
                
        except Exception as e:
            logging.error(f"❌ Error during bot execution: {str(e)}")
            return False
        
        return True

def job():
    bot = BloggerBot()
    bot.run()

def main():
    logging.info("🤖 Starting Blogger Bot")
    
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
