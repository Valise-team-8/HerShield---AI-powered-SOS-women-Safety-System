#!/usr/bin/env python3
"""
Reliable Voice Detection System - Simple and crash-resistant
"""

import speech_recognition as sr
import time
import threading

class ReliableVoiceDetector:
    """Simple, reliable voice detection that won't crash"""
    
    def __init__(self, callback_function=None):
        self.callback_function = callback_function
        self.is_listening = False
        self.detection_thread = None
        
        # Emergency keywords
        self.keywords = [
            "help", "emergency", "danger", "police", "fire", "ambulance",
            "save me", "call police", "need help", "attack", "stop it",
            "sos", "urgent", "crisis"
        ]
        
        print("🛡️ Reliable Voice Detector initialized")
    
    def start_monitoring(self):
        """Start reliable voice monitoring"""
        if not sr:
            print("❌ Speech recognition not available")
            return False
        
        self.is_listening = True
        
        # Start detection thread
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        
        print("✅ Reliable voice monitoring started")
        return True
    
    def stop_monitoring(self):
        """Stop voice monitoring"""
        self.is_listening = False
        print("🛑 Reliable voice monitoring stopped")
    
    def _detection_loop(self):
        """Main detection loop with error handling"""
        r = sr.Recognizer()
        
        # Use proven working settings
        r.energy_threshold = 150
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.8
        r.phrase_threshold = 0.3
        r.non_speaking_duration = 0.8
        
        mic = sr.Microphone()
        
        # Calibrate microphone
        try:
            with mic as source:
                print("🎤 Calibrating microphone...")
                r.adjust_for_ambient_noise(source, duration=1)
                print(f"   Energy threshold: {r.energy_threshold}")
        except Exception as e:
            print(f"Calibration error: {e}")
            return
        
        detections = 0
        consecutive_errors = 0
        max_errors = 5
        
        print(f"🎯 Monitoring for keywords: {self.keywords}")
        
        while self.is_listening and consecutive_errors < max_errors:
            try:
                with mic as source:
                    print("🎧 Listening...")
                    # Use reliable timeout settings
                    audio = r.listen(source, timeout=2, phrase_time_limit=5)
                
                print("🔄 Processing...")
                
                # Use Google recognition (proven to work)
                try:
                    start_time = time.time()
                    text = r.recognize_google(audio, language='en-US').lower()
                    recognition_time = time.time() - start_time
                    
                    print(f"🔊 Recognized ({recognition_time:.2f}s): '{text}'")
                    
                    # Check for keywords
                    found_keywords = []
                    for keyword in self.keywords:
                        if keyword in text:
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        detections += 1
                        print(f"🚨 KEYWORDS DETECTED: {found_keywords}")
                        
                        # Call callback if provided
                        if self.callback_function:
                            try:
                                alert_data = {
                                    'text': text,
                                    'keywords': found_keywords,
                                    'detection_count': detections,
                                    'recognition_time': recognition_time
                                }
                                self.callback_function(alert_data)
                            except Exception as e:
                                print(f"Callback error: {e}")
                        
                        # Stop after detection for safety
                        self.is_listening = False
                        break
                    else:
                        print("   No keywords detected")
                    
                    consecutive_errors = 0  # Reset error counter
                    
                except sr.UnknownValueError:
                    print("❓ Could not understand audio")
                    consecutive_errors = 0  # This is not an error
                except sr.RequestError as e:
                    print(f"❌ Recognition error: {e}")
                    consecutive_errors += 1
                    time.sleep(1)
                
            except sr.WaitTimeoutError:
                print("⏰ No speech detected")
                consecutive_errors = 0  # This is not an error
            except Exception as e:
                print(f"⚠️ Detection error: {e}")
                consecutive_errors += 1
                time.sleep(0.5)
        
        if consecutive_errors >= max_errors:
            print("❌ Too many errors, stopping detection")
        
        print(f"🛑 Detection stopped. Total detections: {detections}")


def test_reliable_detection():
    """Test the reliable voice detection"""
    print("🧪 Testing Reliable Voice Detection")
    print("=" * 40)
    
    def alert_callback(alert_data):
        print(f"\n🚨 ALERT TRIGGERED!")
        print(f"   Text: '{alert_data['text']}'")
        print(f"   Keywords: {alert_data['keywords']}")
        print(f"   Detection #: {alert_data['detection_count']}")
        print(f"   Response time: {alert_data['recognition_time']:.2f}s")
        print("   ⚠️ This would trigger emergency protocol!")
    
    detector = ReliableVoiceDetector(callback_function=alert_callback)
    
    if detector.start_monitoring():
        print("\n🗣️ Say emergency keywords like:")
        print("   'help', 'emergency', 'danger', 'police'")
        print("\n⌨️ Press Ctrl+C to stop")
        
        try:
            while detector.is_listening:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            detector.stop_monitoring()
    else:
        print("❌ Failed to start detection")


if __name__ == "__main__":
    test_reliable_detection()