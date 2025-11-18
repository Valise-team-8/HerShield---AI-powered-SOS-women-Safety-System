#!/usr/bin/env python3
"""
AI 7-Second Window Analyzer
During the 7-second confirmation window, AI analyzes:
- Screams and distress sounds
- Heavy breathing
- Crash/impact sounds
- Video distress indicators
- Auto-confirms if user cannot double-tap
"""

import time
import threading
import numpy as np

try:
    import speech_recognition as sr
    import librosa
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    import cv2
    from core.distress_detection import distress_detector
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False


class AI7SecondAnalyzer:
    """
    Analyzes audio and video during 7-second window
    Auto-confirms emergency if high distress detected
    """
    
    def __init__(self):
        self.analyzing = False
        self.analysis_results = {
            'scream_detected': False,
            'heavy_breathing': False,
            'crash_detected': False,
            'video_distress': False,
            'distress_score': 0,
            'auto_confirm': False
        }
        
        # Thresholds for auto-confirmation
        self.auto_confirm_threshold = 70  # Score above this = auto-confirm
    
    def start_analysis(self, duration=7, callback=None):
        """
        Start 7-second AI analysis
        
        Args:
            duration: Analysis duration in seconds
            callback: Function to call with results
        """
        if self.analyzing:
            return False
        
        self.analyzing = True
        self.analysis_results = {
            'scream_detected': False,
            'heavy_breathing': False,
            'crash_detected': False,
            'video_distress': False,
            'distress_score': 0,
            'auto_confirm': False
        }
        
        # Start analysis threads
        audio_thread = threading.Thread(
            target=self._analyze_audio,
            args=(duration,),
            daemon=True
        )
        
        video_thread = threading.Thread(
            target=self._analyze_video,
            args=(duration,),
            daemon=True
        )
        
        audio_thread.start()
        video_thread.start()
        
        # Monitor and callback
        def monitor():
            start_time = time.time()
            while time.time() - start_time < duration and self.analyzing:
                time.sleep(0.5)
                
                # Check if auto-confirm threshold reached
                if self.analysis_results['distress_score'] >= self.auto_confirm_threshold:
                    self.analysis_results['auto_confirm'] = True
                    self.analyzing = False
                    if callback:
                        callback(self.analysis_results)
                    return
            
            self.analyzing = False
            if callback:
                callback(self.analysis_results)
        
        threading.Thread(target=monitor, daemon=True).start()
        return True
    
    def stop_analysis(self):
        """Stop analysis"""
        self.analyzing = False
    
    def _analyze_audio(self, duration):
        """Analyze audio for screams, breathing, crashes"""
        if not AUDIO_AVAILABLE:
            return
        
        try:
            import pyaudio
            
            # Audio parameters
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            
            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            start_time = time.time()
            
            while time.time() - start_time < duration and self.analyzing:
                try:
                    # Read audio chunk
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    # Analyze chunk
                    self._analyze_audio_chunk(audio_data, RATE)
                    
                except Exception as e:
                    print(f"Audio chunk error: {e}")
                    continue
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            print(f"Audio analysis error: {e}")
    
    def _analyze_audio_chunk(self, audio_data, sample_rate):
        """Analyze single audio chunk for distress indicators"""
        try:
            # Calculate energy (volume)
            energy = np.sqrt(np.mean(audio_data**2))
            
            # Calculate frequency using zero-crossing rate
            zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_data)))) / 2
            frequency = zero_crossings * sample_rate / len(audio_data)
            
            # Detect scream (high frequency + high energy)
            if frequency > 800 and energy > 0.3:
                self.analysis_results['scream_detected'] = True
                self.analysis_results['distress_score'] += 30
                print("🚨 SCREAM DETECTED!")
            
            # Detect heavy breathing (low frequency + rhythmic pattern)
            if 100 < frequency < 300 and energy > 0.15:
                self.analysis_results['heavy_breathing'] = True
                self.analysis_results['distress_score'] += 20
                print("😰 HEAVY BREATHING DETECTED!")
            
            # Detect crash/impact (very high energy + broad spectrum)
            if energy > 0.5:
                self.analysis_results['crash_detected'] = True
                self.analysis_results['distress_score'] += 25
                print("💥 CRASH/IMPACT DETECTED!")
            
        except Exception as e:
            print(f"Audio chunk analysis error: {e}")
    
    def _analyze_video(self, duration):
        """Analyze video for distress indicators"""
        if not VIDEO_AVAILABLE:
            return
        
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                return
            
            start_time = time.time()
            frame_count = 0
            
            while time.time() - start_time < duration and self.analyzing:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                frame_count += 1
                
                # Analyze every 3rd frame for performance
                if frame_count % 3 == 0:
                    result = distress_detector.analyze_frame(frame)
                    
                    if result['distress_detected']:
                        self.analysis_results['video_distress'] = True
                        self.analysis_results['distress_score'] += result['distress_score']
                        print(f"📹 VIDEO DISTRESS: {result['indicators']}")
                
                time.sleep(0.1)
            
            cap.release()
            
        except Exception as e:
            print(f"Video analysis error: {e}")
    
    def get_results(self):
        """Get current analysis results"""
        return self.analysis_results.copy()


# Global instance
ai_analyzer = AI7SecondAnalyzer()
