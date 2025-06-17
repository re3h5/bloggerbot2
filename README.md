# AI Blogger Bot

An intelligent automation tool that generates and publishes engaging blog posts to your Blogger site. It fetches trending topics (with focus on Bangladesh), uses AI to create high-quality content, and automatically categorizes posts with appropriate labels.

An automated blogging system that fetches trending topics, generates engaging blog posts using AI, and publishes them to your Blogger site with appropriate labels.

> **IMPORTANT SECURITY NOTE**: This repository does not contain any sensitive API keys or credentials. You will need to create your own credential files based on the example files provided. See the [Security and Credentials](#security-and-credentials) section for details.

## Features

- 🔍 Fetches trending topics using Google Trends API
- 🤖 Generates high-quality blog posts using OpenRouter AI
- 🖼️ Automatically generates relevant images for each post
- 📝 Posts automatically to Blogger with smart label classification
- ⏰ Runs on a schedule (every 6 hours by default)
- 🏷️ Smart label classification system
- 📊 Comprehensive logging
- ⚠️ Error handling and retries with multiple fallback mechanisms

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
python get_token.py
```

2. Follow the browser prompts to authenticate
3. Allow the application access to your Blogger account
4. The script will generate `token.json`

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

- API rate limits
- Network issues
- Authentication problems
- Content generation failures

It will automatically retry operations and log any issues.

## Customization

### Modifying Schedule

Edit the schedule in `main.py`:

```python
schedule.every(6).hours.do(job)  # Change 6 to your preferred interval
```

### Adjusting Default Topics

Edit the `default_topics` list in the `BloggerBot` class to modify fallback topics when trending topics can't be fetched.

### Label Classification

The label classification system uses keyword matching. You can modify the keywords in the `classify_topic` method to improve categorization for your specific needs.

## Logging

Logs are written to `blogger_bot.log` with UTF-8 encoding. The log includes:

- Timestamp for each operation
- Success/failure indicators
- Error messages and stack traces
- Post URLs after successful publishing

## Troubleshooting

1. **Authentication Failed**: Run `get_token.py` again to refresh OAuth token
2. **API Rate Limits**: Check the logs and adjust posting frequency if needed
3. **Content Generation Issues**: Verify OpenRouter API key and connectivity

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
