import os
import logging
import time
import random
import schedule
import requests
import re
import base64
import io
from datetime import datetime
from pytrends.request import TrendReq
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image
from config import (
    OPENROUTER_API_KEY,
    BLOGGER_ID,
    PIXABAY_API_KEY,
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
            "Blockchain Technology",
            "Remote Work Best Practices",
            "Mental Health and Wellness",
            "Sustainable Living Tips",
            "Financial Planning Strategies",
            "Smart Home Technology",
            "Travel Destinations 2025",
            "Fitness and Nutrition Trends",
            "Personal Development Tips",
            "Photography Techniques",
            "Cooking and Recipe Ideas"
        ]
        
        try:
            # Use multiple working Google Trends approaches
            pytrends = TrendReq(hl='en-US', tz=360)
            
            # Method 1: Simple keyword-based approach
            trending_keywords = ["AI", "Machine Learning", "Blockchain", "Cybersecurity", "Sustainability"]
            topic = random.choice(trending_keywords)
            logging.info(f"Found trending topic: {topic}")
            return topic
            
            # Method 2: Use interest over time with rotating categories
            try:
                all_categories = [
                    'technology', 'health', 'business', 'entertainment', 'sports',
                    'science', 'education', 'travel', 'food', 'fashion',
                    'finance', 'politics', 'environment', 'lifestyle', 'culture'
                ]
                # Select 5 random categories each time for variety
                selected_categories = random.sample(all_categories, 5)
                
                pytrends.build_payload(selected_categories, timeframe='now 1-d')
                interest_data = pytrends.interest_over_time()
                
                if not interest_data.empty:
                    # Get category with highest interest
                    highest_category = interest_data.mean().idxmax()
                    topic = highest_category.capitalize() + " Trends 2025"
                    logging.info(f"Found trending category: {topic}")
                    return topic
            except Exception as e:
                logging.info(f"Interest over time method failed: {str(e)}")
            
            # Method 3: Use suggestions API
            try:
                suggestions = pytrends.suggestions(keyword='trending')
                if suggestions and len(suggestions) > 0:
                    # Get a random suggestion from the list
                    suggestion = random.choice(suggestions[:5])  # Top 5 suggestions
                    if 'title' in suggestion:
                        topic = suggestion['title']
                        logging.info(f"Found suggested topic: {topic}")
                        return topic
                    else:
                        logging.info(f"Suggestions method failed: No title found in suggestion")
                else:
                    logging.info(f"Suggestions method failed: No suggestions found")
            except Exception as e:
                logging.info(f"Suggestions method failed: {str(e)}")
                
        except Exception as e:
            logging.info(f"All Google Trends methods failed: {str(e)}")
        
        # If all Google Trends methods fail, fall back to default topics
        topic = random.choice(default_topics)
        logging.info(f"Using default topic: {topic}")
        return topic
        
    def generate_image(self, prompt, max_retries=3):
        """Get a relevant image for the blog post using Pixabay API with fallbacks."""
        # Create images directory if it doesn't exist
        os.makedirs("images", exist_ok=True)
        
        # Clean up the search term
        search_term = ' '.join([word for word in prompt.split() if len(word) > 2])[:100]
        safe_filename = prompt.replace(' ', '_')[:30] + f"_{int(time.time())}.jpg"
        img_path = f"images/{safe_filename}"
        
        # Try multiple image sources in order of preference
        image_sources = [
            self._get_pixabay_image,
            self._get_pexels_image,
            self._get_placeholder_image
        ]
        
        for source_func in image_sources:
            try:
                result = source_func(search_term, img_path)
                if result:
                    return img_path
            except Exception as e:
                logging.warning(f"Error with image source {source_func.__name__}: {str(e)}")
        
        logging.warning("Could not get an image from any source, continuing without an image")
        return None
    
    def _get_pixabay_image(self, search_term, img_path):
        """Get an image from Pixabay API."""
        if not PIXABAY_API_KEY:
            return False
            
        pixabay_url = "https://pixabay.com/api/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": search_term,
            "image_type": "photo",
            "orientation": "horizontal",  # Ensure landscape orientation
            "safesearch": "true",
            "min_width": 1200,  # Minimum width for landscape
            "min_height": 630,  # Good height for social sharing
            "per_page": 3
        }
        
        response = requests.get(pixabay_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["totalHits"] > 0:
            # Get the first image URL
            img_url = data["hits"][0]["largeImageURL"]
            # Download the image
            img_response = requests.get(img_url)
            img_response.raise_for_status()
            
            with open(img_path, 'wb') as f:
                f.write(img_response.content)
                
            logging.info(f"🖼️ Pixabay image saved to {img_path}")
            return True
        return False
    
    def _get_pexels_image(self, search_term, img_path):
        """Get a free stock image from Pexels."""
        try:
            # Use Pexels' curated photos as they don't require an API key
            pexels_url = f"https://api.pexels.com/v1/search?query={search_term}&per_page=1&orientation=landscape"
            headers = {"Authorization": ""} # No API key needed for this demo
            
            response = requests.get(pexels_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("photos") and len(data["photos"]) > 0:
                    img_url = data["photos"][0]["src"]["large"]
                    img_response = requests.get(img_url)
                    img_response.raise_for_status()
                    
                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    logging.info(f"🖼️ Pexels image saved to {img_path}")
                    return True
        except Exception:
            pass
        return False
    
    def _get_placeholder_image(self, search_term, img_path):
        """Get a placeholder image as last resort."""
        try:
            # Use placeholder.com for a colored placeholder with text in landscape orientation (16:9 ratio)
            color = "%23" + "%06x" % random.randint(0, 0xFFFFFF)
            placeholder_url = f"https://via.placeholder.com/1200x675/{color}/FFFFFF?text={search_term}"
            
            response = requests.get(placeholder_url)
            response.raise_for_status()
            
            with open(img_path, 'wb') as f:
                f.write(response.content)
            
            logging.info(f"🖼️ Placeholder image saved to {img_path}")
            return True
        except Exception:
            return False
            
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
        
        # Generate an image for the blog post
        image_path = self.generate_image(seo_title)
        
        # Add the image to the content if generation was successful
        if image_path:
            try:
                # Read the image file and encode it as base64
                with open(image_path, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                # Add the image at the beginning of the post with CSS to ensure landscape display
                img_html = f'<div class="featured-image" style="max-width:100%;overflow:hidden;"><img src="data:image/jpeg;base64,{img_data}" alt="{seo_title}" style="width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;" /></div>'
                content = img_html + content
                logging.info(f"🖼️ Added featured image to the blog post")
            except Exception as e:
                logging.warning(f"Error adding image to post: {str(e)}")
                # Continue without the image
        
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
            
            # Post to Blogger (label classification and image generation are done inside post_to_blogger)
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
