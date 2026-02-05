# Project Structure & Architecture

## 📁 Complete File Structure

```
Algorithm for Searching a job/
│
├── 🚀 MAIN ENTRY POINTS
│   ├── main.py                    # Start monitoring (run this!)
│   ├── setup.py                   # Initial configuration wizard
│   ├── examples.py                # Test examples & demos
│   └── quickstart.sh              # Automated setup script
│
├── 📖 DOCUMENTATION
│   ├── README.md                  # Complete guide
│   ├── GETTING_STARTED.md         # Quick start guide (start here!)
│   ├── ARCHITECTURE.md            # This file
│   └── .github/
│       └── copilot-instructions.md # VS Code setup notes
│
├── ⚙️ CONFIGURATION
│   ├── config/
│   │   └── config.py              # All settings & constants
│   ├── .env.example               # Example credentials template
│   ├── requirements.txt           # Python dependencies
│   └── .gitignore                 # Git ignore rules
│
├── 🔧 SOURCE CODE (src/)
│   ├── job_scraper.py            # Web scraping for jobs
│   │   ├── JobScraper             # Main scraper class
│   │   ├── scrape_github_jobs()   # GitHub Jobs API
│   │   ├── scrape_indeed_snapshot() # Indeed scraper
│   │   └── scrape_all_sources()   # Master scraper
│   │
│   ├── notifications.py           # Telegram & Email notifications
│   │   ├── TelegramNotifier       # Telegram bot sender
│   │   ├── EmailNotifier          # Gmail sender
│   │   └── NotificationManager    # Unified notifier
│   │
│   └── database.py                # SQLite job tracking
│       ├── JobDatabase            # Database manager
│       ├── add_job()              # Add new job
│       ├── job_exists()           # Check duplicates
│       ├── mark_job_sent()        # Track notifications
│       └── get_job_count()        # Get statistics
│
├── 📊 DATA DIRECTORIES (created at runtime)
│   ├── data/
│   │   ├── jobs_database.db       # SQLite database (auto-created)
│   │   └── sent_jobs.json         # Job cache (optional)
│   │
│   └── logs/
│       └── job_monitor.log        # Activity log (auto-created)
│
└── 🔐 RUNTIME FILES
    └── .env                       # Your credentials (auto-created by setup.py)
```

## 🔄 System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     JOB MONITORING SYSTEM                        │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   main.py        │ ◄── START HERE
                    │   (Main Loop)    │
                    └──────────────────┘
                               │
                               ▼ (Every 1 minute)
                    ┌──────────────────────┐
                    │  job_scraper.py      │
                    │  Search all sites    │
                    │  - GitHub Jobs       │
                    │  - Indeed            │
                    │  - Glassdoor         │
                    └──────────────────────┘
                               │
                               ▼
                  Found jobs? ┌──────┐
                    ┌─────────┤ YES  │
                    │         └──────┘
                    │             │
                    ▼             ▼
           ┌────────────────┐  ┌──────────────────┐
           │  database.py   │  │ Check if new job │
           │  SQLite DB     │  │ (prevent dups)   │
           │  Stores all    │  └──────────────────┘
           │  jobs          │         │
           └────────────────┘         ▼
                    ▲         ┌──────────────┐
                    │         │ New job?     │
                    │         └──────────────┘
                    │               │
                    │ No  ┌─────────┘
                    │     │ Yes
                    │     ▼
                    │  ┌────────────────────────────┐
                    │  │ notifications.py           │
                    │  │ Send via:                  │
                    │  │ - Telegram Bot             │
                    │  │ - Gmail (HTML email)       │
                    │  └────────────────────────────┘
                    │               │
                    │               ▼
                    │  ┌────────────────────────────┐
                    │  │ User Receives:             │
                    │  │ 📱 Telegram message        │
                    │  │ 📧 Email with job details  │
                    │  │ 🔗 Clickable job link      │
                    │  └────────────────────────────┘
                    │               │
                    │               ▼
                    └───────────────────────────────
                         Mark job as sent
                         Log activity
                         Update database

                    LOOP REPEATS EVERY 60 SECONDS
```

## 📊 Database Schema

```sql
-- Jobs Table
CREATE TABLE jobs (
    id                INTEGER PRIMARY KEY,
    job_id            TEXT UNIQUE,        -- MD5 hash of title+company+url
    title             TEXT,               -- Job title
    company           TEXT,               -- Company name
    location          TEXT,               -- Job location
    job_url           TEXT,               -- Link to job posting
    description       TEXT,               -- Job description
    source            TEXT,               -- Where found (GitHub, Indeed, etc)
    posted_date       TEXT,               -- When job was posted
    found_date        TEXT,               -- When we found it
    sent_date         TEXT,               -- When notification sent
    notification_type TEXT,               -- telegram, email, both
    status            TEXT DEFAULT 'pending'  -- pending, sent, archived
);

-- Notifications Table
CREATE TABLE notifications (
    id                  INTEGER PRIMARY KEY,
    job_id              TEXT,              -- Foreign key to jobs
    notification_method TEXT,              -- telegram, email, sms
    sent_date           TEXT,              -- When sent
    status              TEXT,              -- sent, failed, pending
    FOREIGN KEY (job_id) REFERENCES jobs
);
```

## 🔌 Module Dependencies

```
main.py
├── config.config          (configuration)
├── job_scraper.JobScraper (fetch jobs)
├── database.JobDatabase   (store/check jobs)
└── notifications.NotificationManager
    ├── TelegramNotifier   (send Telegram)
    └── EmailNotifier      (send email)

setup.py
├── config.config
└── os (environment)

examples.py
├── config.config
├── job_scraper.JobScraper
└── database.JobDatabase
```

## ⚙️ Configuration Flow

```
.env (User Credentials)
  │
  ├─→ TELEGRAM_BOT_TOKEN
  ├─→ TELEGRAM_CHAT_ID
  ├─→ EMAIL_SENDER
  ├─→ EMAIL_PASSWORD
  ├─→ EMAIL_RECIPIENT
  └─→ TELEGRAM_ENABLED, EMAIL_ENABLED
       │
       ▼
   config.py (Loaded at startup)
       │
       ├─→ JOB_SEARCH_KEYWORDS
       ├─→ CHECK_INTERVAL (60 seconds)
       ├─→ JOB_SITES (GitHub, Indeed, Glassdoor)
       ├─→ LOCATION_FILTER
       ├─→ EMPLOYMENT_TYPE
       └─→ SMTP_SERVER, SMTP_PORT
            │
            ▼
        main.py & modules
```

## 🔐 Security Architecture

```
Sensitive Data Flow:
├── User Input (setup.py)
│   └─→ .env file (gitignored)
│
├── Gmail Password
│   ├─ Never logged
│   ├─ Only used for SMTP authentication
│   └─ Stored only in .env
│
├── Telegram Bot Token
│   ├─ Only used for API calls
│   ├─ Stored only in .env
│   └─ Chat ID used for sending messages
│
└── Database (SQLite)
    ├─ Stores jobs (no credentials)
    ├─ Stores notification history
    └─ Can be backed up or deleted safely
```

## 📈 Scalability Notes

Current implementation can handle:
- ✅ 1-minute check intervals
- ✅ Multiple job sources simultaneously
- ✅ Hundreds of jobs per day
- ✅ Dual notification channels
- ✅ Continuous operation (days/weeks)

Limitations:
- ⚠️ Telegram rate limit: ~30 messages/sec
- ⚠️ Gmail rate limit: ~50 emails/hour
- ⚠️ Database size grows over time
- ⚠️ Web scraping can be slow

Solutions:
- Archive old jobs to separate database
- Add job filtering to reduce notifications
- Use bulk email services
- Implement request throttling

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-27 | Initial release |
| | | - Job scraping (GitHub Jobs, Indeed, Glassdoor) |
| | | - Telegram notifications |
| | | - Email notifications |
| | | - SQLite database |
| | | - Configuration system |
| | | - Setup wizard |

## 🚀 Future Enhancements

```
Phase 2 - Features:
├── Web dashboard for viewing jobs
├── Advanced job filtering (salary, company, etc)
├── Resume parsing and matching
└── Job application tracking

Phase 3 - Integrations:
├── Slack notifications
├── Discord bot
├── LinkedIn API integration
├── Indeed API integration
└── Google Calendar sync

Phase 4 - Intelligence:
├── ML job recommendations
├── Duplicate job detection
├── Salary prediction
├── Company reviews integration
└── Interview preparation tips
```

---

**System Status**: ✅ Production Ready

For questions or issues, check README.md or GETTING_STARTED.md
