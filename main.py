"""
Main job monitoring application
Continuously checks for new job postings and sends notifications
"""
import sys
import time
import logging
from datetime import datetime
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config import *
from src.job_scraper import JobScraper
from src.database import JobDatabase
from src.notifications import NotificationManager


class JobMonitoringSystem:
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        self.scraper = JobScraper(timeout=REQUEST_TIMEOUT)
        self.database = JobDatabase(DATABASE_FILE)
        
        # Import config module to pass to NotificationManager
        import config.config as config_module
        self.notifications = NotificationManager(config_module)
        
        self.check_count = 0
        self.jobs_found = 0
        self.notifications_sent = 0
    
    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=LOG_LEVEL,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    def display_banner(self):
        """Display application banner"""
        banner = """
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║          🔔 JOB & INTERNSHIP MONITORING SYSTEM 🔔                ║
║                                                                    ║
║  Automated job search for Computer Science positions              ║
║  Notifications via Telegram & Email                               ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_new_jobs(self):
        """Check for new jobs and send notifications"""
        self.check_count += 1
        
        print(f"\n{'='*70}")
        print(f"🔍 Check #{self.check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        try:
            # Scrape jobs from all sources
            jobs = self.scraper.scrape_all_sources(JOB_SEARCH_KEYWORDS)
            self.jobs_found += len(jobs)
            
            # Process each job
            new_jobs_count = 0
            for job in jobs:
                job_id = job.get('job_id')
                
                # Check if job is already in database
                if not self.database.job_exists(job_id):
                    # Add to database
                    if self.database.add_job(job):
                        new_jobs_count += 1
                        
                        # Send notification
                        if self.notifications.send_job_alert(job):
                            self.database.mark_job_sent(job_id, 'multi-channel')
                            self.notifications_sent += 1
            
            # Display statistics
            db_stats = self.database.get_job_count()
            print(f"\n📊 Statistics:")
            print(f"   Total jobs in database: {sum(db_stats.values())}")
            print(f"   Pending notifications: {db_stats.get('pending', 0)}")
            print(f"   Sent notifications: {db_stats.get('sent', 0)}")
            print(f"   New jobs this check: {new_jobs_count}")
            print(f"   Total checks: {self.check_count}")
            print(f"   Total notifications sent: {self.notifications_sent}")
            
            if new_jobs_count == 0:
                print(f"   ✅ No new jobs found (already sent or no matches)")
            
        except Exception as e:
            self.logger.error(f"Error during job check: {e}")
            print(f"❌ Error during check: {e}")
    
    def run(self):
        """Main monitoring loop"""
        self.display_banner()
        
        print(f"\n⚙️  Configuration:")
        print(f"   Check interval: {CHECK_INTERVAL} seconds")
        print(f"   Telegram enabled: {TELEGRAM_ENABLED}")
        print(f"   Email enabled: {EMAIL_ENABLED}")
        print(f"   Keywords: {', '.join(JOB_SEARCH_KEYWORDS[:3])}...")
        print(f"\n⏰ Starting monitoring system...")
        print(f"📝 Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.check_new_jobs()
                
                print(f"\n⏳ Next check in {CHECK_INTERVAL} seconds...")
                print(f"   (This is {CHECK_INTERVAL // 60} minute{'s' if CHECK_INTERVAL > 60 else ''})")
                
                time.sleep(CHECK_INTERVAL)
        
        except KeyboardInterrupt:
            self.logger.info("Monitoring system stopped by user")
            self.display_shutdown_message()
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            print(f"\n❌ Unexpected error: {e}")
    
    def display_shutdown_message(self):
        """Display shutdown message with statistics"""
        shutdown_msg = f"""

╔════════════════════════════════════════════════════════════════════╗
║                    MONITORING STOPPED                             ║
╚════════════════════════════════════════════════════════════════════╝

📊 Final Statistics:
   Total checks performed: {self.check_count}
   Total jobs found: {self.jobs_found}
   Total notifications sent: {self.notifications_sent}
   Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ System stopped gracefully. Thank you for using Job Monitoring System!
        """
        print(shutdown_msg)
        self.logger.info(f"Monitoring stopped. Checks: {self.check_count}, Jobs found: {self.jobs_found}, Notifications sent: {self.notifications_sent}")


def main():
    """Entry point"""
    system = JobMonitoringSystem()
    system.run()


if __name__ == "__main__":
    main()
