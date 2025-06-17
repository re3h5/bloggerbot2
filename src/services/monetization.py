"""
Service for adding monetization features to blog posts.
"""
import random
import re

class MonetizationService:
    """Service for adding monetization elements to blog posts."""
    
    def __init__(self):
        # Affiliate product suggestions by category
        self.affiliate_products = {
            'technology': [
                'Latest smartphones and gadgets',
                'Productivity software and tools',
                'Computer accessories and peripherals',
                'Smart home devices'
            ],
            'business': [
                'Business books and courses',
                'Project management tools',
                'Marketing software',
                'Professional development resources'
            ],
            'health': [
                'Fitness equipment and supplements',
                'Health monitoring devices',
                'Wellness books and guides',
                'Nutrition products'
            ],
            'lifestyle': [
                'Fashion and beauty products',
                'Home decor and organization',
                'Travel gear and accessories',
                'Hobby and craft supplies'
            ]
        }
        
        # AdSense optimization tags
        self.ad_placements = [
            '<div class="ad-container" style="text-align: center; margin: 20px 0;"><ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-XXXXXXXXX" data-ad-slot="XXXXXXXXX" data-ad-format="auto"></ins></div>',
            '<div class="ad-container" style="text-align: center; margin: 15px 0;"><ins class="adsbygoogle" style="display:inline-block;width:728px;height:90px" data-ad-client="ca-pub-XXXXXXXXX" data-ad-slot="XXXXXXXXX"></ins></div>',
            '<div class="ad-container" style="float: right; margin: 10px 0 10px 15px;"><ins class="adsbygoogle" style="display:inline-block;width:300px;height:250px" data-ad-client="ca-pub-XXXXXXXXX" data-ad-slot="XXXXXXXXX"></ins></div>'
        ]
    
    def add_monetization_elements(self, content, topic):
        """
        Add monetization elements to blog post content.
        """
        # Replace ad-break tags with actual ad placements
        content = self._insert_ads(content)
        
        # Add affiliate product suggestions
        content = self._add_affiliate_suggestions(content, topic)
        
        # Add email signup call-to-action
        content = self._add_email_signup(content)
        
        # Add social sharing buttons
        content = self._add_social_sharing(content)
        
        return content
    
    def _insert_ads(self, content):
        """Replace ad-break tags with actual ad code."""
        ad_breaks = content.count('<ad-break></ad-break>')
        
        for i in range(ad_breaks):
            ad_code = random.choice(self.ad_placements)
            content = content.replace('<ad-break></ad-break>', ad_code, 1)
        
        return content
    
    def _add_affiliate_suggestions(self, content, topic):
        """Add relevant affiliate product suggestions."""
        # Determine category based on topic
        category = self._categorize_topic(topic.lower())
        
        if category in self.affiliate_products:
            products = self.affiliate_products[category]
            selected_products = random.sample(products, min(2, len(products)))
            
            affiliate_section = f"""
<div class="affiliate-section" style="background: #f8f9fa; padding: 20px; margin: 25px 0; border-left: 4px solid #007bff;">
<h3>🛍️ Recommended Products</h3>
<p>Based on this topic, you might find these helpful:</p>
<ul>
"""
            for product in selected_products:
                affiliate_section += f"<li><strong>{product}</strong> - <a href='#' target='_blank'>Check Latest Prices</a></li>\n"
            
            affiliate_section += """</ul>
<p><small><em>Note: We may earn a commission from purchases made through our links at no extra cost to you.</em></small></p>
</div>
"""
            
            # Insert before conclusion
            content = content.replace('</h2>', '</h2>' + affiliate_section, 1)
        
        return content
    
    def _add_email_signup(self, content):
        """Add email newsletter signup."""
        email_signup = """
<div class="email-signup" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; margin: 30px 0; text-align: center; border-radius: 10px;">
<h3 style="color: white; margin-bottom: 15px;">📧 Stay Updated!</h3>
<p style="margin-bottom: 20px;">Get the latest insights and trending topics delivered to your inbox weekly.</p>
<form style="display: inline-block;">
<input type="email" placeholder="Enter your email" style="padding: 12px; border: none; border-radius: 5px; margin-right: 10px; width: 250px;">
<button type="submit" style="padding: 12px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">Subscribe Now</button>
</form>
<p style="font-size: 12px; margin-top: 10px; opacity: 0.8;">No spam, unsubscribe anytime!</p>
</div>
"""
        
        # Insert before the last paragraph
        content = content.replace('</article>', email_signup + '</article>')
        if '</article>' not in content:
            content += email_signup
        
        return content
    
    def _add_social_sharing(self, content):
        """Add social media sharing buttons."""
        social_sharing = """
<div class="social-sharing" style="text-align: center; margin: 25px 0; padding: 20px; background: #f8f9fa;">
<h4>📢 Share This Article</h4>
<div style="margin-top: 15px;">
<a href="#" onclick="window.open('https://twitter.com/intent/tweet?url='+encodeURIComponent(window.location.href)+'&text='+encodeURIComponent(document.title), 'twitter', 'width=550,height=235');return false;" style="display: inline-block; margin: 0 10px; padding: 10px 15px; background: #1da1f2; color: white; text-decoration: none; border-radius: 5px;">Twitter</a>
<a href="#" onclick="window.open('https://www.facebook.com/sharer/sharer.php?u='+encodeURIComponent(window.location.href), 'facebook', 'width=550,height=235');return false;" style="display: inline-block; margin: 0 10px; padding: 10px 15px; background: #3b5998; color: white; text-decoration: none; border-radius: 5px;">Facebook</a>
<a href="#" onclick="window.open('https://www.linkedin.com/sharing/share-offsite/?url='+encodeURIComponent(window.location.href), 'linkedin', 'width=550,height=235');return false;" style="display: inline-block; margin: 0 10px; padding: 10px 15px; background: #0077b5; color: white; text-decoration: none; border-radius: 5px;">LinkedIn</a>
</div>
</div>
"""
        
        # Insert at the end
        content += social_sharing
        
        return content
    
    def _categorize_topic(self, topic):
        """Categorize topic for affiliate product suggestions."""
        if any(word in topic for word in ['tech', 'ai', 'software', 'computer', 'digital', 'app']):
            return 'technology'
        elif any(word in topic for word in ['business', 'marketing', 'finance', 'money', 'startup']):
            return 'business'
        elif any(word in topic for word in ['health', 'fitness', 'wellness', 'nutrition', 'medical']):
            return 'health'
        else:
            return 'lifestyle'
    
    def optimize_for_adsense(self, content):
        """Optimize content structure for better AdSense performance."""
        # Ensure proper paragraph spacing for ads
        content = re.sub(r'</p>\s*<p>', '</p>\n\n<p>', content)
        
        # Add strategic line breaks for better ad placement
        content = re.sub(r'</h2>', '</h2>\n\n', content)
        content = re.sub(r'</h3>', '</h3>\n\n', content)
        
        return content
