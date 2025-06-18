# 📧 Email Bot Setup Guide

Transform your BloggerBot into an **Email Bot** that sends blog posts via Gmail instead of posting directly to Blogger. Perfect for newsletters, email marketing, and content distribution!

## 🚀 Quick Start

### 1. Gmail Setup

#### Option A: Gmail SMTP (Recommended for beginners)
1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account Settings → Security
   - Under "2-Step Verification", click "App passwords"
   - Generate password for "Mail"
   - Save this password securely

#### Option B: Gmail API (Advanced users)
1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing one
   - Enable Gmail API
   
2. **Create OAuth Credentials**:
   - Go to APIs & Services → Credentials
   - Create OAuth 2.0 Client ID (Desktop application)
   - Download JSON file as `config/gmail_credentials.json`

### 2. Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Gmail SMTP Configuration
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-digit-app-password
GMAIL_SENDER_NAME=Your Name or Bot Name

# Email Recipients
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
EMAIL_BCC=bcc1@example.com,bcc2@example.com

# Content Generation
OPENROUTER_API_KEY=your-openrouter-api-key

# Optional: Pixabay for images
PIXABAY_API_KEY=your-pixabay-api-key
```

### 3. GitHub Secrets (for automation)

Add these secrets to your GitHub repository:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `GMAIL_EMAIL` | Your Gmail address | `yourbot@gmail.com` |
| `GMAIL_APP_PASSWORD` | Gmail app-specific password | `abcd efgh ijkl mnop` |
| `GMAIL_SENDER_NAME` | Display name for emails | `BloggerBot Newsletter` |
| `EMAIL_RECIPIENTS` | Default recipients | `user1@example.com,user2@example.com` |
| `EMAIL_BCC` | BCC recipients (optional) | `archive@example.com` |
| `OPENROUTER_API_KEY` | Content generation API | `sk-or-...` |
| `GMAIL_API_CREDENTIALS` | Gmail API JSON (if using API) | `{"type":"service_account",...}` |

## 🎯 Usage

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Test email setup
python email_bot_manager.py test --recipients your-email@example.com

# Check status
python email_bot_manager.py status

# Send single email (respects schedule)
python email_bot_manager.py run

# Force send email (ignores schedule)
python email_bot_manager.py forcerun

# Send multiple emails
python email_bot_manager.py run --max-emails 3

# Use specific email type
python email_bot_manager.py run --type newsletter

# Set posting pattern
python email_bot_manager.py pattern moderate
```

### GitHub Actions Automation

The Email Bot runs automatically via GitHub Actions:

- **Scheduled**: Every 2 hours, checks if it should send emails
- **Manual**: Trigger manually with custom options

#### Manual Trigger Options:
- **Force Send**: Override posting schedule
- **Posting Pattern**: Conservative, Moderate, or Active
- **Max Emails**: Number of emails to send
- **Email Type**: Newsletter, Blog Post, Digest, or Announcement
- **Gmail Method**: SMTP or API

## 📧 Email Templates

### 1. Newsletter (Default)
- **Style**: Professional newsletter format
- **Subject**: `📧 [Title] - BloggerBot Newsletter`
- **Content**: Styled HTML with header, content, and footer

### 2. Blog Post
- **Style**: Clean blog post format
- **Subject**: `📝 New Post: [Title]`
- **Content**: Article-style layout

### 3. Digest
- **Style**: Summary format
- **Subject**: `📰 Daily Digest: [Title]`
- **Content**: Condensed information

### 4. Announcement
- **Style**: Important announcement
- **Subject**: `📢 Announcement: [Title]`
- **Content**: Attention-grabbing format

## ⚙️ Configuration

### Email Configuration (`config/email_config.json`)

```json
{
  "default_recipients": ["user@example.com"],
  "email_types": {
    "newsletter": {"weight": 40, "subject_prefix": "📧"},
    "blog_post": {"weight": 35, "subject_prefix": "📝"},
    "digest": {"weight": 15, "subject_prefix": "📰"},
    "announcement": {"weight": 10, "subject_prefix": "📢"}
  },
  "sending_preferences": {
    "preferred_hours": [9, 10, 11, 14, 15, 16, 17, 18],
    "avoid_weekends": false,
    "max_daily_emails": 4,
    "min_delay_between_emails": 3600
  }
}
```

### Posting Patterns

| Pattern | Delay Between Emails | Max Daily | Description |
|---------|---------------------|-----------|-------------|
| **Conservative** | 6-12 hours | 3 emails | Cautious, natural |
| **Moderate** | 4-8 hours | 4 emails | Balanced approach |
| **Active** | 2-6 hours | 4 emails | More frequent |

## 🔧 Advanced Features

### Human-Like Behavior
- **Natural delays** between operations (30s-5min)
- **Posting windows** during business hours
- **Content diversity** tracking to avoid repetition
- **Spam detection** and prevention

### Content Diversity
- **Topic tracking** to ensure variety
- **Keyword monitoring** to prevent overuse
- **Category distribution** for balanced content
- **Similarity detection** to avoid duplicates

### Monitoring & Analytics
- **Posting history** tracking
- **Success/failure rates**
- **Content diversity scores**
- **Email sending statistics**

## 🚨 Troubleshooting

### Common Issues

#### 1. Gmail Authentication Failed
```
❌ Failed to connect to Gmail
```
**Solutions**:
- Verify Gmail email and app password
- Ensure 2FA is enabled
- Check app password is 16 digits without spaces
- Try generating new app password

#### 2. No Recipients Configured
```
❌ No recipients specified
```
**Solutions**:
- Set `EMAIL_RECIPIENTS` environment variable
- Add recipients in `config/email_config.json`
- Use `--recipients` flag when running manually

#### 3. Content Generation Failed
```
❌ Failed to generate content
```
**Solutions**:
- Verify `OPENROUTER_API_KEY` is correct
- Check internet connection
- Review API usage limits

#### 4. Gmail API Issues
```
❌ Gmail API connection failed
```
**Solutions**:
- Ensure `config/gmail_credentials.json` exists
- Run OAuth flow locally first
- Check API is enabled in Google Cloud Console

### Debug Commands

```bash
# Test Gmail connection
python email_bot_manager.py test

# Check detailed status
python email_bot_manager.py status --api

# View logs
tail -f email_bot.log

# Reset all data
python email_bot_manager.py reset --confirm
```

## 📊 Monitoring

### GitHub Actions Logs
- Check Actions tab for workflow runs
- Download artifacts for detailed logs
- Monitor success/failure rates

### Local Monitoring
```bash
# View recent email history
python email_bot_manager.py history

# Check content diversity
python email_bot_manager.py diversity

# Monitor status
python email_bot_manager.py status
```

## 🔐 Security Best Practices

1. **Use App Passwords** instead of main Gmail password
2. **Store secrets securely** in GitHub Secrets
3. **Limit recipient lists** to authorized emails
4. **Monitor sending patterns** to avoid spam flags
5. **Use BCC** for large recipient lists
6. **Regular credential rotation**

## 🎉 Success Indicators

✅ **Gmail connection successful**  
✅ **Test email received**  
✅ **Automated emails sending**  
✅ **Content diversity maintained**  
✅ **No spam flags**  
✅ **Recipients receiving emails**

## 📞 Support

If you encounter issues:

1. **Check logs** in `email_bot.log`
2. **Verify configuration** with status command
3. **Test connection** with test command
4. **Review GitHub Actions** logs
5. **Check Gmail settings** and quotas

Your Email Bot is now ready to send automated, human-like emails! 🚀📧
