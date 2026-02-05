# 🔔 Job & Internship Monitoring System

An automated Python system that monitors job boards and sends real-time notifications via **Telegram** and **Email** for Computer Science internship and entry-level positions.

## ✨ Features

- 🔍 **Automated Monitoring** - Checks job sites every 1 minute (configurable)
- 🎯 **Smart Filtering** - Searches for Computer Science jobs and internships
- 📱 **Telegram Notifications** - Instant alerts via Telegram bot
- 📧 **Email Alerts** - HTML-formatted job details via email
- 💾 **Database Tracking** - Prevents duplicate notifications
- 🌐 **Multi-Source** - Searches GitHub Jobs, Indeed, and Glassdoor
- ⚙️ **Easy Configuration** - Simple setup wizard for credentials
- 📊 **Statistics** - Tracks jobs found and notifications sent

## 📋 Prerequisites

- Python 3.8 or higher
- macOS, Linux, or Windows
- Telegram account (for Telegram notifications)
- Gmail account (for email notifications)

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
cd "/Users/mykytakhlan/Desktop/Algorithm for Searching a job"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Your Credentials

Run the setup wizard:

```bash
python setup.py
```

The wizard will prompt you for:
- **Telegram Bot Token** (from @BotFather)
- **Telegram Chat ID** (from @userinfobot)
- **Gmail address** and **App Password**
- **Recipient email address**

This creates a `.env` file with your credentials.

### 4. Start the Monitoring System

```bash
python main.py
```

You'll see:
- Job search progress
- New jobs found
- Notifications sent
- System statistics

## 🔐 Getting Credentials

### Telegram Credentials

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the prompts to create a new bot
4. Copy your **Bot Token**
5. Open Telegram and search for **@userinfobot**
6. Send any message to get your **Chat ID**

### Gmail App Password

1. Go to [Google Account Settings](https://myaccount.google.com)
2. Enable **2-Step Verification** if not already done
3. Go to **App passwords** section
4. Select "Mail" and "Windows Computer" (or your device)
5. Google will generate a 16-character password
6. Use this password in setup (NOT your Gmail password)

## 📁 Project Structure

```
Algorithm for Searching a job/
├── main.py                 # Main application entry point
├── setup.py               # Initial configuration wizard
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment file
├── .gitignore            # Git ignore rules
├── config/
│   └── config.py         # Configuration settings
├── src/
│   ├── database.py       # SQLite database management
│   ├── job_scraper.py    # Web scraping module
│   └── notifications.py  # Telegram & Email sender
├── data/                 # Database and cache storage
├── logs/                 # Application logs
└── README.md             # This file
```

## ⚙️ Configuration

Edit `config/config.py` to customize:

```python
# Job search keywords
JOB_SEARCH_KEYWORDS = [
    "computer science internship",
    "software engineer internship",
    # Add more keywords...
]

# Check interval in seconds
CHECK_INTERVAL = 60  # 1 minute

# Job locations to filter
LOCATION_FILTER = "Remote"  # or "USA", "Canada", etc.

# Employment types
EMPLOYMENT_TYPE = ["Internship", "Entry Level"]
```

## 📊 How It Works

1. **Startup** → Application initializes database and connections
2. **Job Search** → Every 1 minute, searches configured job sites
3. **Duplicate Check** → Compares with database to avoid duplicates
4. **Notification** → Sends new jobs via Telegram and Email
5. **Logging** → Records activity in `logs/job_monitor.log`
6. **Repeat** → Continues until manually stopped

## 🛑 Stopping the Application

Press **Ctrl+C** in the terminal. You'll see:
- Total checks performed
- Total jobs found
- Total notifications sent
- Graceful shutdown message

## 🐛 Troubleshooting

### "Telegram bot token not configured"
- Check your `.env` file has the correct `TELEGRAM_BOT_TOKEN`
- Verify token format (usually starts with numbers and contains colons)

### "Email not sent"
- Verify Gmail app password (not regular Gmail password)
- Check 2-Step Verification is enabled on Gmail
- Confirm recipient email is correct

### No jobs found
- Check internet connection
- Verify keywords match current job listings
- Try modifying keywords in `config/config.py`
- Check `logs/job_monitor.log` for errors

### Database errors
- Delete `data/jobs_database.db` to reset
- System will recreate it on next run

## 📝 Log Files

All activity is logged to `logs/job_monitor.log`:
- Job searches
- New jobs found
- Notifications sent
- Errors and warnings

View logs:
```bash
tail -f logs/job_monitor.log
```

## 🔄 Updating Job Keywords

Edit `config/config.py`:

```python
JOB_SEARCH_KEYWORDS = [
    "your keyword 1",
    "your keyword 2",
    "your keyword 3",
    # ...
]
```

Restart the application for changes to take effect.

## 🌐 Supported Job Sources

Currently searches:
- ✅ **GitHub Jobs** - Developer-focused positions
- 🔄 **Indeed** - General job board (limited by dynamic content)
- 📋 **Glassdoor** - Company reviews and jobs
- (More sources can be added)

## 💡 Tips & Tricks

### Running in Background (macOS/Linux)

```bash
# Using nohup
nohup python main.py > app.log 2>&1 &

# Using screen
screen -S job_monitor python main.py

# Using tmux
tmux new-session -d -s job_monitor 'python main.py'
```

### Running on Startup

Add to your system's crontab:
```bash
crontab -e

# Add this line:
@reboot cd /path/to/project && python main.py >> logs/startup.log 2>&1
```

### Customizing Email Template

Edit the email HTML in `src/notifications.py` `EmailNotifier.send_job_alert()` method.

### Adjusting Check Frequency

Edit `CHECK_INTERVAL` in `config/config.py`:
```python
CHECK_INTERVAL = 300  # Check every 5 minutes
CHECK_INTERVAL = 30   # Check every 30 seconds
```

## 📈 Performance Considerations

- **Database grows over time** - Periodically archive old records
- **Email rate limits** - Gmail allows ~50 emails per hour
- **Telegram API limits** - Generally unlimited for personal bots
- **Web scraping** - Be respectful, don't scrape too aggressively

## 🔒 Security Notes

- **Never commit `.env` file** to Git (already in `.gitignore`)
- Use **App Passwords** for Gmail, not your main password
- Keep bot tokens confidential
- Review email recipients regularly

## 📄 License

This project is open source and available for personal use.

## 🤝 Contributing

Feel free to fork, modify, and improve this project!

### Potential Enhancements
- Add more job board sources
- Implement filtering by salary
- Add Discord notifications
- Create web dashboard
- Add Slack integration
- Schedule job searches by time of day

## 📞 Support

For issues:
1. Check `logs/job_monitor.log` for error messages
2. Verify credentials in `.env` file
3. Test internet connection
4. Review README troubleshooting section

## 🎯 Future Roadmap

- [ ] Web dashboard for job browsing
- [ ] Resume matching with jobs
- [ ] LinkedIn integration
- [ ] Slack notifications
- [ ] Discord bot
- [ ] Job statistics and analytics
- [ ] Mobile app
- [ ] Advanced filtering (salary, company, etc.)

---

**Made with ❤️ for Computer Science students seeking opportunities**

Happy job hunting! 🚀
