"""
Setup script for initial configuration
"""
import os
from config.config import *


def setup_environment():
    """Create .env file with user input"""
    env_file = '.env'
    
    if os.path.exists(env_file):
        response = input(f"\n⚠️  {env_file} already exists. Overwrite? (y/n): ").lower()
        if response != 'y':
            print("Skipping .env setup")
            return
    
    print("\n" + "="*70)
    print("🔧 Job Monitoring System - Initial Setup")
    print("="*70)
    
    # Telegram Setup
    print("\n📱 Telegram Configuration")
    print("-" * 70)
    print("To get Telegram credentials:")
    print("1. Create a bot: @BotFather on Telegram")
    print("2. Get your Chat ID: @userinfobot on Telegram")
    
    telegram_enabled = input("\nEnable Telegram notifications? (y/n): ").lower() == 'y'
    
    if telegram_enabled:
        bot_token = input("Enter Telegram Bot Token: ").strip()
        chat_id = input("Enter Telegram Chat ID: ").strip()
    else:
        bot_token = "YOUR_BOT_TOKEN_HERE"
        chat_id = "YOUR_CHAT_ID_HERE"
    
    # Email Setup
    print("\n📧 Email Configuration")
    print("-" * 70)
    print("Gmail Setup:")
    print("1. Enable 2FA on your Gmail account")
    print("2. Generate App Password: https://myaccount.google.com/apppasswords")
    print("3. Use the app password below")
    
    email_enabled = input("\nEnable Email notifications? (y/n): ").lower() == 'y'
    
    if email_enabled:
        sender_email = input("Enter sender email (Gmail): ").strip()
        app_password = input("Enter Gmail app password: ").strip()
        recipient_email = input("Enter recipient email: ").strip()
    else:
        sender_email = "your_email@gmail.com"
        app_password = "your_app_password"
        recipient_email = "recipient_email@gmail.com"
    
    # API Keys Setup
    print("\n🔑 Job Board API Keys (Optional but Recommended)")
    print("-" * 70)
    print("Using official APIs provides better results and reliability.")
    print("Setup guide: See API_KEYS_SETUP.md")
    
    setup_api_keys = input("\nSetup API keys for Indeed/LinkedIn? (y/n): ").lower() == 'y'
    
    if setup_api_keys:
        indeed_publisher = input("\nEnter Indeed Publisher ID (leave blank to skip): ").strip()
        indeed_api = input("Enter Indeed API Key (leave blank to skip): ").strip()
        linkedin_api = input("Enter LinkedIn API Key (leave blank to skip): ").strip()
    else:
        indeed_publisher = ""
        indeed_api = ""
        linkedin_api = ""
    
    # Write .env file
    env_content = f"""# Telegram Configuration
TELEGRAM_BOT_TOKEN={bot_token}
TELEGRAM_CHAT_ID={chat_id}
TELEGRAM_ENABLED={'true' if telegram_enabled else 'false'}

# Email Configuration
EMAIL_SENDER={sender_email}
EMAIL_PASSWORD={app_password}
EMAIL_RECIPIENT={recipient_email}
EMAIL_ENABLED={'true' if email_enabled else 'false'}

# Indeed API Configuration
INDEED_PUBLISHER_ID={indeed_publisher if indeed_publisher else '# Not configured'}
INDEED_API_KEY={indeed_api if indeed_api else '# Not configured'}

# LinkedIn API Configuration
LINKEDIN_API_KEY={linkedin_api if linkedin_api else '# Not configured'}
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("\n✅ Setup complete!")
    print(f"📝 Configuration saved to {env_file}")
    print("\n⚠️  IMPORTANT: Add .env to .gitignore to protect sensitive data!")
    
    if setup_api_keys:
        if indeed_publisher or linkedin_api:
            print("\n✅ API Keys configured:")
            if indeed_publisher:
                print("   ✓ Indeed Publisher ID added")
            if linkedin_api:
                print("   ✓ LinkedIn API Key added")
        else:
            print("\n📌 No API keys configured - using web scraping")
            print("   You can add them later by editing .env")
    else:
        print("\n📌 Skipped API key setup")
        print("   System will use web scraping instead")
        print("   See API_KEYS_SETUP.md for later configuration")


def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'data']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def main():
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║          🚀 Job Monitoring System - Setup Wizard 🚀              ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Setup environment
    setup_environment()
    
    print("\n" + "="*70)
    print("✅ All setup steps completed!")
    print("="*70)
    print("\n📖 Next steps:")
    print("1. Review .env file with your credentials")
    print("2. Run: python main.py")
    print("3. Monitor the console for job notifications")
    print("\n💡 Tip: You can customize job keywords in config/config.py")
    print("\n")


if __name__ == "__main__":
    main()
