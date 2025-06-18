#!/usr/bin/env python3
"""
Simple Email Test - Direct Gmail test without config files
"""

import os
import sys

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def load_env_file():
    """Load environment variables from .env file"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def test_gmail_direct():
    """Test Gmail connection directly"""
    
    print("📧 Simple Gmail Test")
    print("=" * 30)
    
    # Load environment variables
    load_env_file()
    
    gmail_email = os.getenv('GMAIL_EMAIL')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    gmail_sender = os.getenv('GMAIL_SENDER_NAME', 'Email Bot')
    
    if not gmail_email or not gmail_password:
        print("❌ Gmail credentials not found in .env file")
        return False
    
    print(f"📧 Testing Gmail: {gmail_email}")
    print(f"👤 Sender Name: {gmail_sender}")
    
    try:
        # Import and test Gmail service directly
        from services.gmail_service import GmailService
        
        # Create Gmail service without config files
        gmail_service = GmailService(use_api=False)
        
        # Test connection
        print("🔗 Testing Gmail SMTP connection...")
        success = gmail_service.test_connection()
        
        if success:
            print("✅ Gmail connection successful!")
            
            # Send test email
            recipient = "bsty202502.terabhai99@blogger.com"
            print(f"📤 Sending test email to: {recipient}")
            
            html_content = f"""
            <html>
            <body>
                <h2>🎉 Email Bot Test Successful!</h2>
                <p>Your Email Bot is working correctly!</p>
                <p><strong>Test Details:</strong></p>
                <ul>
                    <li><strong>Sender:</strong> {gmail_sender}</li>
                    <li><strong>Gmail Account:</strong> {gmail_email}</li>
                    <li><strong>Connection:</strong> SMTP ✅</li>
                    <li><strong>Time:</strong> {os.popen('echo %date% %time%').read().strip()}</li>
                </ul>
                <p>🚀 Your Email Bot is ready to send automated emails!</p>
                <hr>
                <p><small>This is a test email from your BloggerBot Email system.</small></p>
            </body>
            </html>
            """
            
            text_content = f"""
Email Bot Test Successful!

Your Email Bot is working correctly!

Test Details:
- Sender: {gmail_sender}
- Gmail Account: {gmail_email}
- Connection: SMTP ✅
- Time: {os.popen('echo %date% %time%').read().strip()}

Your Email Bot is ready to send automated emails!
            """
            
            success = gmail_service.send_email(
                to_emails=[recipient],
                subject="🧪 Email Bot Test - Success!",
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                print("✅ Test email sent successfully!")
                print("📬 Check your inbox to confirm receipt.")
                print("\n🎉 Email Bot is working perfectly!")
                return True
            else:
                print("❌ Failed to send test email")
                return False
        else:
            print("❌ Gmail connection failed")
            print("🔧 Please check your Gmail credentials and app password")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gmail_direct()
    if success:
        print("\n✅ Email Bot test completed successfully!")
        print("🚀 You can now use: python email_bot_manager.py run")
    else:
        print("\n❌ Email Bot test failed")
        print("📝 Please check your Gmail configuration in .env file")
    
    sys.exit(0 if success else 1)
