#!/usr/bin/env python3
"""
Offline Speech Recognition System
Uses Vosk for offline speech recognition as backup to Google Speech API
Supports multiple languages and works without internet connection
"""

import json
import os
import pyaudio
import vosk
import threading
import time
from collections import deque
import logging

class OfflineSpeechRecognizer:
    """Offline speech recognition using Vosk"""
    
    def __init__(self, model_path=None, language="en-us"):
        self.language = language
        self.model_path = model_path or self._get_model_path()
        self.model = None
        self.recognizer = None
        self.is_listening = False
        self.keywords = ["help", "save me", "emergency", "police", "fire", "ambulance", "danger", "attack"]
        
        # Audio configuration
        self.sample_rate = 16000
        self.chunk_size = 4096
        
        # Results buffer
        self.recent_results = deque(maxlen=10)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self._initialize_model()

    def _get_model_path(self):
        """Get path for Vosk model"""
        model_dir = "data/vosk_models"
        os.makedirs(model_dir, exist_ok=True)
        
        # Default English model path
        if self.language == "en-us":
            return os.path.join(model_dir, "vosk-model-en-us-0.22")
        elif self.language == "en-in":
            return os.path.join(model_dir, "vosk-model-en-in-0.5")
        else:
            return os.path.join(model_dir, f"vosk-model-{self.language}")

    def _initialize_model(self):
        """Initialize Vosk model"""
        try:
            if not os.path.exists(self.model_path):
                self.logger.warning(f"Vosk model not found at {self.model_path}")
                self.logger.info("Please download a Vosk model:")
                self.logger.info("1. Visit https://alphacephei.com/vosk/models")
                self.logger.info("2. Download a model (e.g., vosk-model-en-us-0.22)")
                self.logger.info(f"3. Extract to {self.model_path}")
                return False
            
            self.model = vosk.Model(self.model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            
            # Configure recognizer for keywords
            keyword_grammar = {
                "type": "grammar",
                "rules": [
                    {"name": "emergency", "words": self.keywords}
                ]
            }
            
            self.logger.info("Offline speech recognition initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Vosk model: {e}")
            return False

    def is_available(self):
        """Check if offline recognition is available"""
        return self.model is not None and self.recognizer is not None

    def recognize_audio_chunk(self, audio_data):
        """Recognize speech from audio chunk"""
        if not self.is_available():
            return None
        
        try:
            # Convert audio data to bytes if needed
            if isinstance(audio_data, bytes):
                audio_bytes = audio_data
            else:
                # Assume numpy array, convert to bytes
                audio_bytes = (audio_data * 32767).astype('int16').tobytes()
            
            # Process audio
            if self.recognizer.AcceptWaveform(audio_bytes):
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '').strip()
                if text:
                    self.recent_results.append({
                        'text': text,
                        'confidence': result.get('confidence', 0.5),
                        'timestamp': time.time()
                    })
                    return text
            else:
                # Partial result
                partial = json.loads(self.recognizer.PartialResult())
                return partial.get('partial', '')
                
        except Exception as e:
            self.logger.error(f"Recognition error: {e}")
            return None

    def check_for_keywords(self, text):
        """Check if text contains emergency keywords"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords

    def start_continuous_recognition(self, callback=None):
        """Start continuous speech recognition"""
        if self.is_listening or not self.is_available():
            return False
        
        self.is_listening = True
        self.recognition_thread = threading.Thread(
            target=self._recognition_loop, 
            args=(callback,), 
            daemon=True
        )
        self.recognition_thread.start()
        self.logger.info("Continuous offline recognition started")
        return True

    def stop_continuous_recognition(self):
        """Stop continuous recognition"""
        self.is_listening = False
        if hasattr(self, 'recognition_thread'):
            self.recognition_thread.join(timeout=2)
        self.logger.info("Continuous recognition stopped")

    def _recognition_loop(self, callback):
        """Main recognition loop"""
        p = pyaudio.PyAudio()
        
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.logger.info("Audio stream started for offline recognition")
            
            while self.is_listening:
                try:
                    audio_data = stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    # Recognize speech
                    text = self.recognize_audio_chunk(audio_data)
                    
                    if text:
                        self.logger.info(f"Recognized (offline): {text}")
                        
                        # Check for keywords
                        keywords_found = self.check_for_keywords(text)
                        
                        if keywords_found and callback:
                            callback(text, keywords_found, "offline")
                    
                    time.sleep(0.01)  # Small delay
                    
                except Exception as e:
                    self.logger.error(f"Recognition loop error: {e}")
                    time.sleep(1)
            
        except Exception as e:
            self.logger.error(f"Audio stream error: {e}")
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass
            p.terminate()

class HybridSpeechRecognizer:
    """Hybrid speech recognizer using both online and offline methods"""
    
    def __init__(self):
        # Online recognizer (Google Speech API)
        import speech_recognition as sr
        self.online_recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Offline recognizer (Vosk)
        self.offline_recognizer = OfflineSpeechRecognizer()
        
        # Configuration
        self.prefer_offline = False  # Set to True to prefer offline recognition
        self.fallback_enabled = True
        
        self.logger = logging.getLogger(__name__)

    def recognize_with_fallback(self, audio_data, timeout=5):
        """Recognize speech with online/offline fallback"""
        results = []
        
        # Try online first (unless offline preferred)
        if not self.prefer_offline:
            try:
                # Convert audio for online recognition
                if hasattr(audio_data, 'get_wav_data'):
                    text = self.online_recognizer.recognize_google(audio_data, language='en-IN')
                    results.append(('online', text, 0.9))
                    self.logger.info(f"Online recognition: {text}")
            except Exception as e:
                self.logger.warning(f"Online recognition failed: {e}")
        
        # Try offline recognition
        if self.offline_recognizer.is_available():
            try:
                if hasattr(audio_data, 'get_wav_data'):
                    wav_data = audio_data.get_wav_data()
                else:
                    wav_data = audio_data
                
                text = self.offline_recognizer.recognize_audio_chunk(wav_data)
                if text:
                    results.append(('offline', text, 0.7))
                    self.logger.info(f"Offline recognition: {text}")
            except Exception as e:
                self.logger.warning(f"Offline recognition failed: {e}")
        
        # If online failed and we haven't tried it yet, try it now
        if not results and self.prefer_offline and self.fallback_enabled:
            try:
                if hasattr(audio_data, 'get_wav_data'):
                    text = self.online_recognizer.recognize_google(audio_data, language='en-IN')
                    results.append(('online_fallback', text, 0.8))
                    self.logger.info(f"Online fallback: {text}")
            except Exception as e:
                self.logger.warning(f"Online fallback failed: {e}")
        
        return results

    def listen_for_keywords_hybrid(self, keywords, callback=None):
        """Listen for keywords using hybrid approach"""
        self.logger.info("Starting hybrid keyword detection...")
        
        # Start offline continuous recognition if available
        offline_active = False
        if self.offline_recognizer.is_available():
            def offline_callback(text, found_keywords, source):
                if callback:
                    callback(text, found_keywords, source)
            
            offline_active = self.offline_recognizer.start_continuous_recognition(offline_callback)
        
        # Online recognition loop
        try:
            with self.microphone as source:
                self.online_recognizer.adjust_for_ambient_noise(source)
            
            while True:
                try:
                    # Listen for audio
                    with self.microphone as source:
                        audio = self.online_recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    # Process with hybrid recognition
                    results = self.recognize_with_fallback(audio)
                    
                    for source, text, confidence in results:
                        # Check for keywords
                        text_lower = text.lower()
                        found_keywords = [kw for kw in keywords if kw in text_lower]
                        
                        if found_keywords:
                            self.logger.info(f"Keywords detected via {source}: {found_keywords}")
                            if callback:
                                callback(text, found_keywords, source)
                            return text, found_keywords, source
                        
                        # Log all recognized text
                        self.logger.info(f"Heard ({source}): {text}")
                
                except sr.WaitTimeoutError:
                    pass  # Continue listening
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error(f"Hybrid recognition error: {e}")
                    time.sleep(1)
        
        finally:
            if offline_active:
                self.offline_recognizer.stop_continuous_recognition()

def download_vosk_model(language="en-us"):
    """Helper function to download Vosk models"""
    import urllib.request
    import tarfile
    
    models = {
        "en-us": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
        "en-in": "https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip",
        "hi": "https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip"
    }
    
    if language not in models:
        print(f"Model for {language} not available")
        return False
    
    model_dir = "data/vosk_models"
    os.makedirs(model_dir, exist_ok=True)
    
    model_url = models[language]
    model_filename = os.path.basename(model_url)
    model_path = os.path.join(model_dir, model_filename)
    
    print(f"Downloading Vosk model for {language}...")
    try:
        urllib.request.urlretrieve(model_url, model_path)
        
        # Extract the model
        if model_filename.endswith('.zip'):
            import zipfile
            with zipfile.ZipFile(model_path, 'r') as zip_ref:
                zip_ref.extractall(model_dir)
        elif model_filename.endswith('.tar.gz'):
            with tarfile.open(model_path, 'r:gz') as tar_ref:
                tar_ref.extractall(model_dir)
        
        print(f"Model downloaded and extracted to {model_dir}")
        return True
        
    except Exception as e:
        print(f"Failed to download model: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Test offline recognition
    print("Testing offline speech recognition...")
    
    recognizer = OfflineSpeechRecognizer()
    
    if not recognizer.is_available():
        print("Vosk model not available. Attempting to download...")
        if download_vosk_model("en-us"):
            recognizer = OfflineSpeechRecognizer()
    
    if recognizer.is_available():
        def test_callback(text, keywords, source):
            print(f"🚨 KEYWORDS DETECTED via {source}: {keywords} in '{text}'")
        
        try:
            recognizer.start_continuous_recognition(test_callback)
            print("Listening for keywords (offline)... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            recognizer.stop_continuous_recognition()
    else:
        print("Offline recognition not available")