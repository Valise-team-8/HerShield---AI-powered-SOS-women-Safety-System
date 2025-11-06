#!/usr/bin/env python3
"""
Debug Voice Detection - Find and fix voice recognition issues
"""

import time
import numpy as np

def debug_microphone():
    """Debug microphone and audio input"""
    print("🔍 Debugging Microphone and Audio Input")
    print("=" * 50)
    
    try:
        import pyaudio
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        print(f"📊 PyAudio Info:")
        print(f"   Version: {pyaudio.__version__}")
        print(f"   Device Count: {p.get_device_count()}")
        
        # List all audio devices
        print(f"\n🎤 Available Audio Devices:")
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"   [{i}] {device_info['name']}")
                print(f"       Max Input Channels: {device_info['maxInputChannels']}")
                print(f"       Default Sample Rate: {device_info['defaultSampleRate']}")
        
        # Test default microphone
        print(f"\n🧪 Testing Default Microphone...")
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        try:
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            print("✅ Microphone stream opened successfully")
            
            # Test audio capture for 5 seconds
            print("🎤 Recording audio for 5 seconds... (speak now)")
            
            max_energy = 0
            min_energy = float('inf')
            energy_samples = []
            
            for i in range(int(RATE / CHUNK * 5)):  # 5 seconds
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # Calculate energy
                    energy = np.sqrt(np.mean(audio_data.astype(np.float64)**2))
                    energy_samples.append(energy)
                    
                    max_energy = max(max_energy, energy)
                    min_energy = min(min_energy, energy)
                    
                    # Show real-time energy
                    if i % 10 == 0:  # Every ~0.6 seconds
                        print(f"   Energy: {energy:.1f} {'🔊' if energy > 500 else '🔇'}")
                
                except Exception as e:
                    print(f"   Audio read error: {e}")
            
            stream.stop_stream()
            stream.close()
            
            # Analysis
            avg_energy = np.mean(energy_samples)
            print(f"\n📊 Audio Analysis:")
            print(f"   Average Energy: {avg_energy:.1f}")
            print(f"   Max Energy: {max_energy:.1f}")
            print(f"   Min Energy: {min_energy:.1f}")
            print(f"   Energy Range: {max_energy - min_energy:.1f}")
            
            # Recommendations
            if max_energy < 100:
                print("⚠️  Very low audio levels - check microphone volume")
            elif max_energy < 500:
                print("⚠️  Low audio levels - try speaking louder")
            elif max_energy > 10000:
                print("⚠️  Very high audio levels - may cause clipping")
            else:
                print("✅ Good audio levels detected")
            
            # Suggest threshold
            suggested_threshold = avg_energy * 2
            print(f"💡 Suggested voice threshold: {suggested_threshold:.1f}")
            
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
        
        p.terminate()
        
    except ImportError:
        print("❌ PyAudio not available")
    except Exception as e:
        print(f"❌ Audio debug failed: {e}")


def debug_speech_recognition():
    """Debug speech recognition engines"""
    print("\n🔍 Debugging Speech Recognition")
    print("=" * 50)
    
    try:
        import speech_recognition as sr
        
        print(f"📊 SpeechRecognition Info:")
        print(f"   Version: {sr.__version__}")
        
        # Test microphone list
        try:
            mic_list = sr.Microphone.list_microphone_names()
            print(f"   Available Microphones: {len(mic_list)}")
            for i, name in enumerate(mic_list[:5]):  # Show first 5
                print(f"     [{i}] {name}")
        except Exception as e:
            print(f"   Microphone list error: {e}")
        
        # Test recognition engines
        print(f"\n🤖 Testing Recognition Engines:")
        
        r = sr.Recognizer()
        
        # Test with a short recording
        try:
            with sr.Microphone() as source:
                print("🎤 Adjusting for ambient noise... (be quiet)")
                r.adjust_for_ambient_noise(source, duration=1)
                print(f"   Energy threshold set to: {r.energy_threshold}")
                
                print("🗣️  Say something now (you have 3 seconds)...")
                audio = r.listen(source, timeout=1, phrase_time_limit=3)
                print("✅ Audio captured successfully")
                
                # Test Google recognition
                try:
                    print("🌐 Testing Google Speech Recognition...")
                    start_time = time.time()
                    text = r.recognize_google(audio, language='en-US')
                    recognition_time = time.time() - start_time
                    print(f"   ✅ Google: '{text}' ({recognition_time:.2f}s)")
                except sr.UnknownValueError:
                    print("   ⚠️  Google: Could not understand audio")
                except sr.RequestError as e:
                    print(f"   ❌ Google: Request error - {e}")
                
                # Test Sphinx recognition
                try:
                    print("🔧 Testing Sphinx (offline) Recognition...")
                    start_time = time.time()
                    text = r.recognize_sphinx(audio)
                    recognition_time = time.time() - start_time
                    print(f"   ✅ Sphinx: '{text}' ({recognition_time:.2f}s)")
                except sr.UnknownValueError:
                    print("   ⚠️  Sphinx: Could not understand audio")
                except sr.RequestError as e:
                    print(f"   ❌ Sphinx: {e}")
                
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout")
        except Exception as e:
            print(f"❌ Recognition test failed: {e}")
            
    except ImportError:
        print("❌ SpeechRecognition not available")
    except Exception as e:
        print(f"❌ Speech recognition debug failed: {e}")


def test_keyword_detection():
    """Test keyword detection with lower thresholds"""
    print("\n🔍 Testing Keyword Detection")
    print("=" * 50)
    
    try:
        import speech_recognition as sr
        
        r = sr.Recognizer()
        
        # Lower thresholds for better sensitivity
        r.energy_threshold = 100  # Much lower threshold
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.3
        r.phrase_threshold = 0.1
        r.non_speaking_duration = 0.2
        
        print(f"🔧 Optimized Settings:")
        print(f"   Energy Threshold: {r.energy_threshold}")
        print(f"   Pause Threshold: {r.pause_threshold}")
        print(f"   Phrase Threshold: {r.phrase_threshold}")
        
        keywords = ["help", "emergency", "test", "hello", "danger"]
        print(f"🎯 Test Keywords: {keywords}")
        
        with sr.Microphone() as source:
            print("🎤 Calibrating microphone...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            print(f"   New energy threshold: {r.energy_threshold}")
        
        print("\n🗣️  Say test keywords (10 second test)...")
        print("   Try: 'hello', 'test', 'help', 'emergency'")
        
        start_time = time.time()
        detections = 0
        
        while time.time() - start_time < 10:
            try:
                with sr.Microphone() as source:
                    # Very short timeout for responsiveness
                    audio = r.listen(source, timeout=0.1, phrase_time_limit=2)
                
                # Quick recognition
                try:
                    text = r.recognize_google(audio, language='en-US').lower()
                    print(f"🔊 Heard: '{text}'")
                    
                    # Check for keywords
                    found_keywords = [kw for kw in keywords if kw in text]
                    if found_keywords:
                        detections += 1
                        print(f"🚨 KEYWORD DETECTED: {found_keywords}")
                    
                except sr.UnknownValueError:
                    pass  # No speech understood
                except sr.RequestError as e:
                    print(f"Recognition error: {e}")
                    
            except sr.WaitTimeoutError:
                pass  # No speech detected, continue
            except Exception as e:
                print(f"Listen error: {e}")
        
        print(f"\n📊 Test Results:")
        print(f"   Total keyword detections: {detections}")
        print(f"   Test duration: 10 seconds")
        
        if detections == 0:
            print("⚠️  No keywords detected. Possible issues:")
            print("   • Microphone volume too low")
            print("   • Background noise too high")
            print("   • Internet connection issues (for Google)")
            print("   • Need to speak more clearly")
        else:
            print("✅ Keyword detection working!")
            
    except Exception as e:
        print(f"❌ Keyword detection test failed: {e}")


def main():
    """Run all debug tests"""
    print("🛡️ HerShield Voice Detection Debug Tool")
    print("🔍 Identifying and fixing voice recognition issues")
    print()
    
    # Run debug tests
    debug_microphone()
    debug_speech_recognition()
    test_keyword_detection()
    
    print("\n🎯 Debug Summary and Recommendations:")
    print("=" * 50)
    print("1. Check microphone permissions in Windows settings")
    print("2. Ensure microphone is not muted or volume too low")
    print("3. Test in a quiet environment first")
    print("4. Speak clearly and at normal volume")
    print("5. Check internet connection for Google recognition")
    print("6. Try different microphones if available")
    print("\n💡 If issues persist, try running as administrator")


if __name__ == "__main__":
    main()