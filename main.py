"""
Main job monitoring application
Continuously checks for new job postings and sends notifications
"""
import sys
import time
import logging
import traceback
from datetime import datetime, timedelta
from collections import deque
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config import *  # noqa: F403,F401
from src.job_scraper import JobScraper
from src.database import JobDatabase
from src.notifications import NotificationManager

# Ensure new config vars have defaults if missing
try:
    NOTIFICATION_MODE  # noqa: F405
except NameError:
    NOTIFICATION_MODE = 'digest'
try:
    DEDUP_THRESHOLD  # noqa: F405
except NameError:
    DEDUP_THRESHOLD = 0.85

# Maximum consecutive failures before pausing
MAX_CONSECUTIVE_FAILURES = 5
FAILURE_COOLDOWN = 300  # seconds to wait after hitting max failures


class HealthMetrics:
    """Track uptime, error rates, and per-source availability."""

    def __init__(self, window_seconds: int = 3600):
        self.start_time = datetime.now()
        self._window = window_seconds
        self._errors: deque = deque()          # (timestamp, message)
        self._check_times: deque = deque()     # (timestamp, duration_sec)
        self.consecutive_failures = 0

    # --- recording ---
    def record_success(self, duration: float):
        now = datetime.now()
        self._check_times.append((now, duration))
        self.consecutive_failures = 0
        self._prune()

    def record_failure(self, message: str):
        now = datetime.now()
        self._errors.append((now, message))
        self.consecutive_failures += 1
        self._prune()

    # --- queries ---
    @property
    def uptime(self) -> timedelta:
        return datetime.now() - self.start_time

    @property
    def errors_last_hour(self) -> int:
        cutoff = datetime.now() - timedelta(seconds=self._window)
        return sum(1 for ts, _ in self._errors if ts >= cutoff)

    @property
    def avg_check_duration(self) -> float:
        if not self._check_times:
            return 0.0
        cutoff = datetime.now() - timedelta(seconds=self._window)
        recent = [d for ts, d in self._check_times if ts >= cutoff]
        return sum(recent) / len(recent) if recent else 0.0

    def should_cooldown(self) -> bool:
        return self.consecutive_failures >= MAX_CONSECUTIVE_FAILURES

    def summary(self) -> str:
        hh, rem = divmod(int(self.uptime.total_seconds()), 3600)
        mm, ss = divmod(rem, 60)
        return (
            f"Uptime {hh}h{mm:02d}m | "
            f"Errors/hr {self.errors_last_hour} | "
            f"Avg check {self.avg_check_duration:.1f}s | "
            f"Consecutive fails {self.consecutive_failures}"
        )

    def _prune(self):
        cutoff = datetime.now() - timedelta(seconds=self._window * 2)
        while self._errors and self._errors[0][0] < cutoff:
            self._errors.popleft()
        while self._check_times and self._check_times[0][0] < cutoff:
            self._check_times.popleft()


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
        self.health = HealthMetrics()
    
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
        """Check for new jobs and send notifications (self-recovering)."""
        self.check_count += 1
        
        print(f"\n{'='*70}")
        print(f"🔍 Check #{self.check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        t0 = time.time()
        try:
            # Scrape jobs from all sources
            jobs = self.scraper.scrape_all_sources(JOB_SEARCH_KEYWORDS)
            self.jobs_found += len(jobs)

            # Fuzzy deduplication
            jobs = self.scraper.deduplicate_jobs(jobs, threshold=DEDUP_THRESHOLD)

            # Relevance scoring & ranking
            jobs = self.scraper.rank_jobs(jobs, JOB_SEARCH_KEYWORDS)
            
            # Filter to only truly new jobs
            new_jobs = []
            for job in jobs:
                job_id = job.get('job_id')
                if not job_id:
                    job['job_id'] = self.scraper.generate_job_id(job)
                    job_id = job['job_id']
                if not self.database.job_exists(job_id):
                    if self.database.add_job(job):
                        new_jobs.append(job)

            # Send notifications
            if new_jobs:
                if NOTIFICATION_MODE == 'digest':
                    if self.notifications.send_digest(new_jobs):
                        for job in new_jobs:
                            self.database.mark_job_sent(job['job_id'], 'digest')
                        self.notifications_sent += len(new_jobs)
                else:
                    for job in new_jobs:
                        if self.notifications.send_job_alert(job):
                            self.database.mark_job_sent(job['job_id'], 'multi-channel')
                            self.notifications_sent += 1
            
            duration = time.time() - t0
            self.health.record_success(duration)

            # Periodic DB maintenance (every 50 checks)
            if self.check_count % 50 == 0:
                try:
                    self.database.cleanup_old_jobs(days=90)
                    self.database.vacuum()
                    self.logger.info("Periodic DB maintenance completed")
                except Exception as maint_err:
                    self.logger.warning(f"DB maintenance error (non-fatal): {maint_err}")

            # Display statistics
            db_stats = self.database.get_job_count()
            print(f"\n📊 Statistics:")
            print(f"   Total jobs in database: {sum(db_stats.values())}")
            print(f"   Pending notifications: {db_stats.get('pending', 0)}")
            print(f"   Sent notifications: {db_stats.get('sent', 0)}")
            print(f"   New jobs this check: {len(new_jobs)}")
            if new_jobs:
                top = new_jobs[0]
                print(f"   🏆 Top match: {top.get('title','')} @ {top.get('company','')} (score {top.get('relevance_score',0)})")
            print(f"   Total checks: {self.check_count}")
            print(f"   Total notifications sent: {self.notifications_sent}")
            print(f"   ⚡ {self.health.summary()}")
            
            if not new_jobs:
                print(f"   ✅ No new jobs found (already sent or no matches)")
            
        except Exception as e:
            duration = time.time() - t0
            self.health.record_failure(str(e))
            self.logger.error(f"Error during job check #{self.check_count}: {e}\n{traceback.format_exc()}")
            print(f"❌ Error during check: {e}")
            print(f"   ⚡ {self.health.summary()}")
    
    def run(self):
        """Main monitoring loop — self-recovering with cooldown."""
        self.display_banner()
        
        print(f"\n⚙️  Configuration:")
        print(f"   Check interval: {CHECK_INTERVAL} seconds")
        print(f"   Telegram enabled: {TELEGRAM_ENABLED}")
        print(f"   Email enabled: {EMAIL_ENABLED}")
        print(f"   Keywords: {', '.join(JOB_SEARCH_KEYWORDS[:3])}...")
        print(f"   Max consecutive failures before cooldown: {MAX_CONSECUTIVE_FAILURES}")
        print(f"\n⏰ Starting monitoring system...")
        print(f"📝 Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Cooldown if too many consecutive failures
                if self.health.should_cooldown():
                    self.logger.warning(
                        f"{MAX_CONSECUTIVE_FAILURES} consecutive failures — "
                        f"cooling down for {FAILURE_COOLDOWN}s"
                    )
                    print(
                        f"\n⚠️  {MAX_CONSECUTIVE_FAILURES} consecutive failures. "
                        f"Pausing {FAILURE_COOLDOWN}s before retrying..."
                    )
                    time.sleep(FAILURE_COOLDOWN)
                    self.health.consecutive_failures = 0  # reset after cooldown

                self.check_new_jobs()
                
                print(f"\n⏳ Next check in {CHECK_INTERVAL} seconds...")
                print(f"   (This is {CHECK_INTERVAL // 60} minute{'s' if CHECK_INTERVAL > 60 else ''})")
                
                time.sleep(CHECK_INTERVAL)
        
        except KeyboardInterrupt:
            self.logger.info("Monitoring system stopped by user")
            self.display_shutdown_message()
        
        except Exception as e:
            self.logger.critical(f"Fatal error in main loop: {e}\n{traceback.format_exc()}")
            print(f"\n❌ Fatal error: {e}")
            self.display_shutdown_message()
    
    def display_shutdown_message(self):
        """Display shutdown message with statistics"""
        hh, rem = divmod(int(self.health.uptime.total_seconds()), 3600)
        mm, ss = divmod(rem, 60)
        shutdown_msg = f"""

╔════════════════════════════════════════════════════════════════════╗
║                    MONITORING STOPPED                             ║
╚════════════════════════════════════════════════════════════════════╝

📊 Final Statistics:
   Total checks performed: {self.check_count}
   Total jobs found: {self.jobs_found}
   Total notifications sent: {self.notifications_sent}
   Uptime: {hh}h {mm:02d}m {ss:02d}s
   Errors in last hour: {self.health.errors_last_hour}
   Avg check duration: {self.health.avg_check_duration:.1f}s
   Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ System stopped gracefully. Thank you for using Job Monitoring System!
        """
        print(shutdown_msg)
        self.logger.info(
            f"Monitoring stopped. Checks: {self.check_count}, "
            f"Jobs: {self.jobs_found}, Notifications: {self.notifications_sent}, "
            f"Uptime: {hh}h{mm:02d}m"
        )

    def notify_if_new(self, job: dict) -> bool:
        """Send notification only if job doesn't exist yet."""
        job_id = job.get('job_id')

        if not job_id:
            job['job_id'] = self.scraper.generate_job_id(job)
            job_id = job['job_id']

        if self.database.job_exists(job_id):
            return False

        if self.database.add_job(job):
            if self.notifications.send_job_alert(job):
                self.database.mark_job_sent(job_id, 'multi-channel')
                self.notifications_sent += 1
            return True

        return False


def main():
    """Entry point"""
    system = JobMonitoringSystem()
    system.run()


if __name__ == "__main__":
    main()
