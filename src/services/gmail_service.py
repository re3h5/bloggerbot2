"""
Gmail Email Service for sending blog posts via email
Supports both SMTP and Gmail API methods
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import base64
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GmailService:
    """Service for sending emails via Gmail SMTP or Gmail API"""
    
    def __init__(self, use_api: bool = False):
        self.logger = logging.getLogger(__name__)
        self.use_api = use_api
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Gmail API scopes
        self.scopes = ['https://www.googleapis.com/auth/gmail.send']
        
        # Load configuration
        self.config = self._load_config()
        
        if self.use_api:
            self.service = self._setup_gmail_api()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load email configuration from environment variables"""
        return {
            'sender_email': os.getenv('GMAIL_EMAIL'),
            'sender_password': os.getenv('GMAIL_APP_PASSWORD'),  # App-specific password
            'sender_name': os.getenv('GMAIL_SENDER_NAME', 'BloggerBot'),
            'default_recipients': os.getenv('EMAIL_RECIPIENTS', '').split(','),
            'bcc_recipients': os.getenv('EMAIL_BCC', '').split(',') if os.getenv('EMAIL_BCC') else [],
        }
    
    def _setup_gmail_api(self):
        """Set up Gmail API service"""
        creds = None
        token_path = 'config/gmail_token.pickle'
        
        # Load existing token
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'config/gmail_credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('gmail', 'v1', credentials=creds)
    
    def create_email_content(self, title: str, content: str, 
                           email_type: str = "newsletter") -> Dict[str, str]:
        """Create formatted email content from blog post"""
        
        # Email templates
        templates = {
            "newsletter": self._create_newsletter_template(title, content),
            "blog_post": self._create_blog_post_template(title, content),
            "digest": self._create_digest_template(title, content),
            "announcement": self._create_announcement_template(title, content)
        }
        
        return templates.get(email_type, templates["newsletter"])
    
    def _create_newsletter_template(self, title: str, content: str) -> Dict[str, str]:
        """Create newsletter-style email template"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ background: #333; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                h1 {{ margin: 0; font-size: 24px; }}
                h2 {{ color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 5px; }}
                .date {{ font-size: 14px; opacity: 0.8; }}
                .content-body {{ background: white; padding: 20px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📧 BloggerBot Newsletter</h1>
                <div class="date">{datetime.now().strftime('%B %d, %Y')}</div>
            </div>
            <div class="content">
                <div class="content-body">
                    <h2>{title}</h2>
                    {self._format_content_for_email(content)}
                </div>
            </div>
            <div class="footer">
                <p>Sent by BloggerBot | Automated Content Distribution</p>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M UTC')}</p>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
        BloggerBot Newsletter - {datetime.now().strftime('%B %d, %Y')}
        
        {title}
        {'=' * len(title)}
        
        {content}
        
        ---
        Sent by BloggerBot
        Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M UTC')}
        """
        
        return {
            'subject': f"📧 {title} - BloggerBot Newsletter",
            'html': html_content,
            'text': text_content
        }
    
    def _create_blog_post_template(self, title: str, content: str) -> Dict[str, str]:
        """Create blog post style email template"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Georgia, serif; line-height: 1.8; color: #2c3e50; max-width: 700px; margin: 0 auto; padding: 20px; }}
                .post-header {{ text-align: center; margin-bottom: 30px; border-bottom: 3px solid #3498db; padding-bottom: 20px; }}
                .post-title {{ font-size: 28px; color: #2c3e50; margin-bottom: 10px; }}
                .post-meta {{ color: #7f8c8d; font-size: 14px; }}
                .post-content {{ font-size: 16px; }}
                .signature {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1; color: #7f8c8d; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="post-header">
                <h1 class="post-title">{title}</h1>
                <div class="post-meta">Published on {datetime.now().strftime('%B %d, %Y')}</div>
            </div>
            <div class="post-content">
                {self._format_content_for_email(content)}
            </div>
            <div class="signature">
                <p><strong>BloggerBot</strong><br>
                Automated Content Creation & Distribution</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        {title}
        Published on {datetime.now().strftime('%B %d, %Y')}
        
        {content}
        
        ---
        BloggerBot
        Automated Content Creation & Distribution
        """
        
        return {
            'subject': f"📝 New Post: {title}",
            'html': html_content,
            'text': text_content
        }
    
    def _create_digest_template(self, title: str, content: str) -> Dict[str, str]:
        """Create digest style email template"""
        return {
            'subject': f"📰 Daily Digest: {title}",
            'html': f"<h2>Daily Digest</h2><h3>{title}</h3><p>{content}</p>",
            'text': f"Daily Digest\n\n{title}\n\n{content}"
        }
    
    def _create_announcement_template(self, title: str, content: str) -> Dict[str, str]:
        """Create announcement style email template"""
        return {
            'subject': f"📢 Announcement: {title}",
            'html': f"<h2>📢 Important Announcement</h2><h3>{title}</h3><p>{content}</p>",
            'text': f"📢 Important Announcement\n\n{title}\n\n{content}"
        }
    
    def _format_content_for_email(self, content: str) -> str:
        """Format content for email display"""
        # Convert line breaks to HTML
        formatted = content.replace('\n\n', '</p><p>').replace('\n', '<br>')
        
        # Wrap in paragraph tags
        if not formatted.startswith('<p>'):
            formatted = f'<p>{formatted}</p>'
        
        return formatted
    
    def send_email_smtp(self, recipients: List[str], subject: str, 
                       html_content: str, text_content: str,
                       bcc_recipients: Optional[List[str]] = None) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config['sender_name']} <{self.config['sender_email']}>"
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            if bcc_recipients:
                msg['Bcc'] = ', '.join(bcc_recipients)
            
            # Add both plain text and HTML versions
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.config['sender_email'], self.config['sender_password'])
                
                all_recipients = recipients + (bcc_recipients or [])
                server.send_message(msg, to_addrs=all_recipients)
            
            self.logger.info(f"Email sent successfully to {len(all_recipients)} recipients")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email via SMTP: {str(e)}")
            return False
    
    def send_email_api(self, recipients: List[str], subject: str,
                      html_content: str, text_content: str,
                      bcc_recipients: Optional[List[str]] = None) -> bool:
        """Send email using Gmail API"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config['sender_name']} <{self.config['sender_email']}>"
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            if bcc_recipients:
                msg['Bcc'] = ', '.join(bcc_recipients)
            
            # Add content
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            
            # Send via API
            message = {'raw': raw_message}
            result = self.service.users().messages().send(userId='me', body=message).execute()
            
            self.logger.info(f"Email sent successfully via API. Message ID: {result['id']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email via API: {str(e)}")
            return False
    
    def send_blog_post_email(self, title: str, content: str, 
                           recipients: Optional[List[str]] = None,
                           email_type: str = "newsletter") -> bool:
        """Send a blog post as an email"""
        try:
            # Use default recipients if none provided
            if not recipients:
                recipients = [r.strip() for r in self.config['default_recipients'] if r.strip()]
            
            if not recipients:
                self.logger.error("No recipients specified")
                return False
            
            # Create email content
            email_data = self.create_email_content(title, content, email_type)
            
            # Get BCC recipients
            bcc_recipients = [r.strip() for r in self.config['bcc_recipients'] if r.strip()]
            
            # Send email
            if self.use_api:
                success = self.send_email_api(
                    recipients, 
                    email_data['subject'],
                    email_data['html'],
                    email_data['text'],
                    bcc_recipients
                )
            else:
                success = self.send_email_smtp(
                    recipients,
                    email_data['subject'], 
                    email_data['html'],
                    email_data['text'],
                    bcc_recipients
                )
            
            if success:
                self.logger.info(f"Blog post email '{title}' sent successfully")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to send blog post email: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test email service connection"""
        try:
            if self.use_api:
                # Test API connection
                profile = self.service.users().getProfile(userId='me').execute()
                self.logger.info(f"Gmail API connected successfully. Email: {profile['emailAddress']}")
                return True
            else:
                # Test SMTP connection
                context = ssl.create_default_context()
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls(context=context)
                    server.login(self.config['sender_email'], self.config['sender_password'])
                
                self.logger.info("Gmail SMTP connected successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to connect to Gmail: {str(e)}")
            return False
