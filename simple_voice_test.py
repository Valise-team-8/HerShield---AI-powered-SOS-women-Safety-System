#!/usr/bin/env python3
"""
Simple Voice Test - Test basic voice recognition with working settings
"""

import speech_recognition as sr
import time

def simple_voice_test():
    """Simple voice recognition test that actually works"""
    print("🎤 Simple Voice Recognition Test")
    print("=" * 40)
    
    r = sr.Recognizer()
    
    # Use settings that work based on debug results
    r.energy_threshold = 100  # Lower threshold
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8  # Longer pause for better detection
    r.phrase_threshold = 0.3
    r.non_speaking_duration = 0.8
    
    keywords = ["help", "emergency", "test", "hello", "danger", "police", "fire"]
    
    print(f"🎯 Keywords to detect: {keywords}")
    print(f"🔧 Energy threshold: {r.energy_threshold}")
    
    with sr.Microphone() as source:
        print("🎤 Calibrating microphone...")
        r.adjust_for_ambient_noise(source, duration=1)
        print(f"   Adjusted energy threshold: {r.energy_threshold}")
    
    print("\n🗣️  Speak clearly and say keywords...")
    print("   Press Ctrl+C to stop")
    
    detections = 0
    
    try:
        while True:
            try:
                with sr.Microphone() as source:
                    print("🎧 Listening...")
                    # Longer timeout and phrase limit for better detection
                    audio = r.listen(source, timeout=2, phrase_time_limit=5)
                
                print("🔄 Processing...")
                
                # Use Google recognition (we know it works)
                try:
                    start_time = time.time()
                    text = r.recognize_google(audio, language='en-US').lower()
                    recognition_time = time.time() - start_time
                    
                    print(f"🔊 Recognized ({recognition_time:.2f}s): '{text}'")
                    
                    # Check for keywords
                    found_keywords = []
                    for keyword in keywords:
                        if keyword in text:
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        detections += 1
                        print(f"🚨 KEYWORDS DETECTED: {found_keywords}")
                        print(f"   Total detections: {detections}")
                    else:
                        print("   No keywords found")
                    
                except sr.UnknownValueError:
                    print("❓ Could not understand audio")
                except sr.RequestError as e:
                    print(f"❌ Recognition error: {e}")
                    
            except sr.WaitTimeoutError:
                print("⏰ No speech detected, listening again...")
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Test stopped. Total detections: {detections}")


def continuous_voice_test():
    """Continuous voice monitoring test"""
    print("\n🔄 Continuous Voice Monitoring Test")
    print("=" * 40)
    
    r = sr.Recognizer()
    
    # Optimized settings for continuous monitoring
    r.energy_threshold = 150
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.5
    r.phrase_threshold = 0.2
    r.non_speaking_duration = 0.5
    
    keywords = ["help", "emergency", "danger", "police", "fire", "save me"]
    
    print(f"🎯 Emergency keywords: {keywords}")
    
    with sr.Microphone() as source:
        print("🎤 Calibrating for continuous monitoring...")
        r.adjust_for_ambient_noise(source, duration=1)
        print(f"   Energy threshold: {r.energy_threshold}")
    
    print("\n🚨 Emergency voice monitoring active!")
    print("   Say emergency keywords to trigger alerts")
    print("   Press Ctrl+C to stop")
    
    alerts = 0
    
    try:
        while True:
            try:
                with sr.Microphone() as source:
                    # Quick listening for emergency detection
                    audio = r.listen(source, timeout=1, phrase_time_limit=3)
                
                # Fast recognition
                try:
                    text = r.recognize_google(audio, language='en-US').lower()
                    print(f"🔊 '{text}'")
                    
                    # Emergency keyword detection
                    found_keywords = [kw for kw in keywords if kw in text]
                    
                    if found_keywords:
                        alerts += 1
                        print(f"🚨 EMERGENCY ALERT #{alerts}: {found_keywords}")
                        print(f"   Text: '{text}'")
                        print(f"   ⚠️  This would trigger emergency protocol!")
                        
                        # In real app, this would trigger emergency response
                        
                except sr.UnknownValueError:
                    pass  # No speech, continue monitoring
                except sr.RequestError as e:
                    print(f"Recognition error: {e}")
                    
            except sr.WaitTimeoutError:
                pass  # Continue monitoring
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(0.5)
                
    except KeyboardInterrupt:
        print(f"\n🛑 Monitoring stopped. Total alerts: {alerts}")


if __name__ == "__main__":
    print("🛡️ HerShield Voice Recognition Tests")
    print("🎤 Testing voice detection with working settings")
    print()
    
    # Run simple test first
    simple_voice_test()
    
    # Then continuous monitoring test
    continuous_voice_test()
    
    print("\n✅ Voice tests completed!")
    print("💡 Use these settings in the main application for better detection")