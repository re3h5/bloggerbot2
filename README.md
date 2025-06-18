# AI Blogger Bot

An intelligent automation tool that generates and publishes engaging blog posts to your Blogger site. It fetches trending topics (including cryptocurrency trends), uses AI to create high-quality content with proper thumbnail images, and automatically categorizes posts with appropriate labels.

This automated blogging system combines trending topic discovery, AI-powered content generation, and image integration to create professional-looking blog posts with minimal human intervention.

> **IMPORTANT SECURITY NOTE**: This repository does not contain any sensitive API keys or credentials. You will need to create your own credential files based on the example files provided. See the [Security and Credentials](#security-and-credentials) section for details.

## Features

### Core Functionality
- 🔍 Fetches trending topics using Google Trends API with AI fallback
- 💰 Includes cryptocurrency trends (BTC, ETH) in topic discovery
- 📰 Creates engaging, clickable headlines using AI (without quotation marks)
- 🤖 Generates high-quality blog posts using OpenRouter AI
- 🖼️ Automatically generates relevant images with proper thumbnails for Blogger
- 🔄 Multi-tiered image fetching with Pixabay, Pexels, and placeholder fallbacks
- 📝 Posts automatically to Blogger with smart label classification
- 🏷️ Smart label classification system for better content organization

### Human-like Behavior & Anti-Spam
- 🧠 **Human-like Posting Patterns**: Natural delays and posting schedules (3-4 posts/day, 19-27/week)
- ⏰ **Smart Scheduling**: Preferred posting hours (9 AM - 6 PM) with realistic inconsistency
- 🎨 **Content Diversity**: Tracks topics, keywords, and writing styles to prevent repetition
- 🛡️ **Spam Prevention**: Advanced content filtering and quality checks
- 📊 **Analytics**: Success rates, diversity scores, and posting statistics

### Automation & Management
- 🚀 **GitHub Actions**: Automated posting with human-like behavior
- 🎛️ **Bot Manager CLI**: Easy monitoring, configuration, and manual control
- 📈 **Multiple Posting Patterns**: Conservative, Moderate, and Active modes
- 🔄 **Force Override**: Manual posting for testing and immediate needs

### Technical Features
- 📊 Comprehensive logging with Unicode emoji support (Windows-compatible)
- ⚠️ Robust error handling with API rate limiting and retries
- 🔄 Automatic OAuth token refreshing
- 🧹 Clean project structure with proper organization

## Prerequisites

1. Python 3.7 or higher
2. A Google Cloud Project with Blogger API enabled
3. An OpenRouter API key
4. A Blogger blog

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd bloggerbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the Blogger API for your project
4. Create OAuth 2.0 credentials:
   - Go to Credentials
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app"
   - Download the client configuration file
   - Save it as `client_secrets.json` in the project directory

### 4. Environment Configuration

Create a `.env` file in the project root with the following content:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
BLOGGER_ID=your_blogger_id
PIXABAY_API_KEY=your_pixabay_api_key  # Optional, for better images
```

Replace:

- `your_openrouter_api_key` with your OpenRouter API key
- `your_blogger_id` with your Blogger blog ID (find it in your Blogger URL or settings)
- `your_pixabay_api_key` with your Pixabay API key (optional, get a free key at [Pixabay API](https://pixabay.com/api/docs/))

### 5. Generate Google OAuth Token

1. Run the authentication script:

```bash
python src/get_token.py
```

2. Follow the browser prompts to authenticate
3. Allow the application access to your Blogger account
4. The script will generate `config/token.json`

## Usage

### Starting the Bot

Run the main script:

```bash
python main.py
```

The bot will:

1. Start immediately with one post
2. Continue running on a schedule (every 6 hours)
3. Log all activities to `blogger_bot.log`

## AI-Powered Content Generation

### Trending Topic Discovery

The bot uses a multi-tiered approach to discover trending topics:

1. **Google Trends API** (Primary Source)
   - Attempts multiple methods to fetch real trending topics
   - Uses interest_over_time and suggestions APIs
   - Rotates through different categories for variety

2. **AI Trend Forecasting** (Smart Fallback)
   - When Google Trends fails, the bot asks AI to suggest trending topics
   - Uses GPT to identify currently popular or emerging topics
   - Ensures topics are specific enough for engaging content

3. **Curated Default Topics** (Final Fallback)
   - If all else fails, selects from a list of evergreen topics
   - Topics are carefully selected to be relevant across time periods

### Engaging Headlines

The bot generates clickable, SEO-optimized headlines:

- Uses AI to craft headlines that grab attention while maintaining accuracy
- Ensures headlines include the main topic keyword
- Optimizes length for SEO (under 60 characters)
- Uses power words and creates curiosity to improve click-through rates

## Image Generation

The bot automatically generates relevant images for each blog post using multiple sources:

1. **Pixabay API** (Primary Source)
   - Requires a free Pixabay API key in your `.env` file
   - Fetches high-quality, royalty-free images related to the blog topic
   - Configured to return landscape-oriented images for better blog display

2. **Pexels API** (Fallback)
   - Used automatically if Pixabay fails or no API key is provided
   - No API key required for basic usage
   - Also configured for landscape orientation

3. **Placeholder Images** (Final Fallback)
   - Generated if both Pixabay and Pexels fail
   - Creates a simple placeholder image with the topic name
   - Maintains 16:9 aspect ratio (1200x675)

All images are embedded directly in the blog post with responsive CSS styling to maintain proper display across devices.

### Available Labels

The bot automatically classifies posts into these categories:

- Art
- Travel
- Life Style
- Photography
- Nature
- Food
- Adventure

### Monitoring

Check the `blogger_bot.log` file for:

- Trending topics fetched
- Content generation status
- Posting results
- Any errors or issues

## Error Handling

The bot includes robust error handling for:

- API rate limits with progressive backoff
- Network issues with automatic retries
- Authentication problems with token refreshing
- Content generation failures with fallback mechanisms
- Permission issues with detailed error messages

It will automatically retry operations and log any issues.

## Project Structure

```
bloggerbot2/
├── .env                  # Environment variables
├── .gitignore            # Git ignore file
├── README.md             # Documentation
├── main.py               # Main entry point
├── config/               # Configuration files
│   ├── credentials.json  # OAuth credentials
│   └── token.json        # OAuth token
├── images/               # Generated images (gitignored)
├── logs/                 # Log files
└── src/                  # Source code
    ├── blogger_bot.py    # Main bot class
    ├── get_token.py      # Token generation script
    ├── services/         # Service modules
    │   ├── blogger_service.py
    │   ├── content_generator.py
    │   ├── image_service.py
    │   └── trending_topics.py
    └── utils/            # Utility modules
        ├── config.py     # Configuration
        ├── logger.py     # Logging setup
        ├── rate_limiter.py
        └── token_manager.py  # Token management
```

## Recent Improvements 

### Version 2.1 - OAuth & Token Management Improvements
- **🔧 Fixed OAuth Authentication**: Resolved redirect URI mismatch errors and port conflicts
- **🔑 Enhanced Token Generation**: Improved token manager with automatic process management and port handling
- **🖥️ Windows Compatibility**: Fixed Unicode emoji logging issues on Windows systems
- **🔄 Refresh Token Support**: Added proper refresh token handling with offline access
- **🛠️ Better Error Handling**: Enhanced error messages and troubleshooting guidance
- **📱 Multi-Port Support**: Automatic port detection and conflict resolution for OAuth redirect
- **🎯 Web Client Support**: Full compatibility with both desktop and web application OAuth clients

### Key Features
- **🤖 AI-Powered Content Generation**: Uses OpenRouter API for high-quality blog content
- **📈 Trending Topics**: Automatically fetches trending topics from Google Trends
- **🖼️ Smart Image Integration**: Multi-source image fetching with automatic thumbnail support
- **📝 Content Cleanup**: Advanced content and headline cleanup for professional posts
- **🔐 Secure Authentication**: OAuth 2.0 with proper token management and refresh handling
- **⚡ Automated Posting**: Scheduled posting via GitHub Actions
- **📊 Rate Limit Management**: Built-in API rate limiting and quota management

## Quick Start 

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd bloggerbot2
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Setup Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Blogger API v3
4. Create OAuth 2.0 credentials (Web Application or Desktop Application)
5. Add `http://localhost:8080` to authorized redirect URIs
6. Download credentials as `config/credentials.json`

### 4. Generate OAuth Token
```bash
python src/get_token.py
```
**Important**: If you get "No refresh_token found" warning:
1. Go to https://myaccount.google.com/permissions
2. Remove access for your BloggerBot app
3. Run the token generation again for a fresh consent flow

### 5. Run the Bot
```bash
python main.py
```

## Troubleshooting 

### OAuth Issues
- **Error 400: redirect_uri_mismatch**
  - Ensure `http://localhost:8080` is added to your OAuth client's authorized redirect URIs
  - Check that your `credentials.json` file is properly configured

- **Port 8080 already in use**
  - The bot automatically handles port conflicts and finds available ports
  - If issues persist, close applications using port 8080 or restart your system

- **No refresh_token found**
  - Revoke app permissions at https://myaccount.google.com/permissions
  - Run `python src/get_token.py` again for fresh consent
  - This ensures you get a refresh token for long-term operation

### Token Issues
- **"Authorized user info was not in the expected format"**
  - Delete `config/token.json` and regenerate with `python src/get_token.py`
  - Ensure you completed the full OAuth consent flow

- **Authentication failed: Invalid credentials**
  - Check your `BLOGGER_ID` in the `.env` file
  - Verify your blog is accessible and you have admin permissions
  - Regenerate token if it's expired

### Content Generation Issues
- **Unicode logging errors on Windows**
  - Fixed in latest version with Windows-safe emoji logging
  - Emojis are automatically converted to text equivalents

- **Missing thumbnails in posts**
  - Ensure `PIXABAY_API_KEY` is set in `.env` (optional but recommended)
  - Images are embedded in content for automatic thumbnail extraction

- **Rate limiting errors**
  - Built-in rate limiting prevents API quota exhaustion
  - Check `rate_limits/blogger_api_calls.json` for current usage

### GitHub Actions Issues
- **Workflow fails with missing secrets**
  - Add all required secrets: `GOOGLE_CREDENTIALS`, `BLOGGER_TOKEN`, `OPENROUTER_API_KEY`, `BLOGGER_ID`
  - `PIXABAY_API_KEY` is optional but recommended

- **Token expires in GitHub Actions**
  - Refresh tokens are automatically handled
  - If issues persist, regenerate and update `BLOGGER_TOKEN` secret

## Security and Credentials

### Sensitive Files

This repository contains example files for all required credentials. You must create your own versions of these files with your actual credentials:

1. `credentials.json` - Create this from the example file `credentials.json.example`
2. `client_secret.json` - Create this from the example file `client_secret.json.example`
3. `config/token.json` - Create this from the example file `config/token.json.example`
4. `.env` - Create this from the example file `.env.example`

### Security Best Practices

1. **NEVER commit sensitive credentials to public repositories**
2. Add all credential files to your `.gitignore`
3. Use environment variables or secrets for CI/CD pipelines
4. Regularly rotate your API keys and credentials
5. Limit the scope of OAuth permissions to only what's needed

### Setting Up Credential Files

1. **For credentials.json and client_secret.json**:
   - Follow the Google Cloud Setup instructions above
   - Download the OAuth credentials from Google Cloud Console
   - Save them to the appropriate files

2. **For token.json**:
   - Run the `get_token.py` script which will generate this file
   - This file contains your OAuth access tokens

3. **For .env**:
   - Create this file with your API keys as shown in the Environment Configuration section

## License

[Your chosen license]

## Contributing

[Your contribution guidelines]

## GitHub Actions Setup

The bot can run automatically using GitHub Actions. To set this up:

1. Fork this repository
2. Go to your forked repository's Settings
3. Navigate to "Secrets and variables" → "Actions"
4. Add the following secrets:

### Required Secrets

1. `GOOGLE_CREDENTIALS`

   - Content: Your entire Google OAuth credentials JSON
   - How to get:
     1. Go to Google Cloud Console
     2. Navigate to your project
     3. Go to APIs & Services → Credentials
     4. Download your OAuth 2.0 Client credentials
     5. Copy the entire JSON content
   - Example format:
     ```json
     {
       "installed": {
         "client_id": "your-client-id.apps.googleusercontent.com",
         "project_id": "your-project-id",
         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
         "token_uri": "https://oauth2.googleapis.com/token",
         "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
         "client_secret": "your-client-secret",
         "redirect_uris": ["http://localhost"]
       }
     }
     ```

2. `OPENROUTER_API_KEY`

   - Content: Your OpenRouter API key
   - How to get:
     1. Go to [OpenRouter](https://openrouter.ai/api-keys)
     2. Create or copy your API key
   - Format: `sk-or-v1-xxxxxxxxxxxx...`

3. `BLOGGER_ID`
   - Content: Your Blogger blog ID
   - How to get:
     1. Go to your Blogger dashboard
     2. The ID is in your blog's URL or settings
   - Format: A long number like `1234567890123456789`

4. `BLOGGER_TOKEN`
   - Content: Your pre-generated Blogger API token
   - How to get:
     1. Run the `get_token.py` script locally on your machine
     2. After authentication completes, find the generated token at `config/token.json`
     3. Copy the entire contents of this file
   - Example format:
     ```json
     {
       "token": "ya29.a0AfB_...",
       "refresh_token": "1//0gGm...",
       "token_uri": "https://oauth2.googleapis.com/token",
       "client_id": "your-client-id.apps.googleusercontent.com",
       "client_secret": "your-client-secret",
       "scopes": ["https://www.googleapis.com/auth/blogger"],
       "expiry": "2025-06-17T20:54:02.886Z"
     }
     ```

### Workflow Schedule

The bot is configured to run every hour by default. You can modify this in `.github/workflows/bot.yml`:

```yaml
on:
  schedule:
    - cron: "0 */1 * * *" # Runs every hour
```

Common cron examples:

- Every 2 hours: `0 */2 * * *`
- Every 6 hours: `0 */6 * * *`
- Twice daily: `0 */12 * * *`
- Once daily: `0 0 * * *`

### Manual Trigger

You can also trigger the bot manually:

1. Go to the "Actions" tab
2. Select "Blogger Auto Bot"
3. Click "Run workflow"

### Monitoring GitHub Actions

Check the "Actions" tab to:

- View run history
- Check execution logs
- Monitor for any errors
- Verify successful posts
