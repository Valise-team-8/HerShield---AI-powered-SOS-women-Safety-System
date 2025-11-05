#!/usr/bin/env python3
"""
AI-based Threat Detection System
Detects distress sounds, screams, crashes, and unusual audio patterns
Uses offline machine learning models for real-time threat assessment
"""

import numpy as np
import librosa
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import pickle
import os
import threading
import time
from collections import deque
import logging

class AudioThreatDetector:
    """AI-powered audio threat detection system"""
    
    def __init__(self):
        self.sample_rate = 16000
        self.frame_length = 2048
        self.hop_length = 512
        self.n_mels = 128
        
        # Audio buffer for continuous analysis
        self.audio_buffer = deque(maxlen=self.sample_rate * 5)  # 5 seconds
        self.threat_threshold = 0.7
        self.is_monitoring = False
        
        # Load or initialize models
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.load_models()
        
        # Threat patterns (pre-trained features)
        self.threat_patterns = self._initialize_threat_patterns()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _initialize_threat_patterns(self):
        """Initialize known threat audio patterns"""
        return {
            'scream': {
                'freq_range': (300, 3000),  # Hz
                'intensity_threshold': 0.8,
                'duration_min': 0.5,  # seconds
                'spectral_rolloff_threshold': 0.85
            },
            'crash': {
                'freq_range': (100, 8000),
                'intensity_threshold': 0.9,
                'duration_min': 0.2,
                'spectral_centroid_threshold': 2000
            },
            'breaking_glass': {
                'freq_range': (2000, 15000),
                'intensity_threshold': 0.7,
                'duration_min': 0.1,
                'high_freq_energy_threshold': 0.6
            },
            'struggle_sounds': {
                'freq_range': (50, 2000),
                'intensity_threshold': 0.6,
                'duration_min': 1.0,
                'irregularity_threshold': 0.8
            }
        }

    def extract_audio_features(self, audio_data):
        """Extract comprehensive audio features for threat detection"""
        try:
            # Ensure audio is the right format
            if len(audio_data) < self.frame_length:
                return None
                
            # Basic spectral features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=self.sample_rate)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
            
            # Energy and intensity features
            rms_energy = librosa.feature.rms(y=audio_data)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=self.sample_rate)
            
            # Advanced features for threat detection
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=self.sample_rate)
            mel_spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=self.sample_rate, n_mels=self.n_mels)
            
            # Aggregate features
            features = np.concatenate([
                np.mean(mfccs, axis=1),
                np.std(mfccs, axis=1),
                [np.mean(spectral_centroid), np.std(spectral_centroid)],
                [np.mean(spectral_rolloff), np.std(spectral_rolloff)],
                [np.mean(zero_crossing_rate), np.std(zero_crossing_rate)],
                [np.mean(rms_energy), np.std(rms_energy)],
                [np.mean(spectral_bandwidth), np.std(spectral_bandwidth)],
                np.mean(chroma, axis=1),
                [np.mean(mel_spectrogram), np.std(mel_spectrogram)]
            ])
            
            return features
            
        except Exception as e:
            self.logger.error(f"Feature extraction error: {e}")
            return None

    def detect_specific_threats(self, audio_data, features):
        """Detect specific types of threats based on audio characteristics"""
        threats_detected = []
        
        try:
            # Calculate additional metrics
            fft = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(fft), 1/self.sample_rate)
            magnitude = np.abs(fft)
            
            # Scream detection
            if self._detect_scream(audio_data, freqs, magnitude):
                threats_detected.append(('scream', 0.9))
            
            # Crash/impact detection
            if self._detect_crash(audio_data, freqs, magnitude):
                threats_detected.append(('crash', 0.85))
            
            # Glass breaking detection
            if self._detect_glass_breaking(freqs, magnitude):
                threats_detected.append(('breaking_glass', 0.8))
            
            # Struggle/fight sounds
            if self._detect_struggle_sounds(audio_data, features):
                threats_detected.append(('struggle_sounds', 0.75))
            
            return threats_detected
            
        except Exception as e:
            self.logger.error(f"Threat detection error: {e}")
            return []

    def _detect_scream(self, audio_data, freqs, magnitude):
        """Detect scream patterns in audio"""
        pattern = self.threat_patterns['scream']
        
        # Check frequency range
        freq_mask = (freqs >= pattern['freq_range'][0]) & (freqs <= pattern['freq_range'][1])
        freq_energy = np.sum(magnitude[freq_mask]) / np.sum(magnitude)
        
        # Check intensity
        rms = np.sqrt(np.mean(audio_data**2))
        
        # Check spectral characteristics typical of screams
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=self.sample_rate)
        rolloff_ratio = np.mean(spectral_rolloff) / (self.sample_rate / 2)
        
        return (freq_energy > 0.3 and 
                rms > pattern['intensity_threshold'] and 
                rolloff_ratio > pattern['spectral_rolloff_threshold'])

    def _detect_crash(self, audio_data, freqs, magnitude):
        """Detect crash/impact sounds"""
        pattern = self.threat_patterns['crash']
        
        # Sudden onset detection
        onset_frames = librosa.onset.onset_detect(y=audio_data, sr=self.sample_rate)
        
        # High energy across wide frequency range
        freq_mask = (freqs >= pattern['freq_range'][0]) & (freqs <= pattern['freq_range'][1])
        broad_spectrum_energy = np.sum(magnitude[freq_mask]) / np.sum(magnitude)
        
        # Peak intensity
        rms = np.sqrt(np.mean(audio_data**2))
        
        return (len(onset_frames) > 0 and 
                broad_spectrum_energy > 0.6 and 
                rms > pattern['intensity_threshold'])

    def _detect_glass_breaking(self, freqs, magnitude):
        """Detect glass breaking sounds"""
        pattern = self.threat_patterns['breaking_glass']
        
        # High frequency energy characteristic of glass breaking
        high_freq_mask = freqs >= pattern['freq_range'][0]
        high_freq_energy = np.sum(magnitude[high_freq_mask]) / np.sum(magnitude)
        
        return high_freq_energy > pattern['high_freq_energy_threshold']

    def _detect_struggle_sounds(self, audio_data, features):
        """Detect struggle/fight sounds"""
        pattern = self.threat_patterns['struggle_sounds']
        
        # Irregular patterns and sustained activity
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
        irregularity = np.std(zero_crossing_rate)
        
        # Sustained energy in lower frequencies
        rms = np.sqrt(np.mean(audio_data**2))
        
        return (irregularity > pattern['irregularity_threshold'] and 
                rms > pattern['intensity_threshold'])

    def analyze_audio_chunk(self, audio_chunk):
        """Analyze a chunk of audio for threats"""
        if len(audio_chunk) < self.frame_length:
            return None, []
        
        # Extract features
        features = self.extract_audio_features(audio_chunk)
        if features is None:
            return None, []
        
        # Anomaly detection
        try:
            features_scaled = self.scaler.transform([features])
            anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
            is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1
        except:
            anomaly_score = 0
            is_anomaly = False
        
        # Specific threat detection
        specific_threats = self.detect_specific_threats(audio_chunk, features)
        
        # Calculate overall threat level
        threat_level = 0
        if is_anomaly:
            threat_level += 0.3
        
        if specific_threats:
            max_threat_score = max([score for _, score in specific_threats])
            threat_level += max_threat_score
        
        threat_level = min(threat_level, 1.0)  # Cap at 1.0
        
        return threat_level, specific_threats

    def load_models(self):
        """Load pre-trained models or initialize new ones"""
        model_dir = "data/models"
        os.makedirs(model_dir, exist_ok=True)
        
        scaler_path = os.path.join(model_dir, "audio_scaler.pkl")
        detector_path = os.path.join(model_dir, "anomaly_detector.pkl")
        
        try:
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
            
            if os.path.exists(detector_path):
                with open(detector_path, 'rb') as f:
                    self.anomaly_detector = pickle.load(f)
            else:
                # Initialize with some baseline data
                self._initialize_baseline_model()
                
        except Exception as e:
            self.logger.warning(f"Could not load models: {e}. Using defaults.")
            self._initialize_baseline_model()

    def _initialize_baseline_model(self):
        """Initialize baseline model with synthetic normal audio features"""
        # Generate synthetic normal audio features for initial training
        normal_features = []
        for _ in range(100):
            # Simulate normal ambient audio features
            features = np.random.normal(0, 0.1, 45)  # 45 features total
            normal_features.append(features)
        
        normal_features = np.array(normal_features)
        self.scaler.fit(normal_features)
        self.anomaly_detector.fit(normal_features)
        
        # Save the initialized models
        self.save_models()

    def save_models(self):
        """Save trained models"""
        model_dir = "data/models"
        os.makedirs(model_dir, exist_ok=True)
        
        try:
            with open(os.path.join(model_dir, "audio_scaler.pkl"), 'wb') as f:
                pickle.dump(self.scaler, f)
            
            with open(os.path.join(model_dir, "anomaly_detector.pkl"), 'wb') as f:
                pickle.dump(self.anomaly_detector, f)
                
        except Exception as e:
            self.logger.error(f"Could not save models: {e}")

    def update_model_with_feedback(self, audio_features, is_threat):
        """Update model based on user feedback"""
        try:
            if is_threat:
                # This was a real threat - adjust anomaly detector
                pass  # Isolation Forest doesn't support online learning
            else:
                # This was normal audio - add to normal patterns
                features_scaled = self.scaler.transform([audio_features])
                # Could retrain periodically with accumulated data
                
        except Exception as e:
            self.logger.error(f"Model update error: {e}")

class ThreatDetectionSystem:
    """Main threat detection system coordinator"""
    
    def __init__(self, alert_callback=None):
        self.audio_detector = AudioThreatDetector()
        self.alert_callback = alert_callback
        self.is_active = False
        self.detection_thread = None
        
        # Detection history for reducing false positives
        self.recent_detections = deque(maxlen=10)
        self.confirmation_threshold = 2  # Require 2 detections in recent history

    def start_monitoring(self):
        """Start continuous threat monitoring"""
        if self.is_active:
            return
        
        self.is_active = True
        self.detection_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.detection_thread.start()
        print("[AI THREAT DETECTOR] Monitoring started")

    def stop_monitoring(self):
        """Stop threat monitoring"""
        self.is_active = False
        if self.detection_thread:
            self.detection_thread.join(timeout=2)
        print("[AI THREAT DETECTOR] Monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        import pyaudio
        
        # Audio stream setup
        chunk_size = 1024
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 16000
        
        p = pyaudio.PyAudio()
        
        try:
            stream = p.open(
                format=audio_format,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk_size
            )
            
            print("[AI THREAT DETECTOR] Audio stream active")
            
            while self.is_active:
                try:
                    # Read audio chunk
                    audio_data = stream.read(chunk_size, exception_on_overflow=False)
                    audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    # Add to buffer
                    self.audio_detector.audio_buffer.extend(audio_array)
                    
                    # Analyze when we have enough data
                    if len(self.audio_detector.audio_buffer) >= self.audio_detector.sample_rate * 2:  # 2 seconds
                        buffer_array = np.array(list(self.audio_detector.audio_buffer))
                        threat_level, specific_threats = self.audio_detector.analyze_audio_chunk(buffer_array)
                        
                        if threat_level and threat_level > self.audio_detector.threat_threshold:
                            self._handle_threat_detection(threat_level, specific_threats)
                    
                    time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                    
                except Exception as e:
                    print(f"[AI THREAT DETECTOR ERROR] {e}")
                    time.sleep(1)
            
        except Exception as e:
            print(f"[AI THREAT DETECTOR FATAL ERROR] {e}")
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass
            p.terminate()

    def _handle_threat_detection(self, threat_level, specific_threats):
        """Handle detected threats with confirmation logic"""
        current_time = time.time()
        
        # Add to recent detections
        self.recent_detections.append({
            'time': current_time,
            'level': threat_level,
            'threats': specific_threats
        })
        
        # Check for confirmation (multiple recent detections)
        recent_count = sum(1 for d in self.recent_detections 
                          if current_time - d['time'] < 5.0 and d['level'] > 0.6)
        
        if recent_count >= self.confirmation_threshold:
            threat_types = []
            for detection in self.recent_detections:
                for threat_type, _ in detection['threats']:
                    if threat_type not in threat_types:
                        threat_types.append(threat_type)
            
            threat_description = f"AI detected audio threats: {', '.join(threat_types) if threat_types else 'anomalous audio'}"
            
            print(f"[THREAT CONFIRMED] Level: {threat_level:.2f}, Types: {threat_types}")
            
            # Trigger alert
            if self.alert_callback:
                self.alert_callback(threat_description)
            
            # Clear recent detections to prevent spam
            self.recent_detections.clear()

# Example usage
if __name__ == "__main__":
    def test_alert_callback(threat_description):
        print(f"🚨 ALERT TRIGGERED: {threat_description}")
    
    detector = ThreatDetectionSystem(alert_callback=test_alert_callback)
    
    try:
        detector.start_monitoring()
        print("Monitoring for threats... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        detector.stop_monitoring()
        print("Monitoring stopped")