#!/usr/bin/env python3
"""
Email-based alert system as alternative to Twilio SMS
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.user_config import user_config

class EmailAlert:
    """Send emergency alerts via email"""

    def __init__(self):
        self.config = user_config.get_messaging_config()["email_config"]
        self.user_info = user_config.get_user_info()

    def send_alert(self, user_email, reason="Emergency alert", location=None):
        """Send emergency alert via email"""

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config["username"]
            msg['Subject'] = f"🚨 HER SHIELD EMERGENCY ALERT - {self.user_info['name']}"

            # Email body
            body = f"""
🚨 HER SHIELD EMERGENCY ALERT 🚨

User: {self.user_info['name']}
Email: {self.user_info['email']}
Phone: {self.user_info['phone']}
Reason: {reason}

{f'Location: {location}' if location else ''}

Medical Information:
- Blood Type: {self.user_info['medical_info']['blood_type'] or 'Not specified'}
- Allergies: {', '.join(self.user_info['medical_info']['allergies']) or 'None specified'}
- Medications: {', '.join(self.user_info['medical_info']['medications']) or 'None specified'}
- Conditions: {', '.join(self.user_info['medical_info']['conditions']) or 'None specified'}

Emergency Contacts:
{chr(10).join(f"- {contact}" for contact in self.user_info['emergency_contacts'])}

---
This is an automated emergency alert from HerShield safety system.
Please respond immediately if you receive this message.
"""

            msg.attach(MIMEText(body, 'plain'))

            # Connect to SMTP server
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            if self.config["use_tls"]:
                server.starttls()

            server.login(self.config["username"], self.config["password"])

            # Send to all emergency contacts
            contacts = user_config.get_emergency_contacts()
            sent_count = 0

            for contact in contacts:
                # Extract email if contact is in "Name: email" format
                if ':' in contact:
                    email = contact.split(':')[1].strip()
                else:
                    # Assume contact is just an email
                    email = contact.strip()

                if '@' in email:  # Basic email validation
                    msg['To'] = email
                    server.send_message(msg)
                    print(f"[EMAIL SENT] Alert sent to {email}")
                    sent_count += 1

            server.quit()

            if sent_count > 0:
                print(f"[SUCCESS] Email alerts sent to {sent_count} contacts")
                return True
            else:
                print("[ERROR] No valid email addresses found")
                return False

        except Exception as e:
            print(f"[ERROR] Failed to send email alert: {e}")
            return False

def test_email_config():
    """Test email configuration"""
    print("Testing email configuration...")

    alert = EmailAlert()
    config = alert.config

    if not config["smtp_server"] or not config["username"] or not config["password"]:
        print("❌ Email not configured. Run user setup first.")
        return False

    try:
        server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
        if config["use_tls"]:
            server.starttls()
        server.login(config["username"], config["password"])
        server.quit()
        print("✅ Email configuration is working")
        return True
    except Exception as e:
        print(f"❌ Email configuration error: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Test configuration
    test_email_config()

    # Send test alert
    if input("Send test alert? (y/n): ").lower().startswith('y'):
        alert = EmailAlert()
        alert.send_alert("test@example.com", "Test emergency alert", "Test location")