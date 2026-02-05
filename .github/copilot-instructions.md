<!-- 
Job Monitoring System - Custom Instructions for VS Code
This file provides workspace-specific setup and development guidelines.
-->

## Setup Checklist

- [x] Project directory structure created
- [x] Core modules implemented (scraper, notifications, database)
- [x] Configuration system with .env support
- [x] Setup wizard for credentials
- [x] Requirements.txt with dependencies
- [x] Complete README documentation
- [ ] Install dependencies
- [ ] Run setup.py configuration
- [ ] Start main.py

## Project Overview

**Job & Internship Monitoring System** - Automated Python application that:
- Monitors job boards every 1 minute
- Searches for CS internships and entry-level positions
- Sends notifications via Telegram and Email
- Tracks jobs in SQLite database to prevent duplicates

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials
python setup.py

# 3. Start monitoring
python main.py
```

## File Organization

- **main.py** - Entry point, main monitoring loop
- **setup.py** - Initial configuration wizard
- **config/config.py** - Configuration settings and constants
- **src/job_scraper.py** - Web scraping module for job boards
- **src/notifications.py** - Telegram and Email notification classes
- **src/database.py** - SQLite database management
- **.env** - Sensitive credentials (auto-created by setup.py)
- **requirements.txt** - Python package dependencies
- **README.md** - Complete user documentation

## Dependencies

- requests - HTTP requests for web scraping
- beautifulsoup4 - HTML parsing
- python-telegram-bot - Telegram API
- python-dotenv - Environment variable management

## Key Features

1. **Multi-source job monitoring** - GitHub Jobs, Indeed, Glassdoor
2. **Dual notifications** - Telegram bot + HTML emails
3. **Smart deduplication** - SQLite database prevents duplicate alerts
4. **Configurable keywords** - Edit search terms in config.py
5. **Detailed logging** - All activity logged to logs/job_monitor.log
6. **Statistics tracking** - Counts jobs found and notifications sent

## Development Notes

- System runs indefinitely until Ctrl+C is pressed
- Check interval is 60 seconds (configurable)
- Jobs are uniquely identified by MD5 hash of title+company+URL
- Email requires Gmail app password (not main password)
- Telegram requires bot token and chat ID

## Troubleshooting

- Telegram not working? Verify bot token in .env
- Email not sending? Check 2FA enabled and app password correct
- No jobs found? Check keywords and internet connection
- Database issues? Delete data/jobs_database.db and restart

---
