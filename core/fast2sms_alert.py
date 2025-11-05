#!/usr/bin/env python3
"""
Fast2SMS Quick SMS alert system - No DLT registration required
Uses international gateway for instant SMS delivery
"""

import requests
from core.user_config import user_config

class Fast2SMSAlert:
    """Send emergency alerts via Fast2SMS Quick SMS API"""

    def __init__(self):
        self.api_key = "YOUR_FAST2SMS_API_KEY"  # Replace with actual API key
        self.base_url = "https://www.fast2sms.com/dev/bulkV2"

    def send_alert(self, user_email, reason="Emergency alert", location=None):
        """Send emergency alert via Fast2SMS Quick SMS"""

        if self.api_key == "YOUR_FAST2SMS_API_KEY":
            print("[ERROR] Fast2SMS API key not configured")
            return False

        # Create SMS message (keep it short for SMS)
        sms_message = self._create_sms_message(reason, location)

        # Get emergency contacts
        contacts = self._get_sms_contacts()
        if not contacts:
            print("[ERROR] No SMS-capable contacts configured")
            return False

        # Extract phone numbers
        phone_numbers = []
        for contact in contacts:
            if ':' in contact:
                phone = contact.split(':')[1].strip()
            else:
                phone = contact.strip()

            # Remove any non-numeric characters and ensure it starts with number
            phone = ''.join(filter(str.isdigit, phone))
            if phone and len(phone) >= 10:
                phone_numbers.append(phone)

        if not phone_numbers:
            print("[ERROR] No valid phone numbers found")
            return False

        # Send SMS
        return self._send_sms(sms_message, phone_numbers)

    def _create_sms_message(self, reason, location):
        """Create a concise SMS message"""
        user_info = user_config.get_user_info()
        name = user_info.get('name', 'User')

        message = f"🚨 HER SHIELD ALERT 🚨\n{name}: {reason}"
        if location:
            message += f"\nLocation: {location}"

        return message

    def _get_sms_contacts(self):
        """Get emergency contacts for SMS"""
        user_info = user_config.get_user_info()
        contacts = user_info.get('emergency_contacts', [])
        return contacts

    def _send_sms(self, message, phone_numbers):
        """Send SMS via Fast2SMS Quick SMS API"""
        try:
            # Join phone numbers with comma
            numbers_str = ','.join(phone_numbers)

            # Prepare payload
            payload = {
                'authorization': self.api_key,
                'message': message,
                'language': 'english',
                'route': 'q',  # Quick SMS route
                'numbers': numbers_str
            }

            # Make API request
            response = requests.post(self.base_url, data=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get('return') == True:
                    print(f"[SMS SENT] Alert sent to {len(phone_numbers)} number(s)")
                    print(f"Request ID: {result.get('request_id')}")
                    return True
                else:
                    print(f"[SMS ERROR] API returned false: {result}")
                    return False
            else:
                print(f"[SMS ERROR] HTTP {response.status_code}: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"[SMS ERROR] Request failed: {e}")
            return False
        except Exception as e:
            print(f"[SMS ERROR] Unexpected error: {e}")
            return False