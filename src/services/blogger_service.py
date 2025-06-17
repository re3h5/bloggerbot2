"""
Service for interacting with the Blogger API.
"""
import os
import logging
import base64
import re
import json
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from src.utils.config import BLOGGER_ID, TOKEN_PATH, CREDENTIALS_PATH
from src.utils.rate_limiter import RateLimiter

class BloggerService:
    """Service for interacting with the Blogger API."""
    
    def __init__(self):
        self.blogger_id = BLOGGER_ID
        self.credentials_path = CREDENTIALS_PATH
        self.token_path = TOKEN_PATH
        # Initialize rate limiter with conservative limits
        # Google API typically allows 10,000 queries per day
        self.rate_limiter = RateLimiter("blogger", max_calls_per_day=9500, max_calls_per_minute=40)
        self.service = self._build_service()
    
    def _build_service(self):
        """Build and return the Blogger API service."""
        try:
            if not os.path.exists(self.token_path):
                logging.error(f"Token file not found at {self.token_path}")
                return None
            
            # Use only the necessary scopes to avoid invalid_scope errors
            # The 'https://www.googleapis.com/auth/blogger' scope includes all permissions
            scopes = ['https://www.googleapis.com/auth/blogger']
            
            credentials = Credentials.from_authorized_user_info(
                info=self._load_token(),
                scopes=scopes
            )
            
            # Check if credentials are valid
            if not credentials.valid and credentials.expired and credentials.refresh_token:
                logging.info("Refreshing expired credentials")
                credentials.refresh(Request())
            
            service = build('blogger', 'v3', credentials=credentials)
            
            # Verify blog access by trying to get blog info
            try:
                blog = service.blogs().get(blogId=self.blogger_id).execute()
                logging.info(f"Successfully authenticated to blog: {blog.get('name', 'Unknown')}")
            except Exception as e:
                logging.error(f"Cannot access blog with ID {self.blogger_id}: {str(e)}")
                logging.error("Please verify your Blogger ID and permissions")
                return None
                
            return service
        except Exception as e:
            logging.error(f"Error building Blogger service: {str(e)}")
            return None
    
    def _load_token(self):
        """Load OAuth token from file."""
        try:
            with open(self.token_path, 'r') as token_file:
                return json.load(token_file)
        except Exception as e:
            logging.error(f"Error loading token: {str(e)}")
            return None
    
    def post_to_blogger(self, title, content, image_result=None, max_retries=3):
        """
        Post content to Blogger.
        Returns the URL of the published post or None if posting failed.
        """
        if not self.service:
            logging.error("Blogger service not initialized")
            return None
        
        # Check rate limits before proceeding
        if not self.rate_limiter.wait_if_needed():
            logging.error("Blogger API daily rate limit reached. Cannot post content.")
            return None
        
        # Extract SEO elements
        meta_description = self._extract_tag(content, "meta-description")
        keywords = self._extract_tag(content, "keywords")
        seo_title = self._extract_tag(content, "seo-title")
        
        # Use SEO title if available, otherwise use the provided title
        post_title = seo_title if seo_title else title
        
        # Clean content by removing SEO tags
        clean_content = self._remove_seo_tags(content)
        
        # Add meta description as hidden HTML if available
        if meta_description:
            clean_content = f'<div style="display:none;">{meta_description}</div>\n{clean_content}'
        
        # Add image to content if provided
        image_path = None
        image_url = None
        
        if image_result:
            if isinstance(image_result, dict):
                image_path = image_result.get('path')
                image_url = image_result.get('url')
            else:
                # For backward compatibility
                image_path = image_result
        
        # Embed image in content if local path is available
        if image_path and os.path.exists(image_path):
            try:
                if image_url:
                    img_html = (
                        f'<div class="featured-image" style="max-width:100%;overflow:hidden;">'
                        f'<img src="{image_url}" alt="{post_title}" '
                        f'style="width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;">'
                        f'</div>\n\n'
                    )
                else:
                    with open(image_path, 'rb') as img_file:
                        img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    
                    img_html = (
                        f'<div class="featured-image" style="max-width:100%;overflow:hidden;">'
                        f'<img src="data:image/jpeg;base64,{img_data}" alt="{post_title}" '
                        f'style="width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;">'
                        f'</div>\n\n'
                    )
                clean_content = img_html + clean_content
            except Exception as e:
                logging.error(f"Error embedding image: {str(e)}")
        
        # Prepare labels from keywords
        labels = []
        if keywords:
            labels = [label.strip() for label in keywords.split(',')]
        
        # Create the post body
        body = {
            'kind': 'blogger#post',
            'blog': {'id': self.blogger_id},
            'title': post_title,
            'content': clean_content
        }
        
        if labels:
            body['labels'] = labels
        
        # Try posting with retries
        for attempt in range(max_retries):
            try:
                # Check rate limits before each attempt
                if attempt > 0 and not self.rate_limiter.wait_if_needed():
                    logging.error("Blogger API rate limit reached during retry. Aborting.")
                    return None
                
                post = self.service.posts().insert(
                    blogId=self.blogger_id,
                    isDraft=False,
                    body=body
                ).execute()
                
                post_url = post.get('url')
                logging.info(f"Successfully posted to Blogger: {post_url}")
                return post_url
            
            except HttpError as e:
                error_message = str(e)
                logging.warning(f"Encountered {e.resp.status} {e.reason}")
                
                # Handle rate limit errors specifically
                if e.resp.status == 429 or "rate limit exceeded" in error_message.lower():
                    wait_time = 60 * (attempt + 1)  # Progressive backoff
                    logging.warning(f"Rate limit hit. Waiting {wait_time} seconds before retry.")
                    time.sleep(wait_time)
                # Handle permission errors
                elif e.resp.status == 403:
                    logging.error("Permission denied. Please check your OAuth scopes and Blogger ID.")
                    logging.error("Make sure you've authorized the correct account with proper permissions.")
                    if attempt == max_retries - 1:
                        return None
                    time.sleep(5)  # Short delay before retry
                else:
                    logging.error(f"HTTP error posting to Blogger (attempt {attempt + 1}): {error_message}")
                    if attempt == max_retries - 1:
                        return None
                    time.sleep(5)  # Short delay before retry
            
            except Exception as e:
                logging.error(f"Error posting to Blogger (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(5)  # Short delay before retry
        
        return None
    
    def _extract_tag(self, content, tag_name):
        """Extract content from a custom tag in the blog post."""
        pattern = f"<{tag_name}>(.*?)</{tag_name}>"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    def _remove_seo_tags(self, content):
        """Remove SEO tags from the content."""
        patterns = [
            r"<meta-description>.*?</meta-description>\s*",
            r"<keywords>.*?</keywords>\s*",
            r"<seo-title>.*?</seo-title>\s*"
        ]
        
        clean_content = content
        for pattern in patterns:
            clean_content = re.sub(pattern, "", clean_content, flags=re.DOTALL)
        
        return clean_content
