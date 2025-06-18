"""
Service for generating blog post content and headlines.
"""
import logging
import requests
import time
import re
import random
from datetime import datetime
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
        
        # Content diversity templates for more human-like variation
        self.writing_styles = [
            "conversational and friendly",
            "professional yet approachable",
            "informative and analytical",
            "storytelling with examples",
            "practical and actionable"
        ]
        
        self.content_structures = [
            "problem-solution format",
            "step-by-step guide approach",
            "comparison and analysis style",
            "narrative with case studies",
            "FAQ and tips format"
        ]
        
        # Quality filters to avoid spam-like content
        self.spam_indicators = [
            r'\b(click here|buy now|limited time|act now|urgent|guaranteed)\b',
            r'\b(100% free|amazing deal|incredible offer|don\'t miss)\b',
            r'[!]{3,}',  # Multiple exclamation marks
            # r'\b[A-Z]{15,}\b',  # Very long sequences of capital letters (15+ chars) - DISABLED FOR DEBUG
            r'\$\d+.*\$\d+',  # Price ranges that look spammy
        ]
    
    def generate_blog_post(self, topic, headline=None, max_retries=3):
        """
        Generate a blog post about the given topic with enhanced quality and diversity.
        Returns the generated content as a string.
        """
        # Add randomization for more human-like content
        writing_style = random.choice(self.writing_styles)
        content_structure = random.choice(self.content_structures)
        current_date = datetime.now().strftime("%B %Y")
        
        system_message = (
            f"You are an experienced human blogger writing in {current_date}. "
            f"Write in a {writing_style} tone using a {content_structure}. "
            f"Create original, well-researched content that provides genuine value to readers. "
            f"Avoid promotional language, excessive enthusiasm, or spam-like phrases. "
            f"Write as if you're sharing knowledge with a friend who asked for advice."
        )
        
        # Enhanced prompt for better content quality
        headline_instruction = ""
        if headline:
            headline_instruction = f"Use this headline as the title: '{headline}'\n"
            
        prompt = (
            f"Write a comprehensive blog post about: {topic}\n\n"
            f"{headline_instruction}"
            f"Content Requirements:\n"
            f"1. Write 1200-1500 words with natural, flowing paragraphs\n"
            f"2. Include personal insights, examples, or anecdotes when relevant\n"
            f"3. Use varied sentence structures and paragraph lengths\n"
            f"4. Include practical, actionable advice readers can implement\n"
            f"5. Reference current trends or recent developments (it's {current_date})\n"
            f"6. Use subheadings that feel natural, not keyword-stuffed\n"
            f"7. Include 2-3 lists or bullet points for readability\n"
            f"8. Write a compelling introduction that hooks readers naturally\n"
            f"9. End with a thoughtful conclusion and genuine call-to-action\n"
            f"10. Include 3-4 relevant questions in an FAQ section\n"
            f"11. Suggest 2-3 related topics readers might find interesting\n\n"
            f"SEO Elements (integrate naturally):\n"
            f"- Meta description (150-160 chars): <meta-description>description</meta-description>\n"
            f"- Keywords (6-8 relevant terms): <keywords>term1, term2, etc.</keywords>\n"
            f"- SEO title: <seo-title>{headline if headline else 'SEO-optimized title'}</seo-title>\n"
            f"- Use semantic HTML tags (h2, h3, p, ul, ol)\n"
            f"- Add <ad-break></ad-break> after every 3-4 paragraphs for ad placement\n\n"
            f"Content Quality Guidelines:\n"
            f"- Avoid promotional language or excessive enthusiasm\n"
            f"- Don't use phrases like 'click here', 'buy now', 'limited time'\n"
            f"- Keep exclamation marks to a minimum (max 2-3 in entire post)\n"
            f"- Write in active voice when possible\n"
            f"- Include specific details and examples\n"
            f"- Maintain consistent tone throughout\n"
            f"- Return only clean HTML content without code blocks or formatting markers"
        )

        for attempt in range(max_retries):
            try:
                payload = {
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 2500,
                    "temperature": 0.7 + (random.random() * 0.3)  # Add randomness for content diversity
                }
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
                    content = response_data["choices"][0]["message"]["content"].strip()
                    
                    # Enhanced content cleanup and quality filtering
                    content = self._clean_and_filter_content(content)
                    
                    # Quality check
                    if self._passes_quality_check(content):
                        logging.info(f"Successfully generated high-quality content of length: {len(content)}")
                        return content
                    else:
                        logging.warning(f"Content failed quality check (attempt {attempt + 1}), regenerating...")
                        continue
                else:
                    logging.warning(f"Invalid response format from API (attempt {attempt + 1})")
            except Exception as e:
                logging.warning(f"Error generating blog post (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
        
        raise Exception("Failed to generate high-quality blog post after multiple attempts")
    
    def _clean_and_filter_content(self, content):
        """Clean and filter content to remove spam-like elements."""
        # Remove standalone "html" words that might appear
        content = re.sub(r'\b\.?html\b', '', content, flags=re.IGNORECASE)
        
        # Remove any stray backticks or code block markers
        content = re.sub(r'```html?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'```', '', content)
        
        # Clean up excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Remove excessive exclamation marks (keep max 2 consecutive)
        content = re.sub(r'!{3,}', '!!', content)
        
        # Convert excessive caps to normal case (except for acronyms)
        def fix_caps(match):
            text = match.group(0)
            if len(text) > 5 and not any(word in text.upper() for word in ['HTML', 'SEO', 'API', 'URL', 'FAQ']):
                return text.capitalize()
            return text
        
        content = re.sub(r'[A-Z]{6,}', fix_caps, content)
        
        return content.strip()
    
    def _passes_quality_check(self, content):
        """Check if content passes quality filters to avoid spam detection."""
        # Check for spam indicators
        for pattern in self.spam_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                logging.warning(f"Content contains potential spam pattern: {pattern}")
                return False
        
        # Check content length
        if len(content) < 800:
            logging.warning("Content too short for quality standards")
            return False
        
        # Check for excessive repetition
        sentences = content.split('.')
        if len(sentences) > 10:
            # Simple check for repeated sentences
            unique_sentences = set(s.strip().lower() for s in sentences if len(s.strip()) > 20)
            if len(unique_sentences) < len(sentences) * 0.8:
                logging.warning("Content has too much repetition")
                return False
        
        return True

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
