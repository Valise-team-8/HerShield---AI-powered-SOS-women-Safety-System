#!/usr/bin/env python3
"""
Ultra-fast voice recognition test
"""

import speech_recognition as sr
import time

def test_ultra_fast_voice():
    print("🎤 Testing ultra-fast voice recognition...")
    
    try:
        r = sr.Recognizer()
        mic = sr.Microphone()
        
        # Ultra-fast settings
        with mic as source:
            print("🔧 Quick calibration...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            
        r.energy_threshold = 200
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.4
        r.phrase_threshold = 0.1
        r.non_speaking_duration = 0.3
        
        print(f"✅ Settings: Energy={r.energy_threshold}, Pause={r.pause_threshold}")
        
        keywords = ["help", "emergency", "danger", "police", "fire", "sos"]
        
        print(f"\n🎯 Say one of these words: {', '.join(keywords)}")
        print("🗣️ Speak now (ultra-fast detection)...")
        
        for i in range(20):  # 20 quick attempts
            try:
                print(f"[{i+1}/20] Listening...")
                start_time = time.time()
                
                with mic as source:
                    audio = r.listen(source, timeout=0.5, phrase_time_limit=2)
                
                print("🔄 Processing...")
                process_start = time.time()
                
                text = r.recognize_google(audio, language='en-IN').lower()
                
                total_time = time.time() - start_time
                process_time = time.time() - process_start
                
                print(f"✅ Recognized in {total_time:.2f}s (process: {process_time:.2f}s): '{text}'")
                
                # Check keywords
                found_keywords = [kw for kw in keywords if kw in text]
                if found_keywords:
                    print(f"🚨 EMERGENCY KEYWORDS: {found_keywords}")
                    print(f"⚡ Total detection time: {total_time:.2f} seconds")
                    print("✅ Ultra-fast voice detection working!")
                    return True
                elif "stop" in text or "quit" in text:
                    print("🛑 Test stopped")
                    return False
                else:
                    print(f"ℹ️ No keywords in: '{text}'")
                
            except sr.WaitTimeoutError:
                print("⏰ Timeout")
            except sr.UnknownValueError:
                print("❓ No speech")
            except sr.RequestError as e:
                print(f"🌐 API error: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("⚠️ No keywords detected in test")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_microphone_setup():
    """Test microphone setup and sensitivity"""
    print("\n🔧 Testing microphone setup...")
    
    try:
        r = sr.Recognizer()
        mic = sr.Microphone()
        
        print("📋 Available microphones:")
        for i, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  {i}: {name}")
        
        print("\n🔧 Testing energy levels...")
        with mic as source:
            print("🔇 Measuring ambient noise...")
            r.adjust_for_ambient_noise(source, duration=1)
            
        print(f"✅ Energy threshold: {r.energy_threshold}")
        
        print("\n🗣️ Say something to test detection...")
        with mic as source:
            try:
                audio = r.listen(source, timeout=3, phrase_time_limit=2)
                print("✅ Audio captured successfully")
                
                text = r.recognize_google(audio)
                print(f"✅ Recognition test: '{text}'")
                
            except sr.WaitTimeoutError:
                print("⏰ No speech detected")
            except Exception as e:
                print(f"❌ Recognition failed: {e}")
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")

if __name__ == "__main__":
    print("🎤 Ultra-Fast Voice Recognition Test")
    print("=" * 50)
    
    test_microphone_setup()
    
    print("\n" + "=" * 50)
    success = test_ultra_fast_voice()
    
    if success:
        print("\n🎉 Ultra-fast voice detection is working!")
    else:
        print("\n⚠️ Voice detection needs optimization.")
        
    print("\n💡 Tips for better detection:")
    print("• Speak clearly and loudly")
    print("• Use simple words: 'help', 'emergency'")
    print("• Minimize background noise")
    print("• Check microphone permissions")