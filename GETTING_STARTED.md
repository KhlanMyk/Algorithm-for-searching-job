# Getting Started - Job Monitoring System

## 🎯 What You Have

A complete Python application that:
- ✅ Checks job boards every **1 minute**
- ✅ Searches for **Computer Science internships** and entry-level positions
- ✅ Sends notifications via **Telegram** and **Email**
- ✅ Tracks jobs to prevent **duplicate notifications**
- ✅ Logs all activity for troubleshooting

## 📦 What's Included

```
Algorithm for Searching a job/
├── main.py                 ← Start here to run the system
├── setup.py               ← Configure your credentials
├── quickstart.sh          ← Automated setup script
├── examples.py            ← See how to use the modules
├── requirements.txt       ← Python dependencies to install
├── README.md             ← Complete documentation
├── config/
│   └── config.py         ← Customize settings
├── src/
│   ├── job_scraper.py    ← Searches job boards
│   ├── notifications.py  ← Sends Telegram & Email
│   └── database.py       ← Tracks jobs
└── data/                 ← Created automatically
```

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
cd "/Users/mykytakhlan/Desktop/Algorithm for Searching a job"
pip install -r requirements.txt
```

### Step 2: Configure Credentials
```bash
python setup.py
```

You'll be asked for:
- **Telegram Bot Token** (get from @BotFather on Telegram)
- **Telegram Chat ID** (get from @userinfobot)
- **Gmail address** and **App Password** (from myaccount.google.com/apppasswords)

### Step 3: Start Monitoring
```bash
python main.py
```

The system will now check every minute and send notifications! 🎉

## 📱 Getting Telegram Credentials (2 minutes)

1. Open Telegram app
2. Search for **@BotFather**
3. Send `/newbot`
4. Follow prompts to create bot
5. Copy your **Bot Token** (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
6. Search for **@userinfobot**
7. Send any message to get your **Chat ID** (a number like: `987654321`)

## 📧 Getting Gmail App Password (3 minutes)

1. Go to [Google Account](https://myaccount.google.com)
2. Click **Security** on the left
3. Enable **2-Step Verification** (if not done)
4. Scroll to **App passwords**
5. Select "Mail" and "Windows Computer"
6. Google generates a 16-character password
7. Use this password (NOT your Gmail password)

## 🛠️ Customizing

### Change Job Keywords
Edit `config/config.py`:
```python
JOB_SEARCH_KEYWORDS = [
    "your keyword 1",
    "your keyword 2",
]
```

### Change Check Interval
Edit `config/config.py`:
```python
CHECK_INTERVAL = 300  # Check every 5 minutes instead of 1
```

### Enable/Disable Notifications
Edit `.env` file:
```
TELEGRAM_ENABLED=true    # or false
EMAIL_ENABLED=true       # or false
```

## 🧪 Test Without Running

Run examples to test:
```bash
python examples.py
```

This lets you:
- Search jobs once without continuous monitoring
- Test database operations
- Check your configuration

## 📊 What You'll See

When you run `python main.py`:

```
🔍 Check #1 - 2026-01-27 14:30:45
=====================================
✅ Found 12 jobs from GitHub Jobs for 'computer science internship'

📊 Statistics:
   Total jobs in database: 5
   Pending notifications: 0
   Sent notifications: 5
   New jobs this check: 3
   Total checks: 1
   Total notifications sent: 3

⏳ Next check in 60 seconds...
```

You'll get notifications in:
- 📱 **Telegram** - Instant messages with job details
- 📧 **Email** - HTML-formatted emails with clickable links

## 🛑 Stopping

Press **Ctrl+C** in the terminal to stop gracefully.

## 📊 Where Data is Stored

- **Database**: `data/jobs_database.db` - All jobs found
- **Logs**: `logs/job_monitor.log` - Activity log
- **Config**: `.env` - Your credentials (never commit this!)

## ⚠️ Important Notes

1. **Keep `.env` safe** - Contains your private credentials
2. **Never share credentials** - Bot token, passwords, chat IDs
3. **Gmail requires 2FA** - App passwords only work with 2-Step Verification
4. **Respect rate limits** - Don't set check interval too low

## 🚀 Advanced Setup

### Run as Background Service

**macOS/Linux:**
```bash
nohup python main.py > logs/background.log 2>&1 &
```

**Using screen:**
```bash
screen -S job_monitor -d -m python main.py
```

### Run on Startup

Add to crontab:
```bash
crontab -e

# Add this line:
@reboot cd /path/to/project && python main.py >> logs/startup.log 2>&1
```

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Telegram not working | Verify bot token in .env |
| Email not sending | Check Gmail app password + 2FA enabled |
| No jobs found | Check internet, verify keywords, check logs |
| Database errors | Delete `data/jobs_database.db` and restart |
| Python not found | Install Python 3.8+ |

## 📚 More Information

- **README.md** - Complete documentation
- **config/config.py** - All configuration options
- **logs/job_monitor.log** - Detailed activity logs
- **examples.py** - Code examples

## 🎓 How It Works

1. **Scraper** finds jobs on GitHub Jobs, Indeed, Glassdoor
2. **Database** checks if job is new (by title+company+URL hash)
3. **Notifier** sends jobs via Telegram & Email
4. **Logger** records everything for debugging
5. **Repeat** every 60 seconds

## 💡 Tips

- Run **examples.py** to test without continuous monitoring
- Check **logs/job_monitor.log** for detailed errors
- Customize keywords for better results
- Run multiple instances with different keywords
- Archive old database periodically (it grows over time)

---

**Ready to start?**

```bash
python setup.py    # Configure
python main.py     # Run!
```

Happy job hunting! 🚀
