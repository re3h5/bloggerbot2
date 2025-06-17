"""
Service for generating and fetching images for blog posts.
"""
import os
import logging
import random
import requests
import time
import base64
from urllib.parse import quote
from src.utils.config import PIXABAY_API_KEY, BASE_DIR

class ImageService:
    """Service for generating and fetching images for blog posts."""
    
    def __init__(self):
        # Create images directory if it doesn't exist
        self.images_dir = os.path.join(BASE_DIR, 'images')
        os.makedirs(self.images_dir, exist_ok=True)
    
    def generate_image(self, topic, max_retries=3):
        """
        Generate or fetch an image for the given topic.
        Returns the path to the saved image.
        """
        # Try multiple image sources with fallbacks
        image_path = None
        
        # Method 1: Try Pixabay API if API key is available
        if PIXABAY_API_KEY:
            try:
                image_path = self._get_pixabay_image(topic)
                if image_path:
                    logging.info(f"Successfully fetched image from Pixabay for topic: {topic}")
                    return image_path
            except Exception as e:
                logging.warning(f"Error fetching image from Pixabay: {str(e)}")
        
        # Method 2: Try Pexels API (no API key required)
        try:
            image_path = self._get_pexels_image(topic)
            if image_path:
                logging.info(f"Successfully fetched image from Pexels for topic: {topic}")
                return image_path
        except Exception as e:
            logging.warning(f"Error fetching image from Pexels: {str(e)}")
        
        # Method 3: Use placeholder image as final fallback
        try:
            image_path = self._get_placeholder_image(topic)
            if image_path:
                logging.info(f"Using placeholder image for topic: {topic}")
                return image_path
        except Exception as e:
            logging.warning(f"Error creating placeholder image: {str(e)}")
        
        logging.error("All image generation methods failed")
        return None
    
    def _get_pixabay_image(self, topic):
        """Fetch an image from Pixabay API."""
        search_term = quote(topic)
        url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={search_term}&image_type=photo&orientation=horizontal&min_width=1200"
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('totalHits', 0) > 0:
            # Get a random image from the results
            image = random.choice(data['hits'])
            image_url = image['largeImageURL']
            
            # Download and save the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Create a filename based on the topic and timestamp
            filename = f"{topic.replace(' ', '_')}_{int(time.time())}.jpg"
            image_path = os.path.join(self.images_dir, filename)
            
            with open(image_path, 'wb') as f:
                f.write(image_response.content)
            
            return image_path
        
        return None
    
    def _get_pexels_image(self, topic):
        """Fetch an image from Pexels API."""
        search_term = quote(topic)
        url = f"https://api.pexels.com/v1/search?query={search_term}&per_page=15&orientation=landscape"
        
        # Pexels requires a header but no API key for basic access
        headers = {
            "User-Agent": "BloggerBot/1.0"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get('photos', []):
            # Get a random image from the results
            photo = random.choice(data['photos'])
            image_url = photo['src']['large']
            
            # Download and save the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Create a filename based on the topic and timestamp
            filename = f"{topic.replace(' ', '_')}_{int(time.time())}.jpg"
            image_path = os.path.join(self.images_dir, filename)
            
            with open(image_path, 'wb') as f:
                f.write(image_response.content)
            
            return image_path
        
        return None
    
    def _get_placeholder_image(self, topic):
        """Get a placeholder image as final fallback."""
        # Use placeholder.com to generate a placeholder image
        # Format: 1200x675 for 16:9 aspect ratio
        width = 1200
        height = 675
        bg_color = "cccccc"
        text_color = "333333"
        text = quote(f"Blog Image: {topic}")
        
        url = f"https://via.placeholder.com/{width}x{height}/{bg_color}/{text_color}?text={text}"
        
        response = requests.get(url)
        response.raise_for_status()
        
        # Create a filename based on the topic and timestamp
        filename = f"{topic.replace(' ', '_')}_{int(time.time())}.jpg"
        image_path = os.path.join(self.images_dir, filename)
        
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        return image_path
