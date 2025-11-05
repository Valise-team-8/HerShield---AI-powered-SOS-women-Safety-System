#!/usr/bin/env python3
"""
Free SMS alert system using email-to-SMS gateways
No paid services required - uses carrier email gateways
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.user_config import user_config

class SMSAlert:
    """Send emergency alerts via free email-to-SMS gateways"""

    def __init__(self):
        self.config = user_config.get_messaging_config()["sms_config"]
        self.user_info = user_config.get_user_info()

    def send_alert(self, user_email, reason="Emergency alert", location=None):
        """Send emergency alert via SMS using email gateways"""

        if not self.config["smtp_server"] or not self.config["username"] or not self.config["password"]:
            print("[ERROR] SMS (email) not configured")
            return False

        # Create SMS message (keep it short for SMS)
        sms_message = self._create_sms_message(reason, location)

        # Get emergency contacts with carrier info
        contacts = self._get_sms_contacts()
        if not contacts:
            print("[ERROR] No SMS-capable contacts configured")
            return False

        sent_count = 0
        for contact_info in contacts:
            try:
                if self._send_sms_via_email(contact_info, sms_message):
                    sent_count += 1
                    print(f"[SMS SENT] Alert sent to {contact_info['phone']}")
            except Exception as e:
                print(f"[SMS ERROR] Failed to send to {contact_info['phone']}: {e}")

        return sent_count > 0

    def _create_sms_message(self, reason, location):
        """Create a concise SMS message"""
        name = self.user_info['name']

        message = f"🚨 HER SHIELD ALERT 🚨\n{name}: {reason}"

        if location:
            message += f"\nLocation: {location}"

        # Keep under 160 characters for SMS
        if len(message) > 160:
            message = message[:157] + "..."

        return message

    def _get_sms_contacts(self):
        """Get contacts that can receive SMS via email gateways"""
        contacts = []
        emergency_contacts = user_config.get_emergency_contacts()

        for contact in emergency_contacts:
            contact_info = self._parse_contact_for_sms(contact)
            if contact_info:
                contacts.append(contact_info)

        return contacts

    def _parse_contact_for_sms(self, contact):
        """Parse contact string to extract phone and carrier info"""
        # Expected formats:
        # "Name: +1234567890@carrier.com"
        # "+1234567890@carrier.com"
        # "Name: +1234567890 (Verizon)"

        if ':' in contact:
            parts = contact.split(':')
            name = parts[0].strip()
            phone_carrier = parts[1].strip()
        else:
            name = "Contact"
            phone_carrier = contact.strip()

        # Check if it's already an email address
        if '@' in phone_carrier:
            # Extract phone number from email
            email = phone_carrier
            phone = email.split('@')[0]
            if phone.startswith('+'):
                phone = phone[1:]
            return {
                'name': name,
                'phone': phone,
                'email': email
            }

        # If it's a phone number with carrier name, convert to email
        if '(' in phone_carrier and ')' in phone_carrier:
            phone_part = phone_carrier.split('(')[0].strip()
            carrier_part = phone_carrier.split('(')[1].split(')')[0].strip()

            phone = ''.join(filter(str.isdigit, phone_part))
            email = self._phone_to_email(phone, carrier_part)

            if email:
                return {
                    'name': name,
                    'phone': phone,
                    'email': email
                }

        return None

    def _phone_to_email(self, phone, carrier):
        """Convert phone number and carrier to email gateway address"""
        # Indian carrier gateways (primary)
        gateways = {
            # Major Indian carriers
            'airtel': f'{phone}@airtelap.com',
            'airtelkk': f'{phone}@airtelkk.com',
            'vodafone': f'{phone}@vodafone.com',
            'idea': f'{phone}@ideacellular.net',
            'jio': f'{phone}@jio.com',
            'rjil': f'{phone}@rjil.com',  # Reliance Jio
            'bsnl': f'{phone}@bsnl.in',
            'tatadocomo': f'{phone}@tatadocomo.com',
            'docomo': f'{phone}@tatadocomo.com',
            'reliance': f'{phone}@rjil.com',

            # US carriers (fallback for international users)
            'verizon': f'{phone}@vtext.com',
            'att': f'{phone}@txt.att.net',
            'tmobile': f'{phone}@tmomail.net',
            'sprint': f'{phone}@messaging.sprintpcs.com',
            'virgin': f'{phone}@vmobl.com',
            'boost': f'{phone}@myboostmobile.com',
            'cricket': f'{phone}@sms.cricketwireless.net',
            'metro': f'{phone}@mymetropcs.com',
            'straight': f'{phone}@vtext.com',  # Straight Talk uses Verizon
            'uscellular': f'{phone}@email.uscc.net',
            'mint': f'{phone}@mailmymobile.net'
        }

        carrier_lower = carrier.lower().replace(' ', '').replace('-', '')

        # Try exact match first
        if carrier_lower in gateways:
            return gateways[carrier_lower]

        # Try partial matches
        for key, gateway in gateways.items():
            if key in carrier_lower or carrier_lower in key:
                return gateway

        return None

    def _send_sms_via_email(self, contact_info, message):
        """Send SMS by emailing to carrier gateway"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config["username"]
            msg['To'] = contact_info['email']
            msg['Subject'] = ""  # SMS gateways often ignore subject

            msg.attach(MIMEText(message, 'plain'))

            # Connect to SMTP server
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            if self.config["use_tls"]:
                server.starttls()

            server.login(self.config["username"], self.config["password"])
            server.send_message(msg)
            server.quit()

            return True

        except Exception as e:
            print(f"[SMS EMAIL ERROR] {e}")
            return False

def setup_sms_alert():
    """Setup free SMS alerts using email-to-SMS gateways"""
    print("\n📱 FREE SMS ALERT SETUP")
    print("This sends SMS through your email account using carrier gateways!")
    print("Supports Indian carriers: Airtel, Vodafone/Idea, Jio, BSNL, Tata Docomo")
    print("No paid SMS service required.\n")

    print("First, configure your email account for sending:")
    print("1. Gmail: Enable 'Less secure app access' or use App Passwords")
    print("2. Outlook/Hotmail: Use your regular password")
    print("3. Other: Check your email provider's SMTP settings\n")

    smtp_server = input("SMTP Server (e.g., smtp.gmail.com): ").strip()
    smtp_port = int(input("SMTP Port (587 for TLS): ").strip() or "587")
    username = input("Email address: ").strip()
    password = input("Email password/App password: ").strip()

    # Update config
    user_config.config["alert_settings"]["sms_config"] = {
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "username": username,
        "password": password,
        "use_tls": True
    }
    user_config.config["alert_settings"]["messaging_service"] = "sms"
    user_config.save_config()

    print("\n✅ Email configuration saved!")
    print("\nNext, add emergency contacts with carrier info:")
    print("Format: Name: +919876543210 (Airtel)")
    print("Or: Name: +919876543211@jio.com")
    print("\nSupported Indian carriers: Airtel, Vodafone/Idea, Jio, BSNL, Tata Docomo")
    print("International carriers also supported (US, UK, Europe)")

    return True

def test_sms_config():
    """Test SMS configuration"""
    print("Testing SMS configuration...")

    alert = SMSAlert()
    config = alert.config

    if not config["smtp_server"] or not config["username"] or not config["password"]:
        print("❌ SMS not configured. Run setup first.")
        return False

    # Test SMTP connection
    try:
        server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
        if config["use_tls"]:
            server.starttls()
        server.login(config["username"], config["password"])
        server.quit()
        print("✅ Email/SMTP configuration is working")
        return True
    except Exception as e:
        print(f"❌ Email configuration error: {e}")
        return False

if __name__ == "__main__":
    print("Free SMS Alert Setup & Test")
    print("1. Setup SMS alerts")
    print("2. Test configuration")
    print("3. Show supported carriers")

    choice = input("\nChoose option (1-3): ").strip()

    if choice == "1":
        setup_sms_alert()
    elif choice == "2":
        test_sms_config()
    elif choice == "3":
        print("\n📱 SUPPORTED CARRIERS:")
        print("• Verizon: @vtext.com")
        print("• AT&T: @txt.att.net")
        print("• T-Mobile: @tmomail.net")
        print("• Sprint: @messaging.sprintpcs.com")
        print("• Virgin Mobile: @vmobl.com")
        print("• Boost Mobile: @myboostmobile.com")
        print("• Cricket: @sms.cricketwireless.net")
        print("• Metro PCS: @mymetropcs.com")
        print("• US Cellular: @email.uscc.net")
        print("• Mint Mobile: @mailmymobile.net")
        print("\nUsage: Name: +1234567890 (Verizon)")
    else:
        print("Invalid choice")