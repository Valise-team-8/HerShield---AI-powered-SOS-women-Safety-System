#!/usr/bin/env python3
"""
Live Streaming Service
Streams live video and audio to cloud during emergency
Ensures evidence is preserved even if phone is destroyed
"""

import threading
import time
from datetime import datetime
import os

try:
    import cv2
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False

try:
    import pyaudio
    import wave
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


class LiveStreamingService:
    """
    Handles live streaming of video and audio during emergency
    Uploads to cloud in real-time
    """
    
    def __init__(self):
        self.streaming = False
        self.video_thread = None
        self.audio_thread = None
        self.evidence_dir = "evidence"
        os.makedirs(self.evidence_dir, exist_ok=True)
    
    def start_streaming(self, upload_callback=None):
        """
        Start live streaming
        
        Args:
            upload_callback: Function to upload chunks to cloud
        """
        if self.streaming:
            return False
        
        self.streaming = True
        print("🎥 Starting live streaming...")
        
        # Start video streaming
        self.video_thread = threading.Thread(
            target=self._stream_video,
            args=(upload_callback,),
            daemon=True
        )
        self.video_thread.start()
        
        # Start audio streaming
        self.audio_thread = threading.Thread(
            target=self._stream_audio,
            args=(upload_callback,),
            daemon=True
        )
        self.audio_thread.start()
        
        return True
    
    def stop_streaming(self):
        """Stop streaming"""
        self.streaming = False
        print("🛑 Stopping live streaming...")
    
    def _stream_video(self, upload_callback):
        """Stream video in real-time"""
        if not VIDEO_AVAILABLE:
            print("⚠️ Video streaming not available")
            return
        
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("❌ Camera not available")
                return
            
            # Video writer setup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_file = os.path.join(self.evidence_dir, f"emergency_video_{timestamp}.avi")
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            fps = 20.0
            frame_size = (640, 480)
            out = cv2.VideoWriter(video_file, fourcc, fps, frame_size)
            
            frame_count = 0
            chunk_size = 100  # Upload every 100 frames
            
            print(f"📹 Recording video to: {video_file}")
            
            while self.streaming:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Resize frame
                frame = cv2.resize(frame, frame_size)
                
                # Write to file
                out.write(frame)
                
                frame_count += 1
                
                # Upload chunk to cloud
                if upload_callback and frame_count % chunk_size == 0:
                    try:
                        upload_callback('video', video_file, frame_count)
                        print(f"☁️ Uploaded video chunk: {frame_count} frames")
                    except Exception as e:
                        print(f"Upload error: {e}")
            
            cap.release()
            out.release()
            
            # Final upload
            if upload_callback:
                try:
                    upload_callback('video', video_file, frame_count, final=True)
                    print(f"✅ Final video uploaded: {video_file}")
                except Exception as e:
                    print(f"Final upload error: {e}")
        
        except Exception as e:
            print(f"Video streaming error: {e}")
    
    def _stream_audio(self, upload_callback):
        """Stream audio in real-time"""
        if not AUDIO_AVAILABLE:
            print("⚠️ Audio streaming not available")
            return
        
        try:
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
            
            # Audio file setup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = os.path.join(self.evidence_dir, f"emergency_audio_{timestamp}.wav")
            
            wf = wave.open(audio_file, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            
            chunk_count = 0
            chunk_size = 100  # Upload every 100 chunks
            
            print(f"🎤 Recording audio to: {audio_file}")
            
            while self.streaming:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    wf.writeframes(data)
                    
                    chunk_count += 1
                    
                    # Upload chunk to cloud
                    if upload_callback and chunk_count % chunk_size == 0:
                        try:
                            upload_callback('audio', audio_file, chunk_count)
                            print(f"☁️ Uploaded audio chunk: {chunk_count} chunks")
                        except Exception as e:
                            print(f"Upload error: {e}")
                
                except Exception as e:
                    print(f"Audio chunk error: {e}")
                    continue
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            wf.close()
            
            # Final upload
            if upload_callback:
                try:
                    upload_callback('audio', audio_file, chunk_count, final=True)
                    print(f"✅ Final audio uploaded: {audio_file}")
                except Exception as e:
                    print(f"Final upload error: {e}")
        
        except Exception as e:
            print(f"Audio streaming error: {e}")
    
    def get_evidence_files(self):
        """Get list of all evidence files"""
        try:
            files = []
            for filename in os.listdir(self.evidence_dir):
                filepath = os.path.join(self.evidence_dir, filename)
                if os.path.isfile(filepath):
                    files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': os.path.getsize(filepath),
                        'created': os.path.getctime(filepath)
                    })
            return files
        except Exception as e:
            print(f"Error getting evidence files: {e}")
            return []


# Global instance
live_streaming = LiveStreamingService()
