#!/usr/bin/env python3
"""
Real-time voice detection test
"""

import pyaudio
import numpy as np
import speech_recognition as sr
import threading
import queue
import time

def test_realtime_voice():
    print("🎤 Testing REAL-TIME voice detection...")
    
    try:
        # Audio settings
        CHUNK = 512
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        print(f"📋 Audio devices: {p.get_device_count()}")
        
        # Audio queue
        audio_queue = queue.Queue(maxsize=5)
        
        # Open stream
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print("✅ Real-time audio stream started")
        print("🗣️ Say 'help', 'emergency', or 'danger'...")
        
        # Keywords
        keywords = ["help", "emergency", "danger", "police", "fire", "sos"]
        
        # Recognition thread
        def recognition_worker():
            r = sr.Recognizer()
            
            while True:
                try:
                    audio_buffer = audio_queue.get(timeout=1)
                    
                    # Convert to AudioData
                    audio_bytes = np.array(audio_buffer, dtype=np.int16).tobytes()
                    audio = sr.AudioData(audio_bytes, RATE, 2)
                    
                    # Quick recognition
                    start_time = time.time()
                    text = r.recognize_google(audio, language='en-IN').lower()
                    recognition_time = time.time() - start_time
                    
                    print(f"🔊 [{recognition_time:.1f}s] Heard: '{text}'")
                    
                    # Check keywords
                    found_keywords = [kw for kw in keywords if kw in text]
                    if found_keywords:
                        print(f"🚨 EMERGENCY DETECTED: {found_keywords}")
                        print(f"⚡ Total time: {recognition_time:.1f} seconds")
                        return True
                    elif "stop" in text or "quit" in text:
                        print("🛑 Test stopped")
                        return False
                        
                except queue.Empty:
                    continue
                except sr.UnknownValueError:
                    pass
                except Exception as e:
                    print(f"Recognition error: {e}")
                    
        # Start recognition thread
        recognition_thread = threading.Thread(target=recognition_worker, daemon=True)
        recognition_thread.start()
        
        # Audio buffer
        audio_buffer = []
        buffer_size = RATE * 2  # 2 seconds
        
        # Main audio loop
        for i in range(300):  # 30 seconds max
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Add to buffer
                audio_buffer.extend(audio_data)
                
                # Keep buffer size
                if len(audio_buffer) > buffer_size:
                    audio_buffer = audio_buffer[-buffer_size:]
                
                # Voice activity detection
                energy = np.sqrt(np.mean(audio_data**2))
                
                if energy > 300:  # Voice detected
                    if len(audio_buffer) >= RATE:  # 1 second of audio
                        try:
                            audio_queue.put_nowait(audio_buffer.copy())
                        except queue.Full:
                            pass
                
                # Show energy level occasionally
                if i % 50 == 0:
                    print(f"🔊 Energy: {energy:.0f} {'🎤' if energy > 300 else '🔇'}")
                    
            except Exception as e:
                print(f"Audio error: {e}")
                break
        
        # Cleanup
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        print("✅ Real-time test completed")
        
    except Exception as e:
        print(f"❌ Real-time test failed: {e}")

if __name__ == "__main__":
    print("🚀 Real-Time Voice Detection Test")
    print("=" * 40)
    
    try:
        test_realtime_voice()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        
    print("\n💡 This shows how the real-time system works:")
    print("• Continuous audio monitoring")
    print("• Voice activity detection")
    print("• Background speech recognition")
    print("• Instant keyword matching")