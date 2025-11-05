#!/usr/bin/env python3
"""
Telegram Bot alert system as alternative to Twilio SMS
"""

import requests
from core.user_config import user_config

class TelegramAlert:
    """Send emergency alerts via Telegram Bot"""

    def __init__(self):
        self.config = user_config.get_messaging_config()["telegram_config"]
        self.user_info = user_config.get_user_info()
        self.base_url = f"https://api.telegram.org/bot{self.config['bot_token']}"

    def send_alert(self, user_email, reason="Emergency alert", location=None):
        """Send emergency alert via Telegram"""

        if not self.config["bot_token"]:
            print("[ERROR] Telegram bot not configured")
            return False

        # Create message
        message = f"""
🚨 HER SHIELD EMERGENCY ALERT 🚨

👤 User: {self.user_info['name']}
📧 Email: {self.user_info['email']}
📱 Phone: {self.user_info['phone']}
⚠️ Reason: {reason}

{f'📍 Location: {location}' if location else ''}

🏥 Medical Information:
🩸 Blood Type: {self.user_info['medical_info']['blood_type'] or 'Not specified'}
🤧 Allergies: {', '.join(self.user_info['medical_info']['allergies']) or 'None'}
💊 Medications: {', '.join(self.user_info['medical_info']['medications']) or 'None'}
🩺 Conditions: {', '.join(self.user_info['medical_info']['conditions']) or 'None'}

📞 Emergency Contacts:
{chr(10).join(f"• {contact}" for contact in self.user_info['emergency_contacts'])}

---
🤖 Automated alert from HerShield safety system
"""

        # Send to all configured chat IDs
        chat_ids = self.config.get("chat_ids", [])
        if not chat_ids:
            print("[ERROR] No Telegram chat IDs configured")
            return False

        sent_count = 0
        for chat_id in chat_ids:
            try:
                url = f"{self.base_url}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }

                response = requests.post(url, data=data, timeout=10)
                if response.status_code == 200:
                    print(f"[TELEGRAM SENT] Alert sent to chat {chat_id}")
                    sent_count += 1
                else:
                    print(f"[TELEGRAM ERROR] Failed to send to {chat_id}: {response.text}")

            except Exception as e:
                print(f"[TELEGRAM ERROR] Failed to send to {chat_id}: {e}")

        if sent_count > 0:
            print(f"[SUCCESS] Telegram alerts sent to {sent_count} chats")
            return True
        else:
            print("[ERROR] Failed to send any Telegram alerts")
            return False

    def add_chat_id(self, chat_id):
        """Add a chat ID to the configuration"""
        if "chat_ids" not in self.config:
            self.config["chat_ids"] = []

        if chat_id not in self.config["chat_ids"]:
            self.config["chat_ids"].append(chat_id)
            user_config.save_config()
            print(f"✅ Added chat ID: {chat_id}")
        else:
            print(f"ℹ️ Chat ID already exists: {chat_id}")

    def get_chat_ids(self):
        """Get current chat IDs"""
        return self.config.get("chat_ids", [])

def setup_telegram_bot():
    """Help user set up Telegram bot and get chat IDs"""
    print("\n=== TELEGRAM BOT SETUP ===")
    print("Follow these steps:")
    print("1. Open Telegram and search for @BotFather")
    print("2. Send /newbot and follow instructions")
    print("3. Copy the bot token")
    print("4. Send /setcommands to your bot")
    print("5. Add command: alert - Emergency alert")
    print()

    bot_token = input("Enter your bot token: ").strip()
    if not bot_token:
        return False

    # Update config
    user_config.config["alert_settings"]["telegram_config"]["bot_token"] = bot_token
    user_config.save_config()

    print("✅ Bot token saved")
    print("\nNext steps:")
    print("1. Start a chat with your bot")
    print("2. Send any message to activate the chat")
    print("3. Run this script again to get chat IDs")

    return True

def get_chat_updates():
    """Get recent chat updates to find chat IDs"""
    alert = TelegramAlert()
    if not alert.config["bot_token"]:
        print("❌ Bot token not set")
        return

    try:
        url = f"{alert.base_url}/getUpdates"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("result"):
                print("📱 Found chat IDs:")
                for update in data["result"]:
                    if "message" in update:
                        chat = update["message"]["chat"]
                        chat_id = chat["id"]
                        chat_name = chat.get("title", chat.get("username", "Unknown"))
                        print(f"  {chat_name}: {chat_id}")

                        if input(f"Add this chat ID? (y/n): ").lower().startswith('y'):
                            alert.add_chat_id(chat_id)
            else:
                print("❌ No recent messages found")
                print("Send a message to your bot first, then run this again")
        else:
            print(f"❌ Failed to get updates: {response.text}")

    except Exception as e:
        print(f"❌ Error getting updates: {e}")

if __name__ == "__main__":
    print("Telegram Bot Setup")
    print("1. Setup bot token")
    print("2. Get chat IDs")
    print("3. Test alert")

    choice = input("Choose option (1-3): ").strip()

    if choice == "1":
        setup_telegram_bot()
    elif choice == "2":
        get_chat_updates()
    elif choice == "3":
        alert = TelegramAlert()
        alert.send_alert("test@example.com", "Test alert")