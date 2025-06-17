"""
Service for tracking blog performance and analytics.
"""
import json
import os
from datetime import datetime
import logging

class AnalyticsService:
    """Service for tracking blog post performance and analytics."""
    
    def __init__(self):
        self.analytics_file = "analytics/blog_performance.json"
        self.ensure_analytics_dir()
    
    def ensure_analytics_dir(self):
        """Ensure analytics directory exists."""
        os.makedirs("analytics", exist_ok=True)
        
        # Create analytics file if it doesn't exist
        if not os.path.exists(self.analytics_file):
            initial_data = {
                "posts": [],
                "summary": {
                    "total_posts": 0,
                    "total_words": 0,
                    "avg_words_per_post": 0,
                    "most_popular_topics": [],
                    "posting_frequency": "hourly"
                }
            }
            with open(self.analytics_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
    
    def track_post(self, topic, headline, content, post_url=None):
        """Track a new blog post."""
        try:
            # Load existing data
            with open(self.analytics_file, 'r') as f:
                data = json.load(f)
            
            # Create post record
            post_record = {
                "timestamp": datetime.now().isoformat(),
                "topic": topic,
                "headline": headline,
                "word_count": len(content.split()),
                "char_count": len(content),
                "post_url": post_url,
                "status": "published" if post_url else "failed"
            }
            
            # Add to posts list
            data["posts"].append(post_record)
            
            # Update summary
            data["summary"]["total_posts"] = len(data["posts"])
            data["summary"]["total_words"] = sum(post["word_count"] for post in data["posts"])
            data["summary"]["avg_words_per_post"] = data["summary"]["total_words"] // data["summary"]["total_posts"] if data["summary"]["total_posts"] > 0 else 0
            
            # Track popular topics
            topic_counts = {}
            for post in data["posts"]:
                topic_key = post["topic"].lower()
                topic_counts[topic_key] = topic_counts.get(topic_key, 0) + 1
            
            data["summary"]["most_popular_topics"] = sorted(
                topic_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            # Save updated data
            with open(self.analytics_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logging.info(f"📊 Tracked blog post: {headline}")
            
        except Exception as e:
            logging.error(f"❌ Error tracking post analytics: {str(e)}")
    
    def get_performance_summary(self):
        """Get performance summary for logging."""
        try:
            with open(self.analytics_file, 'r') as f:
                data = json.load(f)
            
            summary = data["summary"]
            recent_posts = data["posts"][-5:] if data["posts"] else []
            
            return {
                "total_posts": summary["total_posts"],
                "avg_words": summary["avg_words_per_post"],
                "recent_topics": [post["topic"] for post in recent_posts],
                "success_rate": len([p for p in data["posts"] if p["status"] == "published"]) / len(data["posts"]) * 100 if data["posts"] else 0
            }
            
        except Exception as e:
            logging.error(f"❌ Error getting performance summary: {str(e)}")
            return None
    
    def add_seo_tracking(self, content):
        """Add Google Analytics and Search Console tracking to content."""
        # Add Google Analytics tracking code
        ga_code = """
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>

<!-- Google Search Console Verification -->
<meta name="google-site-verification" content="YOUR_VERIFICATION_CODE" />
"""
        
        # Add structured data for better SEO
        structured_data = """
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "BLOG_HEADLINE",
  "datePublished": "PUBLISH_DATE",
  "dateModified": "PUBLISH_DATE",
  "author": {
    "@type": "Person",
    "name": "AI Blogger Bot"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Your Blog Name"
  },
  "description": "BLOG_DESCRIPTION"
}
</script>
"""
        
        # Insert tracking codes at the beginning of content
        enhanced_content = ga_code + structured_data + content
        
        return enhanced_content
    
    def generate_performance_report(self):
        """Generate a detailed performance report."""
        try:
            summary = self.get_performance_summary()
            if not summary:
                return "No performance data available."
            
            report = f"""
📊 **Blog Performance Report**
================================

📈 **Overall Stats:**
- Total Posts: {summary['total_posts']}
- Average Words per Post: {summary['avg_words']}
- Success Rate: {summary['success_rate']:.1f}%

🔥 **Recent Topics:**
{chr(10).join(f"- {topic}" for topic in summary['recent_topics'])}

💡 **Recommendations:**
- Continue posting hourly for consistent growth
- Focus on topics with higher engagement
- Monitor AdSense performance weekly
- Consider A/B testing headlines

📅 **Next Steps:**
- Set up Google Analytics for detailed tracking
- Monitor search rankings for key topics
- Optimize underperforming posts
- Expand successful topic categories
"""
            
            return report
            
        except Exception as e:
            logging.error(f"❌ Error generating performance report: {str(e)}")
            return "Error generating performance report."
