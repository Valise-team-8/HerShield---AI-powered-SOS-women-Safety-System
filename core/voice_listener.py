import speech_recognition as sr
import threading
import time
import uuid
from datetime import datetime
from core.alert_manager import send_alert
from core.ai_threat_detector import ThreatDetectionSystem
from core.offline_speech_recognition import HybridSpeechRecognizer
from core.offline_alert_system import OfflineAlertSystem
from core.escalation_system import escalation_system
from core.user_config import user_config
from core.enhanced_location_service import EnhancedLocationService
from core.camera_capture import capture_emergency_evidence

# Enhanced keywords for domestic violence and danger situations
KEYWORDS = [
    "help", "save me", "emergency", "police", "fire", "ambulance", "danger", "attack",
    "stop it", "get away", "leave me alone", "don't touch me", "no means no", "get off me",
    "somebody help", "call police", "he's hurting me", "she's hurting me", "domestic violence",
    "abuse", "stalker", "following me", "threatening me", "kidnap", "rape", "assault",
    "harassment", "violence", "beating me", "choking me", "hitting me", "forcing me",
    "won't let me go", "locked in", "can't escape", "being held", "against my will",
    "unsafe", "in danger", "need help now", "call 911", "call emergency", "mayday", "sos"
]

class EnhancedVoiceListener:
    """Enhanced voice listener with AI threat detection and offline capabilities"""
    
    def __init__(self, user_email):
        self.user_email = user_email
        self.is_listening = False
        
        # Initialize components
        self.threat_detector = ThreatDetectionSystem(alert_callback=self.handle_ai_threat)
        self.hybrid_recognizer = HybridSpeechRecognizer()
        self.offline_alert_system = OfflineAlertSystem()
        self.location_service = EnhancedLocationService()
        
        # Start offline alert listener
        self.offline_alert_system.start_alert_listener()
        
        print("[ENHANCED VOICE LISTENER] Initialized with AI threat detection and escalation system")

    def handle_ai_threat(self, threat_description):
        """Handle AI-detected threats with escalation"""
        print(f"[AI THREAT DETECTED] {threat_description}")
        
        # Generate unique alert ID
        alert_id = f"ai_threat_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Get current location and capture evidence
        location_data = self._get_emergency_location()
        evidence_data = self._capture_emergency_evidence()
        
        # Create comprehensive alert message
        alert_message = f"🤖 AI THREAT DETECTED: {threat_description}\n\nAutomatic threat detection system has identified potential danger.\nLocation: {self._format_location_brief(location_data)}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nImmediate response required!"
        
        # Start escalation process
        escalation_system.start_escalation(
            alert_id=alert_id,
            alert_type='ai_threat_detection',
            message=alert_message,
            location_data=location_data,
            evidence_data=evidence_data
        )
        
        print(f"[ESCALATION STARTED] Alert ID: {alert_id}")

    def handle_keyword_detection(self, text, keywords, source):
        """Handle detected keywords with escalation system"""
        print(f"[KEYWORD DETECTED] '{', '.join(keywords)}' via {source} in: '{text}'")
        
        # Generate unique alert ID
        alert_id = f"voice_keyword_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Get current location and capture evidence
        location_data = self._get_emergency_location()
        evidence_data = self._capture_emergency_evidence()
        
        # Determine severity based on keywords
        severity = self._assess_keyword_severity(keywords)
        
        # Create comprehensive alert message
        alert_message = f"🎤 VOICE EMERGENCY DETECTED\n\nKeywords: {', '.join(keywords)}\nFull text: \"{text}\"\nDetection method: {source}\nSeverity: {severity}\n\nLocation: {self._format_location_brief(location_data)}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nImmediate assistance required!"
        
        # Start escalation process
        escalation_system.start_escalation(
            alert_id=alert_id,
            alert_type='voice_keyword_detection',
            message=alert_message,
            location_data=location_data,
            evidence_data=evidence_data
        )
        
        print(f"[ESCALATION STARTED] Alert ID: {alert_id} | Severity: {severity}")
    
    def _get_emergency_location(self):
        """Get current location for emergency"""
        try:
            return self.location_service.get_emergency_location_info()
        except Exception as e:
            print(f"[LOCATION ERROR] {e}")
            return None
    
    def _capture_emergency_evidence(self):
        """Capture emergency evidence"""
        try:
            return capture_emergency_evidence()
        except Exception as e:
            print(f"[EVIDENCE ERROR] {e}")
            return None
    
    def _format_location_brief(self, location_data):
        """Format location data briefly"""
        if not location_data:
            return "Location unavailable"
        
        if location_data.get('address'):
            return location_data['address']
        elif location_data.get('latitude') and location_data.get('longitude'):
            return f"{location_data['latitude']:.4f}, {location_data['longitude']:.4f}"
        else:
            return "Location unavailable"
    
    def _assess_keyword_severity(self, keywords):
        """Assess severity level based on detected keywords"""
        high_severity_keywords = [
            "rape", "kidnap", "assault", "violence", "beating me", "choking me", 
            "hitting me", "forcing me", "being held", "against my will", "can't escape",
            "domestic violence", "abuse", "threatening me", "stalker"
        ]
        
        medium_severity_keywords = [
            "help", "save me", "emergency", "danger", "attack", "hurt", "scared",
            "trapped", "unsafe", "in danger", "need help now"
        ]
        
        # Check for high severity keywords
        for keyword in keywords:
            if any(high_kw in keyword.lower() for high_kw in high_severity_keywords):
                return "CRITICAL"
        
        # Check for medium severity keywords
        for keyword in keywords:
            if any(med_kw in keyword.lower() for med_kw in medium_severity_keywords):
                return "HIGH"
        
        return "MEDIUM"

    def start_monitoring(self):
        """Start comprehensive monitoring (voice + AI threat detection)"""
        if self.is_listening:
            return
        
        self.is_listening = True
        
        # Start AI threat detection
        self.threat_detector.start_monitoring()
        
        # Start hybrid speech recognition
        self.speech_thread = threading.Thread(
            target=self._speech_monitoring_loop, 
            daemon=True
        )
        self.speech_thread.start()
        
        print("[MONITORING STARTED] Voice keywords + AI threat detection active")
        print("Listening for:")
        print(f"  • Keywords: {', '.join(KEYWORDS)}")
        print("  • Screams, crashes, breaking glass, struggle sounds")
        print("  • Unusual audio patterns")
        print("Press Ctrl+C to stop.")

    def stop_monitoring(self):
        """Stop all monitoring"""
        self.is_listening = False
        
        # Stop AI threat detection
        self.threat_detector.stop_monitoring()
        
        # Stop offline alert system
        self.offline_alert_system.stop_monitoring()
        
        print("[MONITORING STOPPED] All systems deactivated")

    def _speech_monitoring_loop(self):
        """Speech recognition monitoring loop"""
        try:
            # Use hybrid recognition with fallback
            self.hybrid_recognizer.listen_for_keywords_hybrid(
                KEYWORDS, 
                callback=self.handle_keyword_detection
            )
        except Exception as e:
            print(f"[SPEECH MONITORING ERROR] {e}")
            # Fallback to basic recognition
            self._basic_speech_loop()

    def _basic_speech_loop(self):
        """Optimized speech recognition with faster response"""
        r = sr.Recognizer()
        mic = sr.Microphone()
        
        # Optimize recognizer settings for speed
        r.energy_threshold = 300  # Lower threshold for faster detection
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.5  # Shorter pause detection
        r.phrase_threshold = 0.3  # Faster phrase detection
        
        print("[OPTIMIZED] Fast speech recognition active")
        
        while self.is_listening:
            try:
                with mic as source:
                    # Quick ambient noise adjustment
                    r.adjust_for_ambient_noise(source, duration=0.2)
                    # Shorter listening timeout for faster response
                    audio = r.listen(source, timeout=0.5, phrase_time_limit=3)

                try:
                    # Try Google Speech API with faster processing
                    text = r.recognize_google(audio, language='en-IN').lower()
                    print(f"[HEARD] {text}")

                    # Immediate keyword check - no delay
                    found_keywords = [kw for kw in KEYWORDS if kw in text]
                    if found_keywords:
                        # Process immediately in separate thread for instant response
                        threading.Thread(
                            target=self.handle_keyword_detection,
                            args=(text, found_keywords, "google_api_fast"),
                            daemon=True
                        ).start()
                        
                except sr.UnknownValueError:
                    pass  # No speech recognized
                except sr.RequestError as e:
                    print(f"[SPEECH API ERROR] {e}")
                    # Could try offline recognition here as backup
                    
            except sr.WaitTimeoutError:
                pass  # Continue listening - no delay
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[SPEECH LOOP ERROR] {e}")
                time.sleep(0.1)  # Minimal delay on error

def listen_for_keyword(user_email):
    """
    Enhanced voice monitoring with AI threat detection and offline capabilities.
    Maintains backward compatibility with existing code.
    """
    listener = EnhancedVoiceListener(user_email)
    
    try:
        listener.start_monitoring()
        
        # Keep running until interrupted
        while listener.is_listening:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[STOPPED] Monitoring interrupted by user")
    finally:
        listener.stop_monitoring()

# Backward compatibility - simple keyword detection
def simple_listen_for_keyword(user_email):
    """Simple keyword detection (original functionality)"""
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("[LISTENING] Voice monitoring started. Say 'help', 'save me', or 'emergency'...")

    while True:
        try:
            with mic as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, phrase_time_limit=5)

            try:
                text = r.recognize_google(audio).lower()
                print(f"[HEARD] {text}")

                for word in KEYWORDS:
                    if word in text:
                        print(f"[ALERT TRIGGERED] Keyword '{word}' detected.")
                        send_alert(user_email, reason=f"Detected keyword: '{word}'")
                        return  # stop after one alert
            except sr.UnknownValueError:
                pass  # no valid speech recognized
            except sr.RequestError as e:
                print(f"[ERROR] Speech Recognition API error: {e}")
        except KeyboardInterrupt:
            print("\n[STOPPED] Listening manually interrupted.")
            break
