#!/usr/bin/env python3
"""
SMS Alert Service for Offline Emergency Notifications
Sends SMS when internet is not available
"""

import os
import json
import time
from datetime import datetime

# Try to import SMS libraries
try:
    # Option 1: Twilio (most reliable)
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️ Twilio not available for SMS")

try:
    # Option 2: System SMS (for devices with SMS capability)
    import subprocess
    SYSTEM_SMS_AVAILABLE = True
except:
    SYSTEM_SMS_AVAILABLE = False


class SMSService:
    """
    SMS Service for offline emergency alerts
    Automatically detects internet connectivity and sends SMS when offline
    """
    
    def __init__(self):
        self.config_file = "config/sms_config.json"
        self.load_config()
        
    def load_config(self):
        """Load SMS configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.twilio_sid = config.get('twilio_account_sid', '')
                    self.twilio_token = config.get('twilio_auth_token', '')
                    self.twilio_number = config.get('twilio_phone_number', '')
            else:
                self.twilio_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
                self.twilio_token = os.getenv('TWILIO_AUTH_TOKEN', '')
                self.twilio_number = os.getenv('TWILIO_PHONE_NUMBER', '')
        except Exception as e:
            print(f"SMS config load error: {e}")
            self.twilio_sid = ''
            self.twilio_token = ''
            self.twilio_number = ''
    
    def is_internet_available(self):
        """Check if internet connection is available"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def send_emergency_sms(self, phone_number, user_name, location_text, alert_type="EMERGENCY"):
        """
        Send emergency SMS alert
        
        Args:
            phone_number: Recipient phone number
            user_name: Name of person in emergency
            location_text: Location information
            alert_type: Type of alert (EMERGENCY, SOS, etc.)
        
        Returns:
            dict with success status and message
        """
        try:
            # Format emergency message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"""
🚨 {alert_type} ALERT 🚨

Person: {user_name}
Time: {timestamp}
Location: {location_text}

This is an automated emergency alert from HerShield AI Safety System.

IMMEDIATE ACTION REQUIRED!
            """.strip()
            
            # Try Twilio first
            if TWILIO_AVAILABLE and self.twilio_sid and self.twilio_token:
                return self._send_via_twilio(phone_number, message)
            
            # Fallback to system SMS
            elif SYSTEM_SMS_AVAILABLE:
                return self._send_via_system(phone_number, message)
            
            else:
                return {
                    'success': False,
                    'message': 'No SMS service available. Please configure Twilio or enable system SMS.'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'SMS send error: {str(e)}'
            }
    
    def _send_via_twilio(self, phone_number, message):
        """Send SMS via Twilio"""
        try:
            client = Client(self.twilio_sid, self.twilio_token)
            
            sms = client.messages.create(
                body=message,
                from_=self.twilio_number,
                to=phone_number
            )
            
            return {
                'success': True,
                'message': f'SMS sent successfully via Twilio (SID: {sms.sid})',
                'sid': sms.sid
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Twilio SMS failed: {str(e)}'
            }
    
    def _send_via_system(self, phone_number, message):
        """Send SMS via system (Android/Linux)"""
        try:
            # This works on Android devices with Termux or Linux with SMS modem
            result = subprocess.run(
                ['termux-sms-send', '-n', phone_number, message],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'SMS sent via system'
                }
            else:
                return {
                    'success': False,
                    'message': f'System SMS failed: {result.stderr}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'System SMS error: {str(e)}'
            }
    
    def send_bulk_emergency_sms(self, contacts, user_name, location_text, alert_type="EMERGENCY"):
        """
        Send emergency SMS to multiple contacts
        
        Args:
            contacts: List of dicts with 'name' and 'phone' keys
            user_name: Name of person in emergency
            location_text: Location information
            alert_type: Type of alert
        
        Returns:
            dict with results for each contact
        """
        results = []
        
        for contact in contacts:
            phone = contact.get('phone', '')
            name = contact.get('name', 'Emergency Contact')
            
            if phone:
                result = self.send_emergency_sms(phone, user_name, location_text, alert_type)
                results.append({
                    'contact_name': name,
                    'phone': phone,
                    'success': result['success'],
                    'message': result['message']
                })
                
                # Small delay between messages to avoid rate limiting
                time.sleep(1)
        
        return {
            'total': len(contacts),
            'sent': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }
    
    def configure_twilio(self, account_sid, auth_token, phone_number):
        """Configure Twilio credentials"""
        try:
            self.twilio_sid = account_sid
            self.twilio_token = auth_token
            self.twilio_number = phone_number
            
            # Save to config file
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump({
                    'twilio_account_sid': account_sid,
                    'twilio_auth_token': auth_token,
                    'twilio_phone_number': phone_number
                }, f, indent=2)
            
            return {
                'success': True,
                'message': 'Twilio configured successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Configuration error: {str(e)}'
            }


# Global instance
sms_service = SMSService()


# Convenience function
def send_offline_emergency_alert(contacts, user_name, location_text):
    """
    Send emergency alert via SMS if offline, otherwise return False
    
    Returns:
        dict with results if offline, None if online
    """
    if not sms_service.is_internet_available():
        print("🚨 OFFLINE MODE - Sending SMS alerts")
        return sms_service.send_bulk_emergency_sms(contacts, user_name, location_text)
    else:
        return None  # Online, use normal alert system
