"""
Notification module for sending alerts via Telegram and Email
"""
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from datetime import datetime


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message: str) -> bool:
        """Send a message via Telegram"""
        if not self.bot_token or self.bot_token == "YOUR_BOT_TOKEN_HERE":
            print("⚠️  Telegram bot token not configured")
            return False
        
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print("✅ Telegram message sent successfully")
                return True
            else:
                print(f"❌ Telegram error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error sending Telegram message: {e}")
            return False
    
    def send_job_alert(self, job: Dict) -> bool:
        """Send formatted job alert via Telegram"""
        message = f"""
🔔 <b>New Job Found!</b>

<b>Title:</b> {job.get('title', 'N/A')}
<b>Company:</b> {job.get('company', 'N/A')}
<b>Location:</b> {job.get('location', 'N/A')}
<b>Source:</b> {job.get('source', 'N/A')}

<a href='{job.get('job_url', '#')}'>View Job</a>
"""
        return self.send_message(message)


class EmailNotifier:
    def __init__(self, sender_email: str, sender_password: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    
    def send_email(self, recipient_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send an email"""
        if not self.sender_email or self.sender_email == "your_email@gmail.com":
            print("⚠️  Email sender not configured")
            return False
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = recipient_email
            
            if is_html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, msg.as_string())
            
            print("✅ Email sent successfully")
            return True
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    def send_job_alert(self, recipient_email: str, job: Dict) -> bool:
        """Send formatted job alert via Email"""
        subject = f"🔔 New Job: {job.get('title')} at {job.get('company')}"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px;">
                    <h2 style="color: #0066cc;">New Job Opportunity Found!</h2>
                    
                    <p><strong>Title:</strong> {job.get('title', 'N/A')}</p>
                    <p><strong>Company:</strong> {job.get('company', 'N/A')}</p>
                    <p><strong>Location:</strong> {job.get('location', 'N/A')}</p>
                    <p><strong>Source:</strong> {job.get('source', 'N/A')}</p>
                    <p><strong>Posted:</strong> {job.get('posted_date', 'N/A')}</p>
                    
                    <p><strong>Description:</strong><br>
                    {job.get('description', 'No description available')[:500]}...</p>
                    
                    <p>
                        <a href='{job.get('job_url', '#')}' 
                           style='background-color: #0066cc; color: white; padding: 10px 20px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;'>
                            View Full Job
                        </a>
                    </p>
                    
                    <hr>
                    <p style="font-size: 12px; color: #999;">
                        Job Monitoring System - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(recipient_email, subject, html_body, is_html=True)


class NotificationManager:
    def __init__(self, config):
        self.config = config
        self.telegram = None
        self.email = None
        
        if config.TELEGRAM_ENABLED:
            self.telegram = TelegramNotifier(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID)
        
        if config.EMAIL_ENABLED:
            self.email = EmailNotifier(
                config.EMAIL_SENDER,
                config.EMAIL_PASSWORD,
                config.SMTP_SERVER,
                config.SMTP_PORT
            )
    
    def send_job_alert(self, job: Dict) -> bool:
        """Send job alert via all enabled channels"""
        success = False
        
        if self.telegram:
            if self.telegram.send_job_alert(job):
                success = True
        
        if self.email:
            if self.email.send_job_alert(self.config.EMAIL_RECIPIENT, job):
                success = True
        
        return success
