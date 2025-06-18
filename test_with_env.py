#!/usr/bin/env python3
"""
Test Email Bot with environment variables
This script helps test the Email Bot when .env file is not loaded automatically
"""

import os
import sys

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_email_bot():
    """Test Email Bot functionality"""
    
    print("🔧 Email Bot Environment Test")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print(f"✅ .env file found: {env_file}")
        
        # Try to load .env file manually
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print("✅ Environment variables loaded from .env file")
        except Exception as e:
            print(f"⚠️  Could not load .env file: {e}")
    else:
        print("❌ .env file not found")
        print("📝 Please create a .env file with your Gmail credentials")
        return False
    
    # Check environment variables
    gmail_email = os.getenv('GMAIL_EMAIL')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    gmail_sender = os.getenv('GMAIL_SENDER_NAME', 'Email Bot')
    recipients = os.getenv('EMAIL_RECIPIENTS')
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    
    print(f"\n📧 Gmail Configuration:")
    print(f"   Email: {'✅ ' + gmail_email if gmail_email else '❌ Not set'}")
    print(f"   App Password: {'✅ Set' if gmail_password else '❌ Not set'}")
    print(f"   Sender Name: {gmail_sender}")
    print(f"   Recipients: {'✅ ' + recipients if recipients else '❌ Not set'}")
    print(f"   OpenRouter API: {'✅ Set' if openrouter_key else '❌ Not set'}")
    
    if not gmail_email or not gmail_password:
        print("\n❌ Gmail credentials not configured!")
        print("📝 Please add these to your .env file:")
        print("   GMAIL_EMAIL=your-email@gmail.com")
        print("   GMAIL_APP_PASSWORD=your-16-digit-app-password")
        print("   GMAIL_SENDER_NAME=Your Bot Name")
        print("   EMAIL_RECIPIENTS=recipient@example.com")
        print("   OPENROUTER_API_KEY=your-api-key")
        return False
    
    # Test Gmail connection
    print(f"\n🧪 Testing Gmail connection...")
    try:
        from services.gmail_service import GmailService
        
        gmail_service = GmailService(use_api=False)
        success = gmail_service.test_connection()
        
        if success:
            print("✅ Gmail connection successful!")
            
            # Try sending a test email
            test_recipient = recipients.split(',')[0] if recipients else 'test@example.com'
            print(f"📧 Sending test email to: {test_recipient}")
            
            success = gmail_service.send_email(
                to_emails=[test_recipient],
                subject="🧪 Email Bot Test",
                html_content="""
                <h2>🎉 Email Bot Test Successful!</h2>
                <p>Your Email Bot is working correctly!</p>
                <p><strong>Configuration:</strong></p>
                <ul>
                    <li>Gmail SMTP: ✅ Connected</li>
                    <li>Sender: """ + gmail_sender + """</li>
                    <li>Time: """ + str(os.popen('date /t & time /t').read().strip()) + """</li>
                </ul>
                <p>You can now use the Email Bot to send automated emails!</p>
                """,
                text_content="Email Bot Test - Your Email Bot is working correctly!"
            )
            
            if success:
                print("✅ Test email sent successfully!")
                print("📬 Check your inbox to confirm receipt.")
                return True
            else:
                print("❌ Failed to send test email")
                return False
        else:
            print("❌ Gmail connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gmail: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_email_bot()
    sys.exit(0 if success else 1)
