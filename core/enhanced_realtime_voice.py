#!/usr/bin/env python3
"""
Enhanced Real-Time Voice Detection System for HerShield
Ultra-fast, accurate, and responsive voice monitoring with advanced features
"""

import threading
import time
import queue
import numpy as np
from datetime import datetime
import json
import os

# Optional imports with fallbacks
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    print("⚠️ Speech recognition not available")
    SPEECH_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    print("⚠️ PyAudio not available")
    PYAUDIO_AVAILABLE = False

try:
    import webrtcvad
    WEBRTC_AVAILABLE = True
except ImportError:
    print("⚠️ WebRTC VAD not available - using basic voice detection")
    WEBRTC_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    print("⚠️ Librosa not available - advanced audio analysis disabled")
    LIBROSA_AVAILABLE = False


class EnhancedRealtimeVoiceDetector:
    """Enhanced real-time voice detection with multiple engines and optimizations"""
    
    def __init__(self, callback_function=None):
        self.callback_function = callback_function
        self.is_listening = False
        self.audio_queue = queue.Queue(maxsize=10)  # Limit queue size
        self.recognition_threads = []
        
        # Audio settings optimized for real-time performance
        self.CHUNK = 1024  # Optimal chunk size for balance of latency/quality
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # Standard rate for speech recognition
        
        # Voice Activity Detection settings
        self.vad_enabled = WEBRTC_AVAILABLE
        if self.vad_enabled:
            self.vad = webrtcvad.Vad(2)  # Aggressiveness level 0-3
        
        # Recognition engines (multiple for redundancy)
        self.recognition_engines = ['google', 'sphinx']  # Add more as needed
        
        # Enhanced keyword sets for different urgency levels
        self.critical_keywords = [
            "help", "emergency", "police", "fire", "ambulance", "911", "100", "108",
            "save me", "call police", "attack", "rape", "kidnap", "murder", "kill me"
        ]
        
        self.high_priority_keywords = [
            "danger", "scared", "afraid", "hurt", "pain", "stop it", "get away",
            "leave me alone", "don't touch me", "no means no", "get off me"
        ]
        
        self.medium_priority_keywords = [
            "unsafe", "uncomfortable", "worried", "nervous", "anxious", "trapped",
            "lost", "stranded", "alone", "isolated", "suspicious person"
        ]
        
        # Performance metrics
        self.stats = {
            'total_detections': 0,
            'false_positives': 0,
            'response_times': [],
            'recognition_accuracy': 0.0,
            'uptime_start': None
        }
        
        # Audio preprocessing settings
        self.noise_reduction_enabled = True
        self.auto_gain_control = True
        self.echo_cancellation = True
        
        print("🚀 Enhanced Real-Time Voice Detector initialized")
    
    def start_monitoring(self, keywords=None):
        """Start enhanced real-time voice monitoring"""
        if not SPEECH_AVAILABLE or not PYAUDIO_AVAILABLE:
            print("❌ Required audio libraries not available")
            return False
        
        if keywords:
            # Merge provided keywords with built-in sets
            self.critical_keywords.extend(keywords)
        
        self.is_listening = True
        self.stats['uptime_start'] = datetime.now()
        
        try:
            # Start audio capture thread
            audio_thread = threading.Thread(target=self._audio_capture_loop, daemon=True)
            audio_thread.start()
            
            # Start multiple recognition threads for parallel processing
            for i in range(2):  # Use 2 threads for better responsiveness
                recognition_thread = threading.Thread(
                    target=self._recognition_loop, 
                    args=(f"thread_{i}",), 
                    daemon=True
                )
                recognition_thread.start()
                self.recognition_threads.append(recognition_thread)
            
            # Start voice activity detection thread
            if self.vad_enabled:
                vad_thread = threading.Thread(target=self._vad_loop, daemon=True)
                vad_thread.start()
            
            print("✅ Enhanced real-time monitoring started")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start monitoring: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop voice monitoring"""
        self.is_listening = False
        
        # Clear audio queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        print("🛑 Enhanced real-time monitoring stopped")
        self._print_stats()
    
    def _audio_capture_loop(self):
        """Enhanced audio capture with preprocessing"""
        try:
            p = pyaudio.PyAudio()
            
            # Find best microphone
            best_device = self._find_best_microphone(p)
            
            # Open audio stream with optimal settings
            stream = p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=best_device,
                frames_per_buffer=self.CHUNK,
                stream_callback=None
            )
            
            print(f"🎤 Audio stream opened (device: {best_device})")
            
            # Audio buffer for continuous processing
            audio_buffer = []
            buffer_duration = 2.0  # 2 seconds of audio
            buffer_size = int(self.RATE * buffer_duration)
            
            # Noise baseline for adaptive thresholding
            noise_samples = []
            noise_baseline = 0
            
            while self.is_listening:
                try:
                    # Read audio data
                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # Preprocess audio
                    if self.noise_reduction_enabled:
                        audio_data = self._reduce_noise(audio_data, noise_baseline)
                    
                    if self.auto_gain_control:
                        audio_data = self._apply_agc(audio_data)
                    
                    # Add to buffer
                    audio_buffer.extend(audio_data)
                    
                    # Maintain buffer size
                    if len(audio_buffer) > buffer_size:
                        audio_buffer = audio_buffer[-buffer_size:]
                    
                    # Voice Activity Detection
                    energy = np.sqrt(np.mean(audio_data**2))
                    
                    # Adaptive noise baseline
                    if len(noise_samples) < 50:  # First 50 chunks for baseline
                        noise_samples.append(energy)
                        noise_baseline = np.mean(noise_samples) * 2  # 2x noise as threshold
                    
                    # Enhanced voice detection
                    if self._is_voice_detected(audio_data, energy, noise_baseline):
                        # Send audio for recognition if buffer has enough data
                        if len(audio_buffer) >= self.RATE:  # At least 1 second
                            try:
                                # Create audio segment for recognition
                                audio_segment = audio_buffer[-int(self.RATE * 1.5):]  # Last 1.5 seconds
                                self.audio_queue.put_nowait({
                                    'audio': audio_segment.copy(),
                                    'timestamp': time.time(),
                                    'energy': energy
                                })
                            except queue.Full:
                                # Remove oldest item and add new one
                                try:
                                    self.audio_queue.get_nowait()
                                    self.audio_queue.put_nowait({
                                        'audio': audio_segment.copy(),
                                        'timestamp': time.time(),
                                        'energy': energy
                                    })
                                except queue.Empty:
                                    pass
                
                except Exception as e:
                    print(f"Audio capture error: {e}")
                    time.sleep(0.1)
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            print(f"Audio capture loop failed: {e}")
    
    def _recognition_loop(self, thread_name):
        """Enhanced recognition loop with multiple engines"""
        r = sr.Recognizer()
        
        # Optimize recognizer settings (using tested working values)
        r.energy_threshold = 150
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.8
        r.phrase_threshold = 0.3
        r.non_speaking_duration = 0.8
        
        print(f"🔊 Recognition thread {thread_name} started")
        
        while self.is_listening:
            try:
                # Get audio from queue
                try:
                    audio_item = self.audio_queue.get(timeout=1.0)  # Longer timeout
                except queue.Empty:
                    continue
                
                audio_data = audio_item['audio']
                timestamp = audio_item['timestamp']
                
                # Convert to AudioData
                audio_bytes = np.array(audio_data, dtype=np.int16).tobytes()
                audio = sr.AudioData(audio_bytes, self.RATE, 2)
                
                # Try multiple recognition engines
                recognition_results = []
                
                # Primary: Google Speech Recognition
                try:
                    start_time = time.time()
                    text = r.recognize_google(audio, language='en-IN').lower()
                    recognition_time = time.time() - start_time
                    recognition_results.append({
                        'engine': 'google',
                        'text': text,
                        'time': recognition_time,
                        'confidence': 0.9  # Google doesn't provide confidence
                    })
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"Google recognition error: {e}")
                
                # Fallback: Sphinx (offline)
                if not recognition_results:
                    try:
                        start_time = time.time()
                        text = r.recognize_sphinx(audio).lower()
                        recognition_time = time.time() - start_time
                        recognition_results.append({
                            'engine': 'sphinx',
                            'text': text,
                            'time': recognition_time,
                            'confidence': 0.7  # Lower confidence for offline
                        })
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError:
                        pass
                
                # Process recognition results
                for result in recognition_results:
                    self._process_recognition_result(result, timestamp, thread_name)
                
            except Exception as e:
                print(f"Recognition loop error ({thread_name}): {e}")
                time.sleep(0.1)
    
    def _process_recognition_result(self, result, timestamp, thread_name):
        """Process recognition result and check for keywords"""
        text = result['text']
        engine = result['engine']
        recognition_time = result['time']
        
        print(f"🔊 [{thread_name}] [{engine}] ({recognition_time:.2f}s): '{text}'")
        
        # Enhanced keyword detection with priority levels
        detected_keywords = {
            'critical': [],
            'high': [],
            'medium': []
        }
        
        # Check critical keywords (immediate response)
        for keyword in self.critical_keywords:
            if keyword in text:
                detected_keywords['critical'].append(keyword)
        
        # Check high priority keywords
        for keyword in self.high_priority_keywords:
            if keyword in text:
                detected_keywords['high'].append(keyword)
        
        # Check medium priority keywords
        for keyword in self.medium_priority_keywords:
            if keyword in text:
                detected_keywords['medium'].append(keyword)
        
        # Determine alert level
        if detected_keywords['critical']:
            alert_level = 'CRITICAL'
            keywords_found = detected_keywords['critical']
        elif detected_keywords['high']:
            alert_level = 'HIGH'
            keywords_found = detected_keywords['high']
        elif detected_keywords['medium']:
            alert_level = 'MEDIUM'
            keywords_found = detected_keywords['medium']
        else:
            return  # No keywords detected
        
        # Calculate total response time
        total_response_time = time.time() - timestamp
        
        print(f"🚨 {alert_level} ALERT: {keywords_found} (response: {total_response_time:.2f}s)")
        
        # Update statistics
        self.stats['total_detections'] += 1
        self.stats['response_times'].append(total_response_time)
        
        # Stop listening for critical alerts
        if alert_level == 'CRITICAL':
            self.is_listening = False
        
        # Trigger callback
        if self.callback_function:
            alert_data = {
                'text': text,
                'keywords': keywords_found,
                'alert_level': alert_level,
                'engine': engine,
                'recognition_time': recognition_time,
                'total_response_time': total_response_time,
                'timestamp': timestamp,
                'thread': thread_name
            }
            
            try:
                self.callback_function(alert_data)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def _find_best_microphone(self, p):
        """Find the best available microphone"""
        try:
            device_count = p.get_device_count()
            best_device = None
            
            for i in range(device_count):
                device_info = p.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    # Prefer USB or high-quality microphones
                    device_name = device_info['name'].lower()
                    if any(keyword in device_name for keyword in ['usb', 'blue', 'rode', 'audio-technica']):
                        best_device = i
                        break
                    elif best_device is None:
                        best_device = i
            
            return best_device
        except:
            return None  # Use default
    
    def _reduce_noise(self, audio_data, noise_baseline):
        """Simple noise reduction"""
        try:
            # Basic noise gate
            threshold = max(noise_baseline, 100)
            audio_data = np.where(np.abs(audio_data) < threshold, 0, audio_data)
            return audio_data
        except:
            return audio_data
    
    def _apply_agc(self, audio_data):
        """Apply automatic gain control"""
        try:
            # Normalize audio to prevent clipping
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                target_level = 16000  # Target amplitude
                gain = min(target_level / max_val, 2.0)  # Limit gain to 2x
                audio_data = (audio_data * gain).astype(np.int16)
            return audio_data
        except:
            return audio_data
    
    def _is_voice_detected(self, audio_data, energy, noise_baseline):
        """Enhanced voice activity detection"""
        # Energy-based detection
        if energy < noise_baseline:
            return False
        
        # WebRTC VAD if available
        if self.vad_enabled:
            try:
                # Convert to bytes for WebRTC VAD
                audio_bytes = audio_data.tobytes()
                # WebRTC VAD expects 10ms, 20ms, or 30ms frames
                frame_duration = 30  # ms
                frame_size = int(self.RATE * frame_duration / 1000)
                
                if len(audio_data) >= frame_size:
                    frame = audio_data[:frame_size].tobytes()
                    is_speech = self.vad.is_speech(frame, self.RATE)
                    return is_speech and energy > noise_baseline
            except:
                pass
        
        # Fallback to energy + zero crossing rate
        try:
            zcr = np.mean(np.abs(np.diff(np.sign(audio_data))))
            return energy > noise_baseline and 0.01 < zcr < 0.5
        except:
            return energy > noise_baseline
    
    def _vad_loop(self):
        """Voice Activity Detection loop for optimization"""
        # This could be used for more advanced VAD features
        pass
    
    def _print_stats(self):
        """Print performance statistics"""
        if self.stats['uptime_start']:
            uptime = datetime.now() - self.stats['uptime_start']
            print(f"\n📊 Enhanced Voice Detection Statistics:")
            print(f"   Uptime: {uptime}")
            print(f"   Total detections: {self.stats['total_detections']}")
            
            if self.stats['response_times']:
                avg_response = np.mean(self.stats['response_times'])
                min_response = np.min(self.stats['response_times'])
                max_response = np.max(self.stats['response_times'])
                print(f"   Response times: avg={avg_response:.2f}s, min={min_response:.2f}s, max={max_response:.2f}s")
    
    def get_stats(self):
        """Get current statistics"""
        stats = self.stats.copy()
        if stats['uptime_start']:
            stats['uptime'] = (datetime.now() - stats['uptime_start']).total_seconds()
        return stats


def test_enhanced_voice_detection():
    """Test the enhanced voice detection system"""
    print("🧪 Testing Enhanced Real-Time Voice Detection")
    
    def alert_callback(alert_data):
        print(f"🚨 ALERT TRIGGERED:")
        print(f"   Text: '{alert_data['text']}'")
        print(f"   Keywords: {alert_data['keywords']}")
        print(f"   Level: {alert_data['alert_level']}")
        print(f"   Engine: {alert_data['engine']}")
        print(f"   Response time: {alert_data['total_response_time']:.2f}s")
    
    detector = EnhancedRealtimeVoiceDetector(callback_function=alert_callback)
    
    if detector.start_monitoring():
        print("🎤 Say something with keywords like 'help', 'emergency', 'danger'...")
        print("Press Ctrl+C to stop")
        
        try:
            while detector.is_listening:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping detection...")
            detector.stop_monitoring()
    else:
        print("❌ Failed to start enhanced voice detection")


if __name__ == "__main__":
    test_enhanced_voice_detection()