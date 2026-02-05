"""
Configuration settings for the Job Monitoring System
"""
import os
from datetime import datetime

# Job Search Configuration
JOB_SEARCH_KEYWORDS = [
    "computer science internship",
    "software engineer internship",
    "junior developer internship",
    "cs internship",
    "software development internship",
    "data science internship",
    "machine learning internship",
    "web developer internship",
]

# Job Search Sites (can add more in the future)
JOB_SITES = {
    "linkedin": "https://www.linkedin.com/jobs/search/?keywords=",
    "indeed": "https://www.indeed.com/jobs?q=",
    "glassdoor": "https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=",
    "github_jobs": "https://jobs.github.com/positions.json?description=",
}

# Check Interval (in seconds)
CHECK_INTERVAL = 60  # 1 minute

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")
TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "true").lower() == "true"

# Email Configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "your_email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_app_password")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "recipient_email@gmail.com")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "true").lower() == "true"

# SMTP Server Configuration (Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Database Configuration
DATABASE_FILE = "data/jobs_database.db"
JOBS_CACHE_FILE = "data/sent_jobs.json"

# Logging Configuration
LOG_FILE = "logs/job_monitor.log"
LOG_LEVEL = "INFO"

# Search Filters
LOCATION_FILTER = "Remote"  # Can be "Remote", "USA", "Canada", etc.
EMPLOYMENT_TYPE = ["Internship", "Entry Level"]  # Types of positions to search

# Timeout Configuration (in seconds)
REQUEST_TIMEOUT = 10
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds

# API Keys for job boards (if needed)
LINKEDIN_API_KEY = os.getenv("LINKEDIN_API_KEY", "")
INDEED_API_KEY = os.getenv("INDEED_API_KEY", "")
INDEED_PUBLISHER_ID = os.getenv("INDEED_PUBLISHER_ID", "")

# LinkedIn API Configuration
LINKEDIN_API_BASE_URL = "https://api.linkedin.com/v2"
LINKEDIN_USE_API = bool(LINKEDIN_API_KEY)

# Indeed API Configuration
INDEED_API_BASE_URL = "https://api.indeed.com/ads/apisearch"
INDEED_USE_API = bool(INDEED_API_KEY and INDEED_PUBLISHER_ID)

# Job Sources to Search (enable/disable)
SEARCH_GITHUB_JOBS = os.getenv("SEARCH_GITHUB_JOBS", "true").lower() == "true"
SEARCH_INDEED = os.getenv("SEARCH_INDEED", "true").lower() == "true"
SEARCH_LINKEDIN = os.getenv("SEARCH_LINKEDIN", "true").lower() == "true"
SEARCH_STACKOVERFLOW = os.getenv("SEARCH_STACKOVERFLOW", "true").lower() == "true"

# Demo Mode (for testing without external APIs)
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

print("""
╔════════════════════════════════════════════════════════════════════╗
║           Job & Internship Monitoring System                       ║
║           Configuration Loaded Successfully                        ║
╚════════════════════════════════════════════════════════════════════╝
""")
