#!/usr/bin/env python3
"""
BloggerBot Manager - Monitor and manage the bot's human-like behavior patterns.
"""
import os
import sys
import json
import argparse
from datetime import datetime
from src.blogger_bot import BloggerBot
from src.services.posting_scheduler import PostingScheduler
from src.services.content_diversity import ContentDiversityService
from src.utils.logger import setup_logger
import logging

def show_status():
    """Show comprehensive bot status."""
    print("🤖 BloggerBot Status Report")
    print("=" * 50)
    
    try:
        bot = BloggerBot()
        status = bot.get_bot_status()
        
        # Posting status
        can_post, reason = status['can_post_now']
        print(f"📊 Current Status: {'✅ Ready to post' if can_post else f'⏸️ {reason}'}")
        print(f"🕐 Next posting time: {status['next_posting_time']}")
        print(f"📈 Posting pattern: {status['posting_pattern']}")
        
        # Performance metrics
        perf = status['recent_performance']
        print(f"\n📈 Recent Performance:")
        print(f"   Daily posts: {perf['daily_posts']}")
        print(f"   Weekly posts: {perf['weekly_posts']}")
        print(f"   Success rate: {perf['success_rate']:.1%}")
        
        # Content diversity
        diversity = status['content_diversity']
        print(f"\n🎨 Content Diversity:")
        print(f"   Diversity score: {diversity['score']:.1f}/100")
        print(f"   Recommendations:")
        for rec in diversity['recommendations']:
            print(f"     • {rec}")
            
    except Exception as e:
        print(f"❌ Error getting status: {e}")

def run_bot(force=False):
    """Run the bot with human-like behavior."""
    if force:
        print("🚀 Starting BloggerBot with FORCE mode (ignoring posting schedule)...")
    else:
        print("🚀 Starting BloggerBot with human-like behavior...")
    
    try:
        bot = BloggerBot()
        if force:
            # Temporarily override the scheduler and behavior settings to force posting
            bot.scheduler.posting_history = []  # Clear history to allow immediate posting
            bot.scheduler.force_post = True  # Add this flag to skip random delays
        success = bot.run()
        
        if success:
            print("\n✅ Bot run completed successfully!")
        else:
            print("\n⏸️ Bot run skipped or failed - check logs for details")
            
    except Exception as e:
        print(f"\n❌ Error running bot: {e}")
        logging.error(f"Bot manager error: {e}")

def force_run_bot():
    """Force run the bot ignoring posting schedule (for testing)."""
    run_bot(force=True)

def adjust_posting_pattern(pattern):
    """Adjust the bot's posting pattern."""
    valid_patterns = ['conservative', 'moderate', 'active']
    
    if pattern not in valid_patterns:
        print(f"❌ Invalid pattern. Choose from: {', '.join(valid_patterns)}")
        return
    
    try:
        scheduler = PostingScheduler()
        scheduler.adjust_posting_pattern(pattern)
        print(f"✅ Posting pattern adjusted to: {pattern}")
        
        # Show new pattern details
        patterns = scheduler.posting_patterns[pattern]
        print(f"   Min hours between posts: {patterns['min_hours']}")
        print(f"   Max hours between posts: {patterns['max_hours']}")
        print(f"   Daily post limit: {patterns['daily_limit']}")
        
    except Exception as e:
        print(f"❌ Error adjusting pattern: {e}")

def show_diversity_report():
    """Show detailed content diversity report."""
    print("🎨 Content Diversity Report")
    print("=" * 50)
    
    try:
        diversity_service = ContentDiversityService()
        stats = diversity_service.get_diversity_stats()
        
        if 'message' in stats:
            print(stats['message'])
            return
        
        print(f"📊 Total posts analyzed: {stats['total_posts']}")
        print(f"🎯 Overall diversity score: {stats['diversity_score']:.1f}/100")
        
        print(f"\n📂 Category Distribution:")
        for category, count in stats['category_distribution'].items():
            print(f"   {category}: {count} posts")
        
        print(f"\n🔤 Most Common Keywords:")
        for keyword, freq in stats['most_common_keywords']:
            print(f"   {keyword}: {freq} times")
        
        print(f"\n💡 Recommendations:")
        for rec in stats['recommendations']:
            print(f"   • {rec}")
            
    except Exception as e:
        print(f"❌ Error getting diversity report: {e}")

def show_posting_history():
    """Show recent posting history."""
    print("📚 Recent Posting History")
    print("=" * 50)
    
    try:
        scheduler = PostingScheduler()
        
        if not scheduler.posting_history:
            print("No posting history available.")
            return
        
        # Show last 10 posts
        recent_posts = scheduler.posting_history[-10:]
        
        for post in reversed(recent_posts):
            timestamp = datetime.fromisoformat(post['timestamp'])
            status = "✅" if post['success'] else "❌"
            print(f"{status} {timestamp.strftime('%Y-%m-%d %H:%M')} - {post['topic']}")
            if post.get('post_url'):
                print(f"   🔗 {post['post_url']}")
        
        # Show statistics
        stats = scheduler.get_posting_stats()
        print(f"\n📊 Statistics:")
        print(f"   Success rate: {stats['success_rate']:.1%}")
        print(f"   Posts this week: {stats['weekly_posts']}")
        print(f"   Posts today: {stats['daily_posts']}")
        
    except Exception as e:
        print(f"❌ Error getting posting history: {e}")

def reset_history():
    """Reset posting and content history (use with caution)."""
    confirm = input("⚠️ This will reset all posting and content history. Are you sure? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Reset cancelled.")
        return
    
    try:
        # Reset posting history
        scheduler = PostingScheduler()
        scheduler.posting_history = []
        scheduler._save_posting_history()
        
        # Reset content diversity history
        diversity_service = ContentDiversityService()
        diversity_service.content_history = []
        diversity_service._save_content_history()
        
        print("✅ All history has been reset.")
        
    except Exception as e:
        print(f"❌ Error resetting history: {e}")

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="BloggerBot Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show bot status')
    
    # Run command
    subparsers.add_parser('run', help='Run the bot')
    
    # Force run command
    subparsers.add_parser('forcerun', help='Force run the bot (ignoring posting schedule)')
    
    # Pattern command
    pattern_parser = subparsers.add_parser('pattern', help='Adjust posting pattern')
    pattern_parser.add_argument('type', choices=['conservative', 'moderate', 'active'],
                               help='Posting pattern type')
    
    # Diversity command
    subparsers.add_parser('diversity', help='Show content diversity report')
    
    # History command
    subparsers.add_parser('history', help='Show posting history')
    
    # Reset command
    subparsers.add_parser('reset', help='Reset all history (use with caution)')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logger()
    
    if args.command == 'status':
        show_status()
    elif args.command == 'run':
        run_bot()
    elif args.command == 'forcerun':
        force_run_bot()
    elif args.command == 'pattern':
        adjust_posting_pattern(args.type)
    elif args.command == 'diversity':
        show_diversity_report()
    elif args.command == 'history':
        show_posting_history()
    elif args.command == 'reset':
        reset_history()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
