#!/usr/bin/env python3
"""
Simple voice recognition test
"""

import speech_recognition as sr
import time

def test_voice():
    print("🎤 Testing voice recognition...")
    
    try:
        r = sr.Recognizer()
        mic = sr.Microphone()
        
        print("📋 Available microphones:")
        for i, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  {i}: {name}")
        
        print("\n🔧 Calibrating microphone...")
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1)
            
        print(f"✅ Energy threshold: {r.energy_threshold}")
        print("\n🎤 Say 'help' or 'emergency' now...")
        
        keywords = ["help", "emergency", "danger", "police", "save me"]
        
        for i in range(10):  # Listen for 10 attempts
            try:
                print(f"[{i+1}/10] Listening...")
                with mic as source:
                    audio = r.listen(source, timeout=2, phrase_time_limit=3)
                
                print("🔄 Processing...")
                text = r.recognize_google(audio).lower()
                print(f"🔊 Heard: '{text}'")
                
                # Check for keywords
                found_keywords = [kw for kw in keywords if kw in text]
                if found_keywords:
                    print(f"🚨 EMERGENCY KEYWORDS DETECTED: {found_keywords}")
                    print("✅ Voice recognition is working!")
                    return True
                    
            except sr.WaitTimeoutError:
                print("⏰ Timeout - no speech detected")
            except sr.UnknownValueError:
                print("❓ Could not understand audio")
            except sr.RequestError as e:
                print(f"❌ Recognition error: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
        print("⚠️ No emergency keywords detected in test")
        return False
        
    except Exception as e:
        print(f"❌ Voice test failed: {e}")
        return False

if __name__ == "__main__":
    test_voice()