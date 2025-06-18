# Human-like Behavior & Anti-Spam Features

This document describes the advanced human-like behavior patterns and anti-spam measures implemented in BloggerBot v2.1.

## Overview

To prevent your account from being flagged for spam or automated behavior, BloggerBot now includes sophisticated human-like posting patterns, content diversity controls, and quality filters.

## Key Features

### 🕐 Smart Posting Scheduler

The posting scheduler prevents spam detection by implementing human-like posting patterns:

- **Minimum delays between posts** (1-72 hours depending on pattern)
- **Daily and weekly posting limits**
- **Preferred posting hours** (9 AM - 6 PM)
- **Random posting skips** (10% chance to skip for natural inconsistency)
- **Progressive delays** based on posting history

### 🎨 Content Diversity Engine

Ensures your content remains varied and original:

- **Topic categorization** across technology, business, lifestyle, education, entertainment, and news
- **Keyword tracking** to prevent overuse of similar terms
- **Content structure variation** using different writing styles and formats
- **Similarity detection** to avoid repetitive content
- **Writing angle rotation** (how-to guides, trend analysis, comparisons, etc.)

### 🛡️ Spam Prevention System

Advanced content filtering to avoid spam detection:

- **Spam phrase detection** (removes "click here", "buy now", "limited time", etc.)
- **Excessive punctuation filtering** (limits exclamation marks)
- **Caps lock normalization** (converts excessive capitals)
- **Content quality scoring** (minimum length, uniqueness checks)
- **Promotional language filtering**

## Posting Patterns

### Conservative Pattern (Recommended for new accounts)
```
Minimum delay: 8 hours
Maximum delay: 72 hours
Daily limit: 1 post
Risk level: Low
```

### Moderate Pattern (Default)
```
Minimum delay: 4 hours
Maximum delay: 48 hours
Daily limit: 2 posts
Risk level: Medium
```

### Active Pattern (Use with caution)
```
Minimum delay: 2 hours
Maximum delay: 24 hours
Daily limit: 3 posts
Risk level: Higher
```

## Bot Manager Commands

### Check Status
```bash
python bot_manager.py status
```
Shows:
- Current posting eligibility
- Next suggested posting time
- Recent performance metrics
- Content diversity score

### Run Bot
```bash
python bot_manager.py run
```
Executes the bot with all human-like behavior features enabled.

### View Diversity Report
```bash
python bot_manager.py diversity
```
Shows:
- Category distribution
- Most common keywords
- Diversity recommendations
- Overall diversity score

### View Posting History
```bash
python bot_manager.py history
```
Shows:
- Recent posting attempts
- Success/failure rates
- Posting timestamps
- Performance statistics

### Adjust Posting Pattern
```bash
python bot_manager.py pattern conservative
python bot_manager.py pattern moderate
python bot_manager.py pattern active
```

### Reset History (Use with caution)
```bash
python bot_manager.py reset
```
Clears all posting and content history.

## Content Quality Improvements

### Enhanced AI Prompts
- **Dynamic writing styles**: Conversational, professional, analytical, storytelling, practical
- **Varied content structures**: Problem-solution, step-by-step, comparison, narrative, FAQ
- **Current date awareness**: References current month/year in content
- **Natural language patterns**: Avoids robotic or template-like writing

### Quality Filters
- **Spam indicator detection**: Automatically flags and regenerates content with spam-like phrases
- **Content length validation**: Ensures minimum quality standards
- **Repetition detection**: Identifies and prevents excessive content repetition
- **Keyword density monitoring**: Maintains natural keyword usage

### Content Cleanup
- **HTML artifact removal**: Cleans unwanted HTML tags and code blocks
- **Formatting normalization**: Removes excessive whitespace and formatting
- **Headline cleanup**: Removes quotation marks and unwanted characters
- **Emoji handling**: Proper Unicode support for Windows compatibility

## Monitoring and Analytics

### Posting Statistics
- Daily and weekly post counts
- Success rate tracking
- Pattern adherence monitoring
- Next posting time predictions

### Content Diversity Metrics
- Category distribution analysis
- Keyword frequency tracking
- Topic similarity scoring
- Diversity recommendations

### Performance Indicators
- Overall diversity score (0-100)
- Spam risk assessment
- Content quality ratings
- Posting pattern compliance

## Best Practices

### For New Accounts
1. Start with **conservative** posting pattern
2. Monitor success rates closely
3. Gradually increase posting frequency if successful
4. Focus on content quality over quantity

### For Established Accounts
1. Use **moderate** pattern as default
2. Monitor diversity scores regularly
3. Adjust patterns based on performance
4. Maintain consistent posting schedule

### Content Strategy
1. Vary topics across different categories
2. Use different writing styles and formats
3. Include personal insights and examples
4. Avoid promotional language
5. Focus on providing genuine value

## Troubleshooting

### Low Diversity Scores
- Increase topic variety across categories
- Use different writing styles
- Vary content length significantly
- Avoid repeating similar keywords

### Posting Restrictions
- Check if you're within daily/weekly limits
- Verify posting hours (9 AM - 6 PM recommended)
- Ensure minimum time between posts has passed
- Consider adjusting to more conservative pattern

### Content Quality Issues
- Review spam indicator warnings in logs
- Ensure content meets minimum length requirements
- Check for excessive repetition or promotional language
- Regenerate content if quality score is low

## Configuration Files

### Posting Schedule
`config/posting_schedule.json` - Stores posting history and timing data

### Content Diversity
`config/content_diversity.json` - Tracks content patterns and diversity metrics

Both files are automatically created and managed by the system.

## Migration from Previous Versions

If upgrading from an older version:

1. The bot will automatically create new configuration files
2. No existing functionality is affected
3. New features are enabled by default
4. Use `bot_manager.py status` to check current state

## Security Considerations

The human-like behavior features are designed to:
- Reduce the risk of account suspension
- Maintain natural posting patterns
- Avoid spam detection algorithms
- Preserve account reputation

However, always ensure you comply with:
- Google's Terms of Service
- Blogger's Community Guidelines
- Platform-specific posting policies
- Local regulations regarding automated content

## Support

For issues related to human-like behavior features:
1. Check the logs for detailed error messages
2. Use `bot_manager.py status` for diagnostic information
3. Review diversity and posting statistics
4. Adjust patterns based on performance metrics
