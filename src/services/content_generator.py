"""
Service for generating blog post content and headlines.
"""
import logging
import requests
import time
from src.utils.config import OPENROUTER_API_KEY

class ContentGeneratorService:
    """Service for generating blog post content and headlines."""
    
    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/blog-bot",
        }
    
    def generate_blog_post(self, topic, headline=None, max_retries=3):
        """
        Generate a blog post about the given topic.
        Returns the generated content as a string.
        """
        system_message = (
            "You are a professional blog writer and SEO expert. Write engaging, well-researched, "
            "and informative content that is optimized for search engines. Use a conversational "
            "yet professional tone. Format the content with proper HTML tags for better presentation "
            "and SEO optimization."
        )
        
        # If headline is provided, use it in the prompt
        headline_instruction = ""
        if headline:
            headline_instruction = f"Use this headline as the title: '{headline}'\n"
            
        prompt = (
            f"Write an engaging and SEO-optimized blog post about: {topic}\n\n"
            f"{headline_instruction}"
            f"Requirements:\n"
            f"1. Around 800-1000 words for better SEO performance\n"
            f"2. Include a compelling meta description (150-160 characters) at the very top as: <meta-description>Your description here</meta-description>\n"
            f"3. Include 5 relevant keywords/phrases for the topic as: <keywords>keyword1, keyword2, keyword3, keyword4, keyword5</keywords>\n"
            f"4. Include an SEO-optimized title (different from the main topic) as: <seo-title>{headline if headline else 'Your SEO Title Here'}</seo-title>\n"
            f"5. Include a brief introduction that hooks the reader\n"
            f"6. Use proper heading hierarchy (h2, h3) with keywords in headings\n"
            f"7. Include at least one bulleted or numbered list\n"
            f"8. Use 2-3 subheadings (h2) with the main keyword included naturally\n"
            f"9. Write short paragraphs (3-4 sentences max) for better readability\n"
            f"10. Include a conclusion with a call to action\n"
            f"11. Format with semantic HTML tags for better SEO and readability\n"
        )

        for attempt in range(max_retries):
            try:
                payload = {
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 2500
                }
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                )
                
                logging.info(f"API Response Status: {response.status_code}")
                response.raise_for_status()
                response_data = response.json()
                
                if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
                    content = response_data["choices"][0]["message"]["content"]
                    logging.info(f"Successfully generated content of length: {len(content)}")
                    return content
                else:
                    logging.warning(f"Invalid response format from API (attempt {attempt + 1})")
            except Exception as e:
                logging.warning(f"Error generating blog post (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
        
        raise Exception("Failed to generate blog post after multiple attempts")
    
    def generate_headline(self, topic, max_retries=3):
        """
        Generate an engaging, clickable headline for the blog post.
        Returns the generated headline as a string.
        """
        system_message = (
            "You are a professional headline writer for viral content. Create engaging, "
            "clickable headlines that grab attention while maintaining accuracy. "
            "Your headlines should be SEO-friendly and compelling."
        )
        
        prompt = (
            f"Create an engaging, clickable headline about: {topic}\n\n"
            f"Requirements:\n"
            f"1. Make it compelling and attention-grabbing\n"
            f"2. Keep it under 60 characters for SEO\n"
            f"3. Include the main keyword: {topic}\n"
            f"4. Use power words that evoke emotion\n"
            f"5. Create curiosity or promise value\n"
            f"6. Return ONLY the headline text with no quotes or formatting"
        )

        for attempt in range(max_retries):
            try:
                payload = {
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 100
                }
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
                    headline = response_data["choices"][0]["message"]["content"].strip()
                    logging.info(f"✨ Generated headline: {headline}")
                    return headline
                else:
                    logging.warning(f"Invalid response format from API (attempt {attempt + 1})")
            except Exception as e:
                logging.warning(f"Error generating headline (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    logging.error(f"Failed to generate headline after {max_retries} attempts")
                    return f"Latest Insights on {topic}"  # Fallback headline
                time.sleep(2)
        
        return f"Latest Insights on {topic}"  # Fallback headline if all attempts fail
