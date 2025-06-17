"""
Simple email collection service using Google Sheets as database.
This is a basic solution for collecting emails without paid services.
"""
import requests
import json
from datetime import datetime

class SimpleEmailCollector:
    """Collect emails using Google Sheets as a simple database."""
    
    def __init__(self):
        # You'll need to set up a Google Apps Script web app
        # Instructions in the setup guide
        self.google_script_url = "YOUR_GOOGLE_SCRIPT_URL_HERE"
    
    def generate_simple_signup_form(self):
        """Generate a simple email signup form that saves to Google Sheets."""
        return """
<div class="email-signup" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; margin: 30px 0; text-align: center; border-radius: 10px;">
<h3 style="color: white; margin-bottom: 15px;">📧 Join Our Newsletter!</h3>
<p style="margin-bottom: 20px;">Get weekly insights on trending topics and opportunities.</p>

<form id="newsletter-form" onsubmit="submitEmail(event)" style="display: inline-block;">
<input type="email" id="email-input" placeholder="Enter your email" required style="padding: 12px; border: none; border-radius: 5px; margin-right: 10px; width: 250px;">
<button type="submit" style="padding: 12px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">Subscribe</button>
</form>

<p id="signup-message" style="font-size: 12px; margin-top: 10px; opacity: 0.8;">No spam, unsubscribe anytime!</p>
</div>

<script>
function submitEmail(event) {
    event.preventDefault();
    
    const email = document.getElementById('email-input').value;
    const messageEl = document.getElementById('signup-message');
    
    // Show loading message
    messageEl.innerHTML = '⏳ Subscribing...';
    
    // Send to Google Sheets
    fetch('YOUR_GOOGLE_SCRIPT_URL_HERE', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: email,
            timestamp: new Date().toISOString(),
            source: 'blog_post'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            messageEl.innerHTML = '✅ Successfully subscribed! Check your email.';
            document.getElementById('email-input').value = '';
        } else {
            messageEl.innerHTML = '❌ Error subscribing. Please try again.';
        }
    })
    .catch(error => {
        messageEl.innerHTML = '❌ Error subscribing. Please try again.';
    });
}
</script>
"""
    
    def get_google_sheets_setup_instructions(self):
        """Return instructions for setting up Google Sheets email collection."""
        return """
# 📊 Google Sheets Email Collection Setup

## Step 1: Create Google Sheet
1. Go to sheets.google.com
2. Create new sheet named "Newsletter Subscribers"
3. Add headers: Email | Timestamp | Source | Status

## Step 2: Create Google Apps Script
1. In your sheet, go to Extensions → Apps Script
2. Replace code with the email collection script
3. Save and deploy as web app

## Step 3: Get Web App URL
1. Click "Deploy" → "New Deployment"
2. Choose "Web app" type
3. Set execute as "Me"
4. Set access to "Anyone"
5. Copy the web app URL

## Step 4: Update Your Bot
1. Replace 'YOUR_GOOGLE_SCRIPT_URL_HERE' with actual URL
2. Test the signup form

## Viewing Your Subscribers
- Open your Google Sheet
- All email signups appear automatically
- Export to CSV for email marketing tools
- Manually send emails using Gmail
"""

# Google Apps Script Code (paste this in Apps Script editor):
GOOGLE_SCRIPT_CODE = '''
function doPost(e) {
  try {
    // Parse the request data
    const data = JSON.parse(e.postData.contents);
    
    // Get the active spreadsheet
    const sheet = SpreadsheetApp.getActiveSheet();
    
    // Add the email to the sheet
    sheet.appendRow([
      data.email,
      data.timestamp,
      data.source || 'unknown',
      'subscribed'
    ]);
    
    // Return success response
    return ContentService
      .createTextOutput(JSON.stringify({success: true}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    // Return error response
    return ContentService
      .createTextOutput(JSON.stringify({success: false, error: error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  // Handle GET requests (for testing)
  return ContentService
    .createTextOutput("Email collection service is running!")
    .setMimeType(ContentService.MimeType.TEXT);
}
'''
