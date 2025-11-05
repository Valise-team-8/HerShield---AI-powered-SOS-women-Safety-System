from twilio.rest import Client
from core.firebase_service import get_user_contacts
from core.enhanced_location_service import EnhancedLocationService
from core.user_config import user_config
from core.email_alert import EmailAlert
from core.telegram_alert import TelegramAlert
from core.discord_alert import DiscordAlert
from core.sms_alert import SMSAlert
from core.fast2sms_alert import Fast2SMSAlert
from core.voice_alert import send_voice_alert
from core.offline_alert_system import OfflineAlertSystem
import datetime, os

def send_alert(user_email, reason="Distress detected"):
    """
    Enhanced alert system with offline capabilities and improved location services.
    Supports multiple messaging services with automatic fallback to offline methods.
    """
    try:
        # Initialize enhanced services
        location_service = EnhancedLocationService()
        offline_system = OfflineAlertSystem()
        
        # Get enhanced location information
        location_info = location_service.get_emergency_location_info()
        location_url = location_info.get('url', 'Location not available')
        location_description = location_info.get('description', 'Location not available')
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Get user info and messaging config
        user_info = user_config.get_user_info()
        messaging_config = user_config.get_messaging_config()
        service = messaging_config["messaging_service"]

        # Create enhanced alert message
        alert_data = {
            "user_email": user_email,
            "reason": reason,
            "location": location_url,
            "location_info": location_info,
            "location_description": location_description,
            "timestamp": timestamp,
            "user_info": user_info
        }

        success_count = 0
        failed_services = []

        # Try online services first
        online_success = False
        
        # Send via configured service(s)
        if service == "twilio" or "twilio" in str(service).split(','):
            if send_twilio_alert(alert_data):
                success_count += 1
                online_success = True
            else:
                failed_services.append("twilio")

        if service == "email" or "email" in str(service).split(','):
            if send_email_alert(alert_data):
                success_count += 1
                online_success = True
            else:
                failed_services.append("email")

        if service == "telegram" or "telegram" in str(service).split(','):
            if send_telegram_alert(alert_data):
                success_count += 1
                online_success = True
            else:
                failed_services.append("telegram")

        if service == "discord" or "discord" in str(service).split(','):
            if send_discord_alert(alert_data):
                success_count += 1
                online_success = True
            else:
                failed_services.append("discord")

        if service == "sms" or "sms" in str(service).split(','):
            if send_sms_alert(alert_data):
                success_count += 1
                online_success = True
            else:
                failed_services.append("sms")

        # If online methods failed, use offline methods
        if not online_success or failed_services:
            print("[FALLBACK] Using offline alert methods...")
            
            # Create comprehensive alert message for offline storage
            offline_message = f"""
🚨 EMERGENCY ALERT 🚨
User: {user_info.get('name', 'Unknown')}
Email: {user_email}
Phone: {user_info.get('phone', 'Not provided')}
Reason: {reason}
Time: {timestamp}

Location Information:
{location_description}

Emergency Contacts:
{chr(10).join(f"• {contact}" for contact in user_info.get('emergency_contacts', []))}

Medical Information:
• Blood Type: {user_info.get('medical_info', {}).get('blood_type', 'Not specified')}
• Allergies: {', '.join(user_info.get('medical_info', {}).get('allergies', [])) or 'None'}
• Medications: {', '.join(user_info.get('medical_info', {}).get('medications', [])) or 'None'}
• Conditions: {', '.join(user_info.get('medical_info', {}).get('conditions', [])) or 'None'}

This alert was generated automatically by HerShield Safety System.
"""
            
            # Send via offline methods
            if offline_system.send_offline_alert(
                'emergency_alert',
                offline_message,
                location_info.get('coordinates'),
                user_info
            ):
                success_count += 1
                print("[OFFLINE ALERT] Emergency alert stored and broadcasted offline")

        # Send voice alerts to emergency services (for official use)
        # Uncomment the line below for production use with emergency services
        # if send_voice_alert(alert_data['reason'], alert_data['location']):
        #     success_count += 1

        if success_count == 0:
            print("[ERROR] Failed to send alert via any method (online or offline)")
            return False

        # Log the alert with enhanced information
        log_alert(user_email, reason, location_url, timestamp, location_info, failed_services)
        
        if online_success:
            print(f"[SUCCESS] Alert sent via {success_count} method(s)")
        else:
            print(f"[OFFLINE SUCCESS] Alert stored offline and will retry when connectivity restored")
        
        return True

    except Exception as e:
        print(f"[CRITICAL ERROR] Alert system failure: {e}")
        
        # Last resort - try basic offline storage
        try:
            offline_system = OfflineAlertSystem()
            offline_system.store_alert_offline(
                'system_failure',
                f"Alert system failure: {reason} - {str(e)}",
                None,
                {'user_email': user_email, 'error': str(e)}
            )
            print("[EMERGENCY FALLBACK] Alert stored in emergency offline storage")
        except:
            print("[FATAL ERROR] All alert methods failed")
        
        return False

def send_twilio_alert(alert_data):
    """Send alert via Twilio SMS"""
    try:
        twilio_config = user_config.get_messaging_config()["twilio_config"]

        if not twilio_config["sid"] or not twilio_config["auth_token"]:
            print("[WARN] Twilio not configured")
            return False

        client = Client(twilio_config["sid"], twilio_config["auth_token"])

        # Create SMS message
        msg = (f"🚨 HER SHIELD ALERT 🚨\n"
               f"User: {alert_data['user_info']['name']}\n"
               f"Reason: {alert_data['reason']}\n"
               f"Location: {alert_data['location']}\n"
               f"Time: {alert_data['timestamp']}")

        # Get contacts (prefer user config over Firebase)
        contacts = user_config.get_emergency_contacts()
        if not contacts:
            # Fallback to Firebase
            contacts = get_user_contacts(alert_data['user_email'])
            if not contacts:
                print("[WARN] No emergency contacts configured")
                return False

        sent_count = 0
        for contact in contacts:
            if not contact or not isinstance(contact, str) or not contact.strip():
                continue

            # Extract phone number if in "Name: +123..." format
            if ':' in contact:
                phone = contact.split(':')[1].strip()
            else:
                phone = contact.strip()

            try:
                # Use Messaging Service SID if available, otherwise use phone number
                if twilio_config.get("messaging_service_sid"):
                    message = client.messages.create(
                        to=phone,
                        messaging_service_sid=twilio_config["messaging_service_sid"],
                        body=msg
                    )
                elif twilio_config.get("phone_number"):
                    message = client.messages.create(
                        to=phone,
                        from_=twilio_config["phone_number"],
                        body=msg
                    )
                else:
                    print("[ERROR] No Twilio sender configured")
                    return False

                print(f"[SMS SENT] Alert sent to {phone} (SID: {message.sid})")
                sent_count += 1

            except Exception as e:
                print(f"[SMS ERROR] Failed to send to {phone}: {e}")

        return sent_count > 0

    except Exception as e:
        print(f"[TWILIO ERROR] {e}")
        return False

def send_email_alert(alert_data):
    """Send alert via email"""
    try:
        email_alert = EmailAlert()
        location = alert_data['location']
        return email_alert.send_alert(alert_data['user_email'], alert_data['reason'], location)
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

def send_telegram_alert(alert_data):
    """Send alert via Telegram"""
    try:
        telegram_alert = TelegramAlert()
        location = alert_data['location']
        return telegram_alert.send_alert(alert_data['user_email'], alert_data['reason'], location)
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")
        return False

def send_discord_alert(alert_data):
    """Send alert via Discord"""
    try:
        discord_alert = DiscordAlert()
        location = alert_data['location']
        return discord_alert.send_alert(alert_data['user_email'], alert_data['reason'], location)
    except Exception as e:
        print(f"[DISCORD ERROR] {e}")
        return False

def send_sms_alert(alert_data):
    """Send alert via Fast2SMS Quick SMS (no DLT required)"""
    try:
        sms_alert = Fast2SMSAlert()
        location = alert_data['location']
        return sms_alert.send_alert(alert_data['user_email'], alert_data['reason'], location)
    except Exception as e:
        print(f"[SMS ERROR] {e}")
        return False

def log_alert(user_email, reason, location, timestamp, location_info=None, failed_services=None):
    """Enhanced alert logging with detailed information"""
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/alerts.log", "a", encoding='utf-8') as f:
            f.write(f"\n[{timestamp}] EMERGENCY ALERT\n")
            f.write(f"User: {user_email}\n")
            f.write(f"Reason: {reason}\n")
            f.write(f"Location URL: {location}\n")
            
            if location_info:
                f.write(f"Location Status: {location_info.get('status', 'unknown')}\n")
                f.write(f"Location Method: {location_info.get('method', 'unknown')}\n")
                f.write(f"Location Accuracy: {location_info.get('accuracy', 'unknown')}\n")
                if location_info.get('coordinates'):
                    coords = location_info['coordinates']
                    f.write(f"Coordinates: {coords.get('latitude', 'N/A')}, {coords.get('longitude', 'N/A')}\n")
            
            if failed_services:
                f.write(f"Failed Services: {', '.join(failed_services)}\n")
            
            f.write("-" * 60 + "\n")
        
        print("[LOGGED] Enhanced alert record created")
    except Exception as e:
        print(f"[LOG ERROR] {e}")
