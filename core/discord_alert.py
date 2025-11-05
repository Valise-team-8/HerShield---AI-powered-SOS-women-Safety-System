#!/usr/bin/env python3
"""
Discord alert system as free alternative to Twilio SMS
Supports both webhooks and bot APIs
"""

import requests
from core.user_config import user_config

class DiscordAlert:
    """Send emergency alerts via Discord"""

    def __init__(self):
        self.config = user_config.get_messaging_config()["discord_config"]
        self.user_info = user_config.get_user_info()

    def send_alert(self, user_email, reason="Emergency alert", location=None):
        """Send emergency alert via Discord"""

        if not self.config["webhook_url"] and not (self.config["bot_token"] and self.config["channel_id"]):
            print("[ERROR] Discord not configured")
            return False

        # Create embed message (rich formatting)
        embed = {
            "title": "🚨 HER SHIELD EMERGENCY ALERT 🚨",
            "color": 16711680,  # Red color
            "fields": [
                {
                    "name": "👤 User",
                    "value": self.user_info['name'],
                    "inline": True
                },
                {
                    "name": "📧 Email",
                    "value": self.user_info['email'],
                    "inline": True
                },
                {
                    "name": "📱 Phone",
                    "value": self.user_info['phone'] or 'Not provided',
                    "inline": True
                },
                {
                    "name": "⚠️ Reason",
                    "value": reason,
                    "inline": False
                }
            ],
            "timestamp": None  # Will be set by Discord
        }

        # Add location if available
        if location:
            embed["fields"].append({
                "name": "📍 Location",
                "value": f"[View on Maps]({location})",
                "inline": False
            })

        # Add medical information
        medical_info = []
        if self.user_info['medical_info']['blood_type']:
            medical_info.append(f"🩸 Blood Type: {self.user_info['medical_info']['blood_type']}")
        if self.user_info['medical_info']['allergies']:
            medical_info.append(f"🤧 Allergies: {', '.join(self.user_info['medical_info']['allergies'])}")
        if self.user_info['medical_info']['medications']:
            medical_info.append(f"💊 Medications: {', '.join(self.user_info['medical_info']['medications'])}")
        if self.user_info['medical_info']['conditions']:
            medical_info.append(f"🩺 Conditions: {', '.join(self.user_info['medical_info']['conditions'])}")

        if medical_info:
            embed["fields"].append({
                "name": "🏥 Medical Information",
                "value": "\n".join(medical_info),
                "inline": False
            })

        # Add emergency contacts
        if self.user_info['emergency_contacts']:
            contacts_text = "\n".join(f"• {contact}" for contact in self.user_info['emergency_contacts'])
            embed["fields"].append({
                "name": "📞 Emergency Contacts",
                "value": contacts_text,
                "inline": False
            })

        # Send via webhook (preferred method)
        if self.config["webhook_url"]:
            return self._send_via_webhook(embed)

        # Send via bot API
        elif self.config["bot_token"] and self.config["channel_id"]:
            return self._send_via_bot(embed)

        return False

    def _send_via_webhook(self, embed):
        """Send alert via Discord webhook"""
        try:
            data = {
                "embeds": [embed],
                "username": "HerShield Alert",
                "avatar_url": "https://i.imgur.com/4M34hi2.png"  # Shield icon
            }

            response = requests.post(self.config["webhook_url"], json=data, timeout=10)

            if response.status_code == 204:
                print("[DISCORD WEBHOOK] Alert sent successfully")
                return True
            else:
                print(f"[DISCORD WEBHOOK ERROR] {response.status_code}: {response.text}")
                return False

        except Exception as e:
            print(f"[DISCORD WEBHOOK ERROR] {e}")
            return False

    def _send_via_bot(self, embed):
        """Send alert via Discord bot API"""
        try:
            url = f"https://discord.com/api/v10/channels/{self.config['channel_id']}/messages"
            headers = {
                "Authorization": f"Bot {self.config['bot_token']}",
                "Content-Type": "application/json"
            }

            data = {
                "embeds": [embed]
            }

            response = requests.post(url, headers=headers, json=data, timeout=10)

            if response.status_code == 200:
                print("[DISCORD BOT] Alert sent successfully")
                return True
            else:
                print(f"[DISCORD BOT ERROR] {response.status_code}: {response.text}")
                return False

        except Exception as e:
            print(f"[DISCORD BOT ERROR] {e}")
            return False

def setup_discord_webhook():
    """Help user set up Discord webhook"""
    print("\n🤖 DISCORD WEBHOOK SETUP")
    print("This is the easiest way to send Discord alerts!")
    print()
    print("Steps:")
    print("1. Open Discord and go to your server")
    print("2. Click the server name → Server Settings")
    print("3. Go to Integrations → Webhooks")
    print("4. Click 'Create Webhook'")
    print("5. Name it 'HerShield Alerts'")
    print("6. Choose a channel for alerts")
    print("7. Click 'Copy Webhook URL'")
    print()

    webhook_url = input("Paste your webhook URL: ").strip()

    if webhook_url and webhook_url.startswith("https://discord.com/api/webhooks/"):
        user_config.config["alert_settings"]["discord_config"]["webhook_url"] = webhook_url
        user_config.config["alert_settings"]["messaging_service"] = "discord"
        user_config.save_config()
        print("✅ Discord webhook configured!")
        print("You can now receive emergency alerts in your Discord channel.")
        return True
    else:
        print("❌ Invalid webhook URL. It should start with 'https://discord.com/api/webhooks/'")
        return False

def test_discord_config():
    """Test Discord configuration"""
    print("Testing Discord configuration...")

    alert = DiscordAlert()
    config = alert.config

    if not config["webhook_url"] and not (config["bot_token"] and config["channel_id"]):
        print("❌ Discord not configured. Run setup first.")
        return False

    # Send test alert
    success = alert.send_alert("test@example.com", "Test emergency alert", "https://maps.google.com/?q=0,0")

    if success:
        print("✅ Discord configuration is working!")
        return True
    else:
        print("❌ Discord test failed. Check your configuration.")
        return False

if __name__ == "__main__":
    print("Discord Alert Setup & Test")
    print("1. Setup webhook")
    print("2. Test configuration")

    choice = input("Choose option (1-2): ").strip()

    if choice == "1":
        setup_discord_webhook()
    elif choice == "2":
        test_discord_config()
    else:
        print("Invalid choice")