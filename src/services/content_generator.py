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
            f"1. Around 1200-1500 words for better SEO performance and ad placement\n"
            f"2. Include a compelling meta description (150-160 characters) at the very top as: <meta-description>Your description here</meta-description>\n"
            f"3. Include 8-10 relevant long-tail keywords/phrases for the topic as: <keywords>keyword1, keyword2, keyword3, keyword4, keyword5, keyword6, keyword7, keyword8</keywords>\n"
            f"4. Include an SEO-optimized title (different from the main topic) as: <seo-title>{headline if headline else 'Your SEO Title Here'}</seo-title>\n"
            f"5. Include a compelling introduction that hooks the reader and includes the main keyword\n"
            f"6. Use proper heading hierarchy (h2, h3, h4) with keywords in headings naturally\n"
            f"7. Include at least 2-3 bulleted or numbered lists for better readability\n"
            f"8. Use 4-6 subheadings (h2) with related keywords included naturally\n"
            f"9. Write short paragraphs (2-3 sentences max) for better readability and ad placement\n"
            f"10. Include a comprehensive conclusion with multiple call-to-actions\n"
            f"11. Add FAQ section with 3-5 common questions about the topic\n"
            f"12. Include 'Related Topics' section suggesting 3-4 related subjects\n"
            f"13. Format with semantic HTML tags for better SEO and readability\n"
            f"14. Add strategic keyword density (1-2% of total content)\n"
            f"15. Include actionable tips and practical advice\n"
            f"16. Add social proof or statistics when relevant\n"
            f"17. Do NOT include any code blocks, backticks, or the word 'html' in the content\n"
            f"18. Return only the clean blog post content without any extra formatting markers\n"
            f"19. Include natural places for ad insertion with <ad-break></ad-break> tags after every 3-4 paragraphs\n"
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
                    
                    # Clean up the content - remove unwanted HTML artifacts
                    import re
                    
                    # Remove standalone "html" words that might appear
                    content = re.sub(r'\b\.?html\b', '', content, flags=re.IGNORECASE)
                    
                    # Remove any stray backticks or code block markers
                    content = re.sub(r'```html?', '', content, flags=re.IGNORECASE)
                    content = re.sub(r'```', '', content)
                    
                    # Clean up excessive whitespace
                    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
                    content = content.strip()
                    
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
                    
                    # Clean up the headline - remove quotation marks and other unwanted formatting
                    headline = headline.strip('"').strip("'").strip()
                    
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
