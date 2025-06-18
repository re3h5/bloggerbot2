#!/usr/bin/env python3
"""
Email Bot Manager - CLI interface for managing the Email Bot
Provides commands to run, test, monitor, and configure the email bot
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from email_bot import EmailBot

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('email_bot.log'),
            logging.StreamHandler()
        ]
    )

def print_status(status: Dict[str, Any]):
    """Print bot status in a formatted way"""
    print("\n" + "="*60)
    print("📧 EMAIL BOT STATUS")
    print("="*60)
    
    print(f"🤖 Bot Type: {status['bot_type']}")
    print(f"📧 Gmail Connected: {'✅ Yes' if status['gmail_connected'] else '❌ No'}")
    print(f"🔗 Gmail Method: {status['gmail_method']}")
    print(f"⏰ Last Check: {status['last_check']}")
    
    print("\n📊 POSTING SCHEDULE STATUS:")
    schedule = status['schedule_status']
    print(f"   Pattern: {schedule['current_pattern']}")
    print(f"   Posts Today: {schedule['posts_today']}/{schedule['daily_limit']}")
    print(f"   Posts This Week: {schedule['posts_this_week']}/{schedule['weekly_limit']}")
    print(f"   Last Post: {schedule['last_post_time'] or 'Never'}")
    print(f"   Next Eligible: {schedule['next_eligible_time'] or 'Now'}")
    
    print("\n🎯 CONTENT DIVERSITY:")
    diversity = status['diversity_report']
    print(f"   Diversity Score: {diversity['diversity_score']:.1f}/10")
    print(f"   Total Posts: {diversity['total_posts']}")
    print(f"   Unique Topics: {len(diversity.get('topic_distribution', {}))}")
    print(f"   Avg Length: {diversity.get('avg_length', 0):.0f} chars")
    
    print("\n📧 EMAIL CONFIGURATION:")
    email_config = status['email_config']
    print(f"   Max Daily Emails: {email_config['sending_preferences']['max_daily_emails']}")
    print(f"   Preferred Hours: {email_config['sending_preferences']['preferred_hours']}")
    print(f"   Avoid Weekends: {email_config['sending_preferences']['avoid_weekends']}")
    
    print("\n📈 EMAIL TYPES:")
    for email_type, config in email_config['email_types'].items():
        print(f"   {config['subject_prefix']} {email_type.title()}: {config['weight']}% weight")

def print_diversity_report(bot: EmailBot):
    """Print detailed content diversity report"""
    report = bot.content_diversity.get_diversity_report()
    
    print("\n" + "="*60)
    print("🎯 CONTENT DIVERSITY REPORT")
    print("="*60)
    
    print(f"Overall Diversity Score: {report['diversity_score']:.1f}/10")
    print(f"Total Posts: {report['total_posts']}")
    print(f"Average Length: {report.get('avg_length', 0):.0f} characters")
    
    if 'topic_distribution' in report and report['topic_distribution']:
        print("\n📊 Topic Distribution:")
        for topic, count in sorted(report['topic_distribution'].items(), 
                                 key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / report['total_posts']) * 100
            print(f"   {topic}: {count} posts ({percentage:.1f}%)")
    
    if 'keyword_frequency' in report and report['keyword_frequency']:
        print("\n🔤 Top Keywords:")
        for keyword, count in sorted(report['keyword_frequency'].items(), 
                                   key=lambda x: x[1], reverse=True)[:15]:
            print(f"   {keyword}: {count} times")
    
    if 'category_distribution' in report and report['category_distribution']:
        print("\n📂 Category Distribution:")
        for category, count in report['category_distribution'].items():
            percentage = (count / report['total_posts']) * 100
            print(f"   {category}: {count} posts ({percentage:.1f}%)")
    
    # Recommendations
    if 'recommendations' in report and report['recommendations']:
        print("\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   • {rec}")

def print_posting_history(bot: EmailBot):
    """Print posting history"""
    history = bot.posting_scheduler.get_posting_history()
    
    print("\n" + "="*60)
    print("📅 EMAIL SENDING HISTORY")
    print("="*60)
    
    if not history:
        print("No emails sent yet.")
        return
    
    print(f"Total Emails Sent: {len(history)}")
    
    # Group by date
    by_date = {}
    for post in history:
        date = post['timestamp'][:10]  # Get date part
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(post)
    
    # Show recent dates
    for date in sorted(by_date.keys(), reverse=True)[:7]:
        posts = by_date[date]
        print(f"\n📅 {date} ({len(posts)} emails):")
        for post in posts:
            time_part = post['timestamp'][11:16]  # Get time part
            print(f"   {time_part} - Email sent")

def run_email_bot(force_send: bool = False, pattern: str = None, 
                 max_emails: int = 1, recipients: List[str] = None,
                 email_type: str = None, use_api: bool = False):
    """Run the email bot"""
    
    print(f"\n🚀 Starting Email Bot...")
    print(f"   Force Send: {force_send}")
    print(f"   Max Emails: {max_emails}")
    print(f"   Gmail Method: {'API' if use_api else 'SMTP'}")
    if pattern:
        print(f"   Pattern: {pattern}")
    if recipients:
        print(f"   Recipients: {', '.join(recipients)}")
    if email_type:
        print(f"   Email Type: {email_type}")
    
    # Initialize bot
    bot = EmailBot(use_gmail_api=use_api)
    
    # Set pattern if specified
    if pattern:
        bot.posting_scheduler.set_posting_pattern(pattern)
        print(f"✅ Set posting pattern to: {pattern}")
    
    # Test Gmail connection first
    print("\n🔗 Testing Gmail connection...")
    if not bot.gmail_service.test_connection():
        print("❌ Failed to connect to Gmail. Please check your configuration.")
        return False
    
    print("✅ Gmail connection successful!")
    
    # Run email campaign
    if max_emails == 1:
        print("\n📧 Sending single email...")
        success = bot.generate_and_send_email(
            force_send=force_send,
            recipients=recipients,
            email_type=email_type
        )
        
        if success:
            print("✅ Email sent successfully!")
        else:
            print("❌ Failed to send email")
        
        return success
    else:
        print(f"\n📧 Running email campaign ({max_emails} emails)...")
        results = bot.run_email_campaign(max_emails=max_emails, force_send=force_send)
        
        print(f"\n📊 Campaign Results:")
        print(f"   ✅ Emails Sent: {results['emails_sent']}")
        print(f"   ❌ Emails Failed: {results['emails_failed']}")
        print(f"   ⏱️  Duration: {results['start_time']} to {results['end_time']}")
        
        return results['emails_sent'] > 0

def test_email_setup(recipients: List[str] = None, use_api: bool = False):
    """Test email setup and send a test email"""
    print("\n🧪 Testing Email Setup...")
    
    # Initialize bot
    bot = EmailBot(use_gmail_api=use_api)
    
    # Test connection
    print("🔗 Testing Gmail connection...")
    if not bot.gmail_service.test_connection():
        print("❌ Gmail connection failed!")
        return False
    
    print("✅ Gmail connection successful!")
    
    # Send test email
    print("📧 Sending test email...")
    success = bot.test_email_sending(test_recipients=recipients)
    
    if success:
        print("✅ Test email sent successfully!")
        print("📬 Check your inbox to confirm receipt.")
    else:
        print("❌ Test email failed to send!")
    
    return success

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Email Bot Manager - Send blog posts via Gmail')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show bot status')
    status_parser.add_argument('--api', action='store_true', help='Use Gmail API instead of SMTP')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run email bot with human-like behavior')
    run_parser.add_argument('--pattern', choices=['conservative', 'moderate', 'active'], 
                           help='Set posting pattern')
    run_parser.add_argument('--max-emails', type=int, default=1, 
                           help='Maximum number of emails to send')
    run_parser.add_argument('--recipients', nargs='+', help='Email recipients')
    run_parser.add_argument('--type', choices=['newsletter', 'blog_post', 'digest', 'announcement'],
                           help='Email type/template')
    run_parser.add_argument('--api', action='store_true', help='Use Gmail API instead of SMTP')
    
    # Force run command
    forcerun_parser = subparsers.add_parser('forcerun', help='Force run ignoring schedule')
    forcerun_parser.add_argument('--pattern', choices=['conservative', 'moderate', 'active'], 
                                help='Set posting pattern')
    forcerun_parser.add_argument('--max-emails', type=int, default=1, 
                                help='Maximum number of emails to send')
    forcerun_parser.add_argument('--recipients', nargs='+', help='Email recipients')
    forcerun_parser.add_argument('--type', choices=['newsletter', 'blog_post', 'digest', 'announcement'],
                                help='Email type/template')
    forcerun_parser.add_argument('--api', action='store_true', help='Use Gmail API instead of SMTP')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test email setup')
    test_parser.add_argument('--recipients', nargs='+', help='Test email recipients')
    test_parser.add_argument('--api', action='store_true', help='Use Gmail API instead of SMTP')
    
    # Pattern command
    pattern_parser = subparsers.add_parser('pattern', help='Set posting pattern')
    pattern_parser.add_argument('pattern', choices=['conservative', 'moderate', 'active'])
    
    # Diversity command
    diversity_parser = subparsers.add_parser('diversity', help='Show content diversity report')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show email sending history')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset posting history and diversity data')
    reset_parser.add_argument('--confirm', action='store_true', 
                             help='Confirm reset (required)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup logging
    setup_logging()
    
    try:
        if args.command == 'status':
            bot = EmailBot(use_gmail_api=args.api)
            status = bot.get_status()
            print_status(status)
            
        elif args.command == 'run':
            success = run_email_bot(
                force_send=False,
                pattern=args.pattern,
                max_emails=args.max_emails,
                recipients=args.recipients,
                email_type=args.type,
                use_api=args.api
            )
            sys.exit(0 if success else 1)
            
        elif args.command == 'forcerun':
            success = run_email_bot(
                force_send=True,
                pattern=args.pattern,
                max_emails=args.max_emails,
                recipients=args.recipients,
                email_type=args.type,
                use_api=args.api
            )
            sys.exit(0 if success else 1)
            
        elif args.command == 'test':
            success = test_email_setup(
                recipients=args.recipients,
                use_api=args.api
            )
            sys.exit(0 if success else 1)
            
        elif args.command == 'pattern':
            bot = EmailBot()
            bot.posting_scheduler.set_posting_pattern(args.pattern)
            print(f"✅ Posting pattern set to: {args.pattern}")
            
        elif args.command == 'diversity':
            bot = EmailBot()
            print_diversity_report(bot)
            
        elif args.command == 'history':
            bot = EmailBot()
            print_posting_history(bot)
            
        elif args.command == 'reset':
            if not args.confirm:
                print("❌ Reset requires --confirm flag for safety")
                print("   Use: python email_bot_manager.py reset --confirm")
                sys.exit(1)
            
            bot = EmailBot()
            bot.posting_scheduler.reset_history()
            bot.content_diversity.reset_data()
            print("✅ Reset completed - all history and diversity data cleared")
            
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logging.error(f"CLI Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
