#!/usr/bin/env python3
"""
User Configuration System for HerShield
Allows users to set up their personal emergency details
"""

import json
import os
from pathlib import Path

class UserConfig:
    """Manages user configuration and settings"""

    def __init__(self, config_file="user_config.json"):
        self.config_file = Path("data") / config_file
        self.config_file.parent.mkdir(exist_ok=True)
        self.config = self.load_config()

    def load_config(self):
        """Load user configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("[WARN] Corrupted config file, creating new one")
                return self.get_default_config()
        return self.get_default_config()

    def get_default_config(self):
        """Get default configuration structure"""
        return {
            "user_info": {
                "name": "",
                "email": "",
                "phone": "",
                "emergency_contacts": [],
                "medical_info": {
                    "blood_type": "",
                    "allergies": [],
                    "medications": [],
                    "conditions": []
                }
            },
            "alert_settings": {
                "messaging_service": "twilio",  # twilio, email, telegram, etc.
                "twilio_config": {
                    "sid": "",
                    "auth_token": "",
                    "phone_number": "",
                    "messaging_service_sid": ""
                },
                "email_config": {
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "use_tls": True
                },
                "telegram_config": {
                    "bot_token": "",
                    "chat_ids": []
                },
                "discord_config": {
                    "webhook_url": "",
                    "bot_token": "",
                    "channel_id": ""
                },
                "sms_config": {
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "use_tls": True
                }
            },
            "location_settings": {
                "enable_gps": True,
                "location_accuracy": "high",
                "share_location": True
            },
            "voice_settings": {
                "keywords": ["help", "save me", "emergency"],
                "sensitivity": "medium",
                "wake_word": "hey shield"
            }
        }

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def setup_user_profile(self):
        """Interactive user profile setup"""
        print("\n=== HER SHIELD USER SETUP ===")
        print("Let's set up your emergency profile\n")

        # Basic info
        print("📋 BASIC INFORMATION")
        self.config["user_info"]["name"] = input("Your full name: ").strip()
        self.config["user_info"]["email"] = input("Your email address: ").strip()
        self.config["user_info"]["phone"] = input("Your phone number (with country code): ").strip()

        # Emergency contacts
        print("\n🚨 EMERGENCY CONTACTS")
        print("Add up to 5 emergency contacts (press Enter when done)")
        contacts = []
        for i in range(5):
            contact = input(f"Emergency contact {i+1} (name: +1234567890): ").strip()
            if not contact:
                break
            contacts.append(contact)
        self.config["user_info"]["emergency_contacts"] = contacts

        # Medical info (optional)
        print("\n🏥 MEDICAL INFORMATION (Optional)")
        if input("Add medical information? (y/n): ").lower().startswith('y'):
            self.config["user_info"]["medical_info"]["blood_type"] = input("Blood type: ").strip()
            allergies = input("Allergies (comma-separated): ").strip()
            if allergies:
                self.config["user_info"]["medical_info"]["allergies"] = [a.strip() for a in allergies.split(',')]
            medications = input("Current medications (comma-separated): ").strip()
            if medications:
                self.config["user_info"]["medical_info"]["medications"] = [m.strip() for m in medications.split(',')]
            conditions = input("Medical conditions (comma-separated): ").strip()
            if conditions:
                self.config["user_info"]["medical_info"]["conditions"] = [c.strip() for c in conditions.split(',')]

        self.save_config()
        print(f"\n✅ Profile saved to {self.config_file}")
        return True

    def setup_messaging(self):
        """Setup messaging service configuration"""
        print("\n📱 ALERT MESSAGING SETUP")
        print("Choose how you want to send/receive alerts:\n")

        print("1. Twilio SMS (requires paid account)")
        print("2. Email alerts")
        print("3. Telegram Bot")
        print("4. Discord (free alternative to SMS)")
        print("5. Free SMS via Email (Indian carriers supported)")
        print("6. Push notifications (future)")
        print("7. Multiple services")

        choice = input("\nSelect option (1-7): ").strip()

        if choice == "1":
            self.setup_twilio()
        elif choice == "2":
            self.setup_email()
        elif choice == "3":
            self.setup_telegram()
        elif choice == "4":
            self.setup_discord()
        elif choice == "5":
            self.setup_sms()
        elif choice == "6":
            print("Push notifications coming soon!")
        elif choice == "7":
            # Setup multiple services
            services = input("Which services? (comma-separated: twilio,email,telegram,discord,sms): ").lower().split(',')
            for service in services:
                service = service.strip()
                if service == "twilio":
                    self.setup_twilio()
                elif service == "email":
                    self.setup_email()
                elif service == "telegram":
                    self.setup_telegram()
                elif service == "discord":
                    self.setup_discord()
                elif service == "sms":
                    self.setup_sms()

        self.save_config()

    def setup_twilio(self):
        """Setup Twilio configuration"""
        print("\n📱 TWILIO SMS SETUP")
        print("Get these from https://console.twilio.com\n")

        self.config["alert_settings"]["messaging_service"] = "twilio"
        self.config["alert_settings"]["twilio_config"]["sid"] = input("Account SID: ").strip()
        self.config["alert_settings"]["twilio_config"]["auth_token"] = input("Auth Token: ").strip()

        phone = input("Twilio phone number (or press Enter to skip): ").strip()
        if phone:
            self.config["alert_settings"]["twilio_config"]["phone_number"] = phone

        msg_sid = input("Messaging Service SID (optional): ").strip()
        if msg_sid:
            self.config["alert_settings"]["twilio_config"]["messaging_service_sid"] = msg_sid

        print("✅ Twilio configured")

    def setup_email(self):
        """Setup email configuration"""
        print("\n📧 EMAIL ALERTS SETUP")

        self.config["alert_settings"]["messaging_service"] = "email"
        self.config["alert_settings"]["email_config"]["smtp_server"] = input("SMTP server (e.g., smtp.gmail.com): ").strip()
        self.config["alert_settings"]["email_config"]["username"] = input("Email address: ").strip()
        self.config["alert_settings"]["email_config"]["password"] = input("App password (not regular password): ").strip()

        port = input("SMTP port (default 587): ").strip()
        if port:
            self.config["alert_settings"]["email_config"]["smtp_port"] = int(port)

        print("✅ Email configured")

    def setup_telegram(self):
        """Setup Telegram bot configuration"""
        print("\n📱 TELEGRAM BOT SETUP")
        print("1. Message @BotFather on Telegram")
        print("2. Create a new bot with /newbot")
        print("3. Copy the bot token\n")

        self.config["alert_settings"]["messaging_service"] = "telegram"
        self.config["alert_settings"]["telegram_config"]["bot_token"] = input("Bot token: ").strip()

        print("✅ Telegram bot configured")
        print("Note: You'll need to start a chat with your bot and get chat IDs")

    def setup_discord(self):
        """Setup Discord webhook/bot configuration"""
        print("\n🤖 DISCORD ALERT SETUP")
        print("Choose your preferred Discord integration method:")
        print("1. Webhook (easiest - no bot needed)")
        print("2. Bot (more advanced - requires bot creation)")

        choice = input("Choice (1 or 2): ").strip()

        if choice == "1":
            print("\n📎 WEBHOOK SETUP")
            print("1. Go to your Discord server settings")
            print("2. Go to Integrations → Webhooks")
            print("3. Create a new webhook")
            print("4. Copy the webhook URL\n")

            webhook_url = input("Webhook URL: ").strip()
            self.config["alert_settings"]["discord_config"]["webhook_url"] = webhook_url
            print("✅ Discord webhook configured")

        elif choice == "2":
            print("\n🤖 BOT SETUP")
            print("1. Go to https://discord.com/developers/applications")
            print("2. Create a new application")
            print("3. Go to Bot section and create a bot")
            print("4. Copy the bot token")
            print("5. Invite bot to your server with proper permissions\n")

            bot_token = input("Bot token: ").strip()
            channel_id = input("Channel ID (right-click channel → Copy ID): ").strip()

            self.config["alert_settings"]["discord_config"]["bot_token"] = bot_token
            self.config["alert_settings"]["discord_config"]["channel_id"] = channel_id
            print("✅ Discord bot configured")

        self.config["alert_settings"]["messaging_service"] = "discord"

    def setup_sms(self):
        """Setup free SMS alerts using email-to-SMS gateways"""
        print("\n📱 FREE SMS ALERT SETUP")
        print("Send SMS through email using carrier gateways (no paid service needed)!")
        print("Supports Indian carriers: Airtel, Vodafone/Idea, Jio, BSNL, Tata Docomo")
        print()

        smtp_server = input("SMTP Server (smtp.gmail.com, smtp-mail.outlook.com, etc.): ").strip()
        smtp_port = int(input("SMTP Port (587 for TLS): ").strip() or "587")
        username = input("Your email address: ").strip()
        password = input("Email password (or App password for Gmail): ").strip()

        self.config["alert_settings"]["sms_config"] = {
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "username": username,
            "password": password,
            "use_tls": True
        }
        self.config["alert_settings"]["messaging_service"] = "sms"

        print("✅ SMS configuration saved!")
        print("\n📝 Add emergency contacts with carrier info:")
        print("Format examples:")
        print("  Mom: +919876543210 (Airtel)")
        print("  Dad: +919876543211@jio.com")
        print("\nSupported Indian carriers: Airtel, Vodafone/Idea, Jio, BSNL, Tata Docomo")
        print("International carriers also supported")

    def get_emergency_contacts(self):
        """Get list of emergency contacts"""
        return self.config["user_info"]["emergency_contacts"]

    def get_user_info(self):
        """Get user information"""
        return self.config["user_info"]

    def get_messaging_config(self):
        """Get messaging configuration"""
        return self.config["alert_settings"]

    def validate_config(self):
        """Validate that configuration is complete"""
        user_info = self.config["user_info"]
        if not user_info["name"] or not user_info["email"]:
            return False, "User name and email are required"

        if not user_info["emergency_contacts"]:
            return False, "At least one emergency contact is required"

        alert_settings = self.config["alert_settings"]
        if alert_settings["messaging_service"] == "twilio":
            twilio = alert_settings["twilio_config"]
            if not twilio["sid"] or not twilio["auth_token"]:
                return False, "Twilio SID and Auth Token are required"

        return True, "Configuration is valid"

# Global instance
user_config = UserConfig()

def setup_new_user():
    """Complete user setup process"""
    config = UserConfig()

    print("Welcome to HerShield Setup!")
    print("=" * 40)

    # Profile setup
    config.setup_user_profile()

    # Messaging setup
    config.setup_messaging()

    # Validation
    valid, message = config.validate_config()
    if valid:
        print(f"\n🎉 Setup complete! {message}")
        return True
    else:
        print(f"\n❌ Setup incomplete: {message}")
        return False

if __name__ == "__main__":
    setup_new_user()