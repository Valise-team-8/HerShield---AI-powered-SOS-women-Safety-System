#!/usr/bin/env python3
"""
Enhanced Escalation System for HerShield
Provides progressive alert escalation with emergency calling and audio alerts
"""

import threading
import time
import logging
import json
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import os

# Audio imports
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

from .user_config import user_config
from .alert_manager import send_alert
from .offline_alert_system import OfflineAlertSystem
from .enhanced_location_service import EnhancedLocationService

logger = logging.getLogger(__name__)


class EscalationSystem:
    """Advanced escalation system with progressive alerts and emergency calling"""
    
    def __init__(self):
        self.active_alerts = {}
        self.escalation_threads = {}
        self.offline_system = OfflineAlertSystem()
        self.location_service = EnhancedLocationService()
        self.emergency_sounds_path = Path("data/emergency_sounds")
        self.emergency_sounds_path.mkdir(exist_ok=True)
        
        # Initialize audio systems
        self.init_audio_systems()
        
        # Create emergency sounds if they don't exist
        self.create_emergency_sounds()
        
        logger.info("Escalation system initialized")
    
    def init_audio_systems(self):
        """Initialize audio systems for alerts"""
        self.pygame_initialized = False
        self.tts_engine = None
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.pygame_initialized = True
                logger.info("Pygame audio system initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize pygame: {e}")
        
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 1.0)
                logger.info("Text-to-speech system initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize TTS: {e}")
    
    def create_emergency_sounds(self):
        """Create emergency sound files if they don't exist"""
        try:
            # Create a simple emergency tone using system beep
            beep_script = self.emergency_sounds_path / "emergency_beep.py"
            if not beep_script.exists():
                beep_code = '''
import time
import sys
import os

def emergency_beep():
    """Create emergency beeping sound"""
    for i in range(10):
        if os.name == 'nt':  # Windows
            import winsound
            winsound.Beep(1000, 500)  # 1000Hz for 500ms
            time.sleep(0.2)
            winsound.Beep(1500, 500)  # 1500Hz for 500ms
            time.sleep(0.2)
        else:  # Unix/Linux
            print("\\a", end="", flush=True)  # System bell
            time.sleep(0.5)

if __name__ == "__main__":
    emergency_beep()
'''
                beep_script.write_text(beep_code)
                logger.info("Emergency beep script created")
        except Exception as e:
            logger.warning(f"Failed to create emergency sounds: {e}")
    
    def play_emergency_sound(self, sound_type="alarm"):
        """Play emergency sound based on type"""
        try:
            if sound_type == "alarm":
                self._play_alarm_sound()
            elif sound_type == "siren":
                self._play_siren_sound()
            elif sound_type == "beep":
                self._play_beep_sound()
        except Exception as e:
            logger.error(f"Failed to play emergency sound: {e}")
    
    def _play_alarm_sound(self):
        """Play alarm sound"""
        try:
            # Try system beep first
            if os.name == 'nt':  # Windows
                import winsound
                for _ in range(5):
                    winsound.Beep(1000, 300)
                    time.sleep(0.1)
                    winsound.Beep(1500, 300)
                    time.sleep(0.1)
            else:
                # Unix/Linux system bell
                for _ in range(10):
                    print("\a", end="", flush=True)
                    time.sleep(0.3)
        except Exception as e:
            logger.warning(f"System beep failed: {e}")
            # Fallback to Python script
            try:
                beep_script = self.emergency_sounds_path / "emergency_beep.py"
                if beep_script.exists():
                    subprocess.Popen([sys.executable, str(beep_script)], 
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            except Exception as e2:
                logger.warning(f"Fallback beep failed: {e2}")
    
    def _play_siren_sound(self):
        """Play siren-like sound"""
        try:
            if os.name == 'nt':
                import winsound
                # Siren pattern: low to high frequency
                for cycle in range(3):
                    for freq in range(800, 1200, 50):
                        winsound.Beep(freq, 100)
                    for freq in range(1200, 800, -50):
                        winsound.Beep(freq, 100)
        except Exception as e:
            logger.warning(f"Siren sound failed: {e}")
            self._play_alarm_sound()  # Fallback
    
    def _play_beep_sound(self):
        """Play simple beep pattern"""
        try:
            if os.name == 'nt':
                import winsound
                for _ in range(3):
                    winsound.Beep(1000, 200)
                    time.sleep(0.3)
        except Exception as e:
            logger.warning(f"Beep sound failed: {e}")
    
    def speak_alert(self, message):
        """Use text-to-speech for alert message"""
        try:
            if self.tts_engine:
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
            else:
                logger.warning("TTS not available for voice alert")
        except Exception as e:
            logger.error(f"TTS alert failed: {e}")
    
    def start_escalation(self, alert_id, alert_type, message, location_data=None, evidence_data=None):
        """Start escalation process for an alert"""
        if alert_id in self.active_alerts:
            logger.warning(f"Alert {alert_id} already active")
            return
        
        alert_info = {
            'id': alert_id,
            'type': alert_type,
            'message': message,
            'location': location_data,
            'evidence': evidence_data,
            'start_time': datetime.now(),
            'escalation_level': 0,
            'acknowledged': False
        }
        
        self.active_alerts[alert_id] = alert_info
        
        # Start escalation thread
        escalation_thread = threading.Thread(
            target=self._escalation_worker,
            args=(alert_id,),
            daemon=True
        )
        self.escalation_threads[alert_id] = escalation_thread
        escalation_thread.start()
        
        logger.info(f"Escalation started for alert {alert_id}")
    
    def _escalation_worker(self, alert_id):
        """Worker thread for handling alert escalation"""
        try:
            alert_info = self.active_alerts[alert_id]
            voice_settings = user_config.get_voice_settings()
            
            escalation_delay = voice_settings.get('escalation_delay_seconds', 15)
            auto_call_delay = voice_settings.get('auto_call_delay_seconds', 30)
            auto_call_enabled = voice_settings.get('auto_call_enabled', True)
            
            # Level 0: Initial alert (immediate)
            self._execute_escalation_level_0(alert_info)
            
            # Wait for escalation delay
            for i in range(escalation_delay):
                if alert_info['acknowledged']:
                    logger.info(f"Alert {alert_id} acknowledged, stopping escalation")
                    return
                time.sleep(1)
            
            # Level 1: Enhanced alerts with sound (after 15 seconds)
            if not alert_info['acknowledged']:
                alert_info['escalation_level'] = 1
                self._execute_escalation_level_1(alert_info)
            
            # Wait for auto-call delay
            remaining_time = auto_call_delay - escalation_delay
            for i in range(remaining_time):
                if alert_info['acknowledged']:
                    logger.info(f"Alert {alert_id} acknowledged, stopping escalation")
                    return
                time.sleep(1)
            
            # Level 2: Emergency calling (after 30 seconds total)
            if not alert_info['acknowledged'] and auto_call_enabled:
                alert_info['escalation_level'] = 2
                self._execute_escalation_level_2(alert_info)
            
            # Continue monitoring for 5 minutes
            for i in range(300):  # 5 minutes
                if alert_info['acknowledged']:
                    return
                time.sleep(1)
                
                # Repeat alerts every minute
                if i % 60 == 0 and i > 0:
                    self._repeat_high_priority_alerts(alert_info)
            
        except Exception as e:
            logger.error(f"Escalation worker error for {alert_id}: {e}")
        finally:
            # Cleanup
            if alert_id in self.active_alerts:
                del self.active_alerts[alert_id]
            if alert_id in self.escalation_threads:
                del self.escalation_threads[alert_id]
    
    def _execute_escalation_level_0(self, alert_info):
        """Level 0: Initial alert - standard notifications"""
        logger.info(f"[ESCALATION L0] Initial alert: {alert_info['id']}")
        
        user_info = user_config.get_user_info()
        
        # Send standard alerts
        try:
            send_alert(user_info.get('email', ''), alert_info['message'])
        except Exception as e:
            logger.error(f"Failed to send initial alert: {e}")
        
        # Store offline alert
        self.offline_system.send_offline_alert(
            alert_info['type'],
            alert_info['message'],
            alert_info['location'] or {},
            alert_info['evidence'] or {}
        )
        
        # Play initial sound
        threading.Thread(target=self.play_emergency_sound, args=("beep",), daemon=True).start()
    
    def _execute_escalation_level_1(self, alert_info):
        """Level 1: Enhanced alerts with continuous sound and voice"""
        logger.info(f"[ESCALATION L1] Enhanced alert with sound: {alert_info['id']}")
        
        # Play alarm sound
        threading.Thread(target=self.play_emergency_sound, args=("alarm",), daemon=True).start()
        
        # Voice alert
        voice_message = f"Emergency alert activated. {alert_info['message']}. Press any key to acknowledge."
        threading.Thread(target=self.speak_alert, args=(voice_message,), daemon=True).start()
        
        # Send enhanced notifications
        enhanced_message = f"🚨 ESCALATED ALERT 🚨\n{alert_info['message']}\n\nThis alert has been active for 15 seconds without acknowledgment.\nImmediate attention required!"
        
        user_info = user_config.get_user_info()
        
        # Send to all emergency contacts
        for contact in user_info.get('emergency_contacts', []):
            try:
                send_alert(contact, enhanced_message)
            except Exception as e:
                logger.error(f"Failed to send enhanced alert to {contact}: {e}")
        
        # Create visual alert file
        try:
            alert_file = Path("EMERGENCY_ALERT_ACTIVE.txt")
            alert_file.write_text(f"EMERGENCY ALERT ACTIVE\n\n{enhanced_message}\n\nTime: {datetime.now()}")
        except Exception as e:
            logger.error(f"Failed to create visual alert file: {e}")
    
    def _execute_escalation_level_2(self, alert_info):
        """Level 2: Emergency calling and maximum alerts"""
        logger.info(f"[ESCALATION L2] Emergency calling initiated: {alert_info['id']}")
        
        # Play siren sound
        threading.Thread(target=self.play_emergency_sound, args=("siren",), daemon=True).start()
        
        # Voice alert for calling
        voice_message = "Emergency calling initiated. Contacting emergency services and all emergency contacts."
        threading.Thread(target=self.speak_alert, args=(voice_message,), daemon=True).start()
        
        # Initiate emergency calls
        self._initiate_emergency_calls(alert_info)
        
        # Send maximum priority alerts
        max_priority_message = f"🆘 MAXIMUM PRIORITY EMERGENCY 🆘\n\n{alert_info['message']}\n\nAUTOMATIC EMERGENCY CALLING INITIATED\nAlert active for 30+ seconds without acknowledgment\n\nLocation: {self._format_location(alert_info['location'])}\nTime: {datetime.now()}\n\nCONTACT EMERGENCY SERVICES IMMEDIATELY!"
        
        user_info = user_config.get_user_info()
        
        # Broadcast to everyone
        for contact in user_info.get('emergency_contacts', []):
            try:
                send_alert(contact, max_priority_message)
            except Exception as e:
                logger.error(f"Failed to send max priority alert to {contact}: {e}")
        
        # Create multiple alert files
        try:
            for drive in ['C:', 'D:', 'E:']:
                try:
                    alert_file = Path(f"{drive}/EMERGENCY_CALL_ACTIVE.txt")
                    alert_file.write_text(max_priority_message)
                except:
                    pass
        except Exception as e:
            logger.error(f"Failed to create emergency call files: {e}")
    
    def _initiate_emergency_calls(self, alert_info):
        """Initiate emergency calls to contacts"""
        try:
            user_info = user_config.get_user_info()
            emergency_contacts = user_info.get('emergency_contacts', [])
            
            # For Windows, we can use system calls or web-based calling
            for contact in emergency_contacts[:3]:  # Limit to first 3 contacts
                try:
                    # Try to open default phone app with the number
                    if contact.isdigit() and len(contact) >= 10:
                        if os.name == 'nt':  # Windows
                            # Open phone app with number
                            subprocess.Popen(['start', f'tel:{contact}'], shell=True)
                        else:
                            # For other systems, create a call instruction file
                            call_file = Path(f"CALL_NOW_{contact}.txt")
                            call_file.write_text(f"EMERGENCY: CALL {contact} IMMEDIATELY\n\nAlert: {alert_info['message']}\nTime: {datetime.now()}")
                        
                        logger.info(f"Emergency call initiated to {contact}")
                        time.sleep(2)  # Delay between calls
                except Exception as e:
                    logger.error(f"Failed to initiate call to {contact}: {e}")
        
        except Exception as e:
            logger.error(f"Emergency calling failed: {e}")
    
    def _repeat_high_priority_alerts(self, alert_info):
        """Repeat high priority alerts periodically"""
        try:
            # Play sound reminder
            threading.Thread(target=self.play_emergency_sound, args=("beep",), daemon=True).start()
            
            # Send reminder alert
            reminder_message = f"🔄 ONGOING EMERGENCY ALERT\n\n{alert_info['message']}\n\nAlert has been active for {int((datetime.now() - alert_info['start_time']).total_seconds() / 60)} minutes.\n\nPress any key to acknowledge or contact emergency services."
            
            user_info = user_config.get_user_info()
            send_alert(user_info.get('email', ''), reminder_message)
            
        except Exception as e:
            logger.error(f"Failed to send reminder alert: {e}")
    
    def _format_location(self, location_data):
        """Format location data for alerts"""
        if not location_data:
            return "Location unavailable"
        
        lat = location_data.get('latitude', 'Unknown')
        lon = location_data.get('longitude', 'Unknown')
        address = location_data.get('address', '')
        
        if address:
            return f"{address} ({lat}, {lon})"
        else:
            return f"Coordinates: {lat}, {lon}"
    
    def acknowledge_alert(self, alert_id):
        """Acknowledge an active alert to stop escalation"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id]['acknowledged'] = True
            logger.info(f"Alert {alert_id} acknowledged by user")
            
            # Clean up alert files
            try:
                for file_name in ["EMERGENCY_ALERT_ACTIVE.txt", "EMERGENCY_CALL_ACTIVE.txt"]:
                    alert_file = Path(file_name)
                    if alert_file.exists():
                        alert_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to clean up alert files: {e}")
            
            return True
        return False
    
    def acknowledge_all_alerts(self):
        """Acknowledge all active alerts"""
        count = 0
        for alert_id in list(self.active_alerts.keys()):
            if self.acknowledge_alert(alert_id):
                count += 1
        return count
    
    def get_active_alerts(self):
        """Get list of currently active alerts"""
        return list(self.active_alerts.keys())
    
    def stop_all_escalations(self):
        """Stop all active escalations"""
        for alert_id in list(self.active_alerts.keys()):
            self.acknowledge_alert(alert_id)
        logger.info("All escalations stopped")


# Global escalation system instance
escalation_system = EscalationSystem()