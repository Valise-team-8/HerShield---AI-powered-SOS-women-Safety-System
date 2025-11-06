#!/usr/bin/env python3
"""
Test voice recognition accuracy
"""

import speech_recognition as sr
import time

def test_voice_accuracy():
    print("🎤 Testing voice recognition accuracy...")
    print("📋 This will help you test the improved voice detection")
    
    try:
        r = sr.Recognizer()
        mic = sr.Microphone()
        
        # Use same settings as main app
        with mic as source:
            print("🔧 Calibrating microphone...")
            r.adjust_for_ambient_noise(source, duration=1.0)
            r.energy_threshold = 300
            r.dynamic_energy_threshold = True
            r.pause_threshold = 0.8
            r.phrase_threshold = 0.3
            
        print(f"✅ Microphone calibrated. Energy threshold: {r.energy_threshold}")
        
        # Test keywords
        keywords = [
            "help", "emergency", "danger", "police", "fire", "ambulance",
            "help me", "save me", "call police", "need help", "please help",
            "attack", "stop", "get away", "sos"
        ]
        
        print(f"\n🎯 Testing keywords: {', '.join(keywords[:10])}...")
        print("🗣️ Say one of these words clearly:")
        
        for i in range(10):  # 10 attempts
            try:
                print(f"\n[{i+1}/10] Listening... (say 'help', 'emergency', or 'stop test')")
                
                with mic as source:
                    audio = r.listen(source, timeout=3, phrase_time_limit=4)
                
                print("🔄 Processing...")
                
                # Try multiple recognition methods
                text = None
                
                try:
                    text = r.recognize_google(audio, language='en-IN').lower()
                    print(f"✅ Recognized (en-IN): '{text}'")
                except:
                    try:
                        text = r.recognize_google(audio, language='en-US').lower()
                        print(f"✅ Recognized (en-US): '{text}'")
                    except:
                        try:
                            text = r.recognize_google(audio).lower()
                            print(f"✅ Recognized (auto): '{text}'")
                        except:
                            print("❌ Could not recognize speech")
                            continue
                
                if text:
                    # Check for keywords
                    found_keywords = [kw for kw in keywords if kw in text]
                    
                    if found_keywords:
                        print(f"🚨 EMERGENCY KEYWORDS DETECTED: {found_keywords}")
                        print("✅ Voice detection would trigger alert!")
                        break
                    elif "stop test" in text:
                        print("🛑 Test stopped by user")
                        break
                    else:
                        print(f"ℹ️ No emergency keywords in: '{text}'")
                
            except sr.WaitTimeoutError:
                print("⏰ Timeout - no speech detected")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n🎉 Voice accuracy test completed!")
        print("\n📋 Tips for better recognition:")
        print("• Speak clearly and loudly")
        print("• Use simple words like 'help' or 'emergency'")
        print("• Avoid background noise")
        print("• Make sure microphone permissions are enabled")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_voice_accuracy()