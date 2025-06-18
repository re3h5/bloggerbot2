# GitHub Actions Setup for BloggerBot

This document explains how to set up and use the GitHub Actions workflow for automated blog posting with human-like behavior.

## Features

- **Automated Posting**: Runs every 2 hours to check if it's time to post
- **Human-like Behavior**: Respects posting schedules and natural delays
- **Manual Control**: Force run or adjust posting patterns via workflow dispatch
- **Health Monitoring**: Status checks and performance analytics
- **Config Persistence**: Automatically saves posting history and diversity data

## Required Secrets

Set up these secrets in your GitHub repository (Settings → Secrets and variables → Actions):

### Required Secrets
- `GOOGLE_CREDENTIALS`: Your Google API credentials JSON (entire file content)
- `BLOGGER_TOKEN`: Your Blogger API token JSON (entire file content)
- `OPENROUTER_API_KEY`: Your OpenRouter API key for AI content generation
- `BLOGGER_ID`: Your Blogger blog ID

### Optional Secrets
- `PIXABAY_API_KEY`: For image generation (optional, will use fallbacks)

## Workflow Triggers

### Automatic (Scheduled)
- Runs every 2 hours via cron: `0 */2 * * *`
- Only posts if the human-like posting schedule allows it
- Performs health checks and status monitoring

### Manual (Workflow Dispatch)
You can manually trigger the workflow with options:

1. **Force Run**: `true/false` - Ignores posting schedule for immediate posting
2. **Posting Pattern**: `conservative/moderate/active` - Sets the posting frequency

## Workflow Jobs

### Main Job: `blog-post`
1. **Setup**: Installs Python, dependencies, and credentials
2. **Status Check**: Shows current bot status and posting statistics
3. **Pattern Setup**: Applies posting pattern if specified
4. **Bot Execution**: Runs the bot with human-like behavior
5. **Reporting**: Shows statistics, diversity reports, and history
6. **Persistence**: Commits updated config files back to repository

### Health Check Job: `health-check`
- Runs alongside the main job for scheduled triggers
- Provides quick status overview
- Alerts if posting should happen soon

## Usage Examples

### Manual Workflow Dispatch

1. **Regular Run** (respects schedule):
   ```
   Force run: false
   Posting pattern: moderate
   ```

2. **Force Post** (ignores schedule):
   ```
   Force run: true
   Posting pattern: active
   ```

3. **Change Pattern Only**:
   ```
   Force run: false
   Posting pattern: conservative
   ```

### Monitoring

Check the Actions tab in your GitHub repository to:
- View posting logs and statistics
- Download log artifacts
- Monitor success/failure rates
- Track content diversity metrics

## Posting Patterns

The workflow supports three posting patterns:

- **Conservative**: 6-12 hours between posts, max 3/day
- **Moderate**: 4-8 hours between posts, max 4/day  
- **Active**: 2-6 hours between posts, max 4/day

## Configuration Files

The workflow automatically manages these config files:
- `config/posting_schedule.json`: Posting history and schedule
- `config/content_diversity.json`: Content diversity tracking

These files are committed back to the repository to maintain state between runs.

## Troubleshooting

### Common Issues

1. **Missing Secrets**: Ensure all required secrets are set correctly
2. **Token Expiry**: Refresh your Blogger token if authentication fails
3. **Rate Limits**: The bot respects API limits and will skip posting if needed
4. **Schedule Conflicts**: Use force run to override posting schedule for testing

### Debugging

1. Check the Actions logs for detailed error messages
2. Download log artifacts for offline analysis
3. Use the status command to check bot health
4. Review posting history for patterns

### Log Artifacts

Each run creates log artifacts containing:
- Bot execution logs
- Posting schedule data
- Content diversity metrics
- Error details (if any)

## Best Practices

1. **Don't Force Run Too Often**: Respect the human-like posting schedule
2. **Monitor Diversity**: Check content diversity reports regularly
3. **Adjust Patterns**: Use different posting patterns based on your needs
4. **Review Logs**: Check for API errors or content quality issues
5. **Update Secrets**: Refresh tokens before they expire

## Security Notes

- Secrets are encrypted and only accessible during workflow execution
- Config files don't contain sensitive information
- Logs are automatically cleaned up after 7 days
- Use repository secrets, not environment variables in code

## Advanced Configuration

You can modify the workflow to:
- Change the cron schedule frequency
- Add notification steps (email, Slack, etc.)
- Implement custom posting logic
- Add additional health checks
- Integrate with monitoring services

For more advanced configurations, edit `.github/workflows/blogger-bot.yml` directly.
