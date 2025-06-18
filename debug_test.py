#!/usr/bin/env python3
"""
Debug test for Email Bot imports and basic functionality
"""

import os
import sys

print("🔍 Debug Test for Email Bot")
print("=" * 40)

# Test 1: Check Python path
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Test 2: Check if src directory exists
src_path = os.path.join(os.getcwd(), 'src')
print(f"Src directory exists: {os.path.exists(src_path)}")

# Test 3: Add src to path and test imports
sys.path.append(src_path)
print("Added src to Python path")

try:
    print("\n📦 Testing imports...")
    
    # Test basic imports
    from services.gmail_service import GmailService
    print("✅ GmailService import successful")
    
    from services.content_generator import ContentGeneratorService
    print("✅ ContentGeneratorService import successful")
    
    from services.posting_scheduler import PostingScheduler
    print("✅ PostingScheduler import successful")
    
    from services.content_diversity import ContentDiversityService
    print("✅ ContentDiversityService import successful")
    
    from email_bot import EmailBot
    print("✅ EmailBot import successful")
    
    print("\n🔧 Testing basic functionality...")
    
    # Test environment variables
    gmail_email = os.getenv('GMAIL_EMAIL')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    
    print(f"GMAIL_EMAIL set: {'✅' if gmail_email else '❌'}")
    print(f"GMAIL_APP_PASSWORD set: {'✅' if gmail_password else '❌'}")
    print(f"OPENROUTER_API_KEY set: {'✅' if openrouter_key else '❌'}")
    
    if gmail_email and gmail_password:
        print(f"Gmail configured for: {gmail_email}")
    else:
        print("⚠️  Gmail credentials not configured")
    
    print("\n🎉 All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()
