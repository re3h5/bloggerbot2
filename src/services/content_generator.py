"""Service for generating blog content using AI."""
import time
import requests
from ..utils.logger import setup_logging
from ..utils.config import OPENROUTER_API_KEY

logger = setup_logging()

class ContentGenerator:
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

    @staticmethod
    def generate_blog_post(topic, max_retries=3):
        """Generate a blog post using OpenRouter AI."""
        system_message = (
            "You are a professional blog writer. Write engaging, well-researched, "
            "and informative content. Use a conversational yet professional tone. "
            "Format the content with proper HTML tags for better presentation."
        )
        
        prompt = (
            f"Write an engaging and informative blog post about: {topic}\n\n"
            f"Requirements:\n"
            f"1. Around 500 words\n"
            f"2. Include a brief introduction that hooks the reader\n"
            f"3. Provide relevant details, examples, and analysis\n"
            f"4. End with a strong conclusion\n"
            f"5. Use proper HTML formatting (<h2> for headings, <p> for paragraphs)\n"
            f"6. Include SEO-friendly headings\n"
            f"7. Write in a clear, engaging style"
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
                response = requests.post(
                    ContentGenerator.OPENROUTER_API_URL,
                    headers=headers,
                    json=data
                )
                
                logger.info(f"API Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"API Error Response: {response.text}")
                    response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                logger.info(f"Successfully generated content of length: {len(content)}")
                return content

            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Error generating blog post (attempt {attempt + 1}): {str(e)}")
                time.sleep(5)
