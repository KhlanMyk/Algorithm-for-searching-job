"""
Example script showing how to use the Job Monitoring System
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config import JOB_SEARCH_KEYWORDS, TELEGRAM_ENABLED, EMAIL_ENABLED
from src.job_scraper import JobScraper
from src.database import JobDatabase


def example_scrape():
    """Example: Scrape jobs once without notifications"""
    print("\n" + "="*70)
    print("📚 Example: Single Job Search Without Notifications")
    print("="*70 + "\n")
    
    scraper = JobScraper()
    
    # Search for jobs
    print("🔍 Searching for jobs...")
    jobs = scraper.scrape_all_sources(JOB_SEARCH_KEYWORDS[:2])  # Use first 2 keywords
    
    # Display results
    print(f"\n✅ Found {len(jobs)} jobs:\n")
    for i, job in enumerate(jobs[:5], 1):  # Show first 5
        print(f"{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   URL: {job['job_url']}")
        print(f"   Source: {job['source']}\n")


def example_database():
    """Example: Database operations"""
    print("\n" + "="*70)
    print("📚 Example: Database Operations")
    print("="*70 + "\n")
    
    db = JobDatabase()
    
    # Sample job
    sample_job = {
        'job_id': 'example_123',
        'title': 'Software Engineer Intern',
        'company': 'Tech Company',
        'location': 'San Francisco',
        'job_url': 'https://example.com/job/123',
        'description': 'Work on exciting projects',
        'source': 'Example',
        'posted_date': '2026-01-27'
    }
    
    # Add job
    print("Adding sample job to database...")
    if db.add_job(sample_job):
        print("✅ Job added successfully")
    else:
        print("⚠️  Job already exists in database")
    
    # Check if exists
    exists = db.job_exists('example_123')
    print(f"Job exists in database: {exists}")
    
    # Get statistics
    stats = db.get_job_count()
    print(f"\nDatabase statistics:")
    for status, count in stats.items():
        print(f"  {status}: {count} jobs")


def example_notification_config():
    """Example: Check notification configuration"""
    print("\n" + "="*70)
    print("📚 Example: Notification Configuration")
    print("="*70 + "\n")
    
    print("Current configuration:")
    print(f"  Telegram enabled: {TELEGRAM_ENABLED}")
    print(f"  Email enabled: {EMAIL_ENABLED}")
    print(f"  Search keywords: {', '.join(JOB_SEARCH_KEYWORDS[:3])}...")
    
    print("\n💡 To enable notifications:")
    print("  1. Run: python setup.py")
    print("  2. Follow the prompts")
    print("  3. Restart the monitoring system")


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║          Job Monitoring System - Examples                         ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    print("\nChoose an example to run:")
    print("  1. Search for jobs (no notifications)")
    print("  2. Database operations")
    print("  3. Check notification config")
    print("  0. Exit")
    
    choice = input("\nEnter your choice (0-3): ").strip()
    
    if choice == "1":
        example_scrape()
    elif choice == "2":
        example_database()
    elif choice == "3":
        example_notification_config()
    else:
        print("Exiting...")
