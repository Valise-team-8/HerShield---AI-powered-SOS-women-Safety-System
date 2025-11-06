import cv2
import datetime
import threading
import time
import os
import logging

class EnhancedCameraCapture:
    """Enhanced camera system with video recording and evidence collection"""
    
    def __init__(self):
        self.is_recording = False
        self.video_writer = None
        self.camera = None
        self.recording_thread = None
        
        # Ensure data directory exists
        os.makedirs("data/evidence", exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def capture_image(self, prefix="capture"):
        """Capture a single image"""
        try:
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                self.logger.error("Could not open camera")
                return None
            
            ret, frame = cam.read()
            if ret:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"data/evidence/{prefix}_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                self.logger.info(f"Image captured: {filename}")
                cam.release()
                return filename
            else:
                self.logger.error("Failed to capture image")
                cam.release()
                return None
                
        except Exception as e:
            self.logger.error(f"Image capture error: {e}")
            return None

    def start_video_recording(self, duration=30, prefix="emergency"):
        """Start video recording for specified duration"""
        if self.is_recording:
            self.logger.warning("Recording already in progress")
            return None
        
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.logger.error("Could not open camera for recording")
                return None
            
            # Get camera properties
            fps = int(self.camera.get(cv2.CAP_PROP_FPS)) or 20
            width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Create video writer
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/evidence/{prefix}_video_{timestamp}.mp4"
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))
            
            if not self.video_writer.isOpened():
                self.logger.error("Could not create video writer")
                return None
            
            self.is_recording = True
            self.recording_thread = threading.Thread(
                target=self._recording_loop, 
                args=(duration, filename), 
                daemon=True
            )
            self.recording_thread.start()
            
            self.logger.info(f"Video recording started: {filename} (duration: {duration}s)")
            return filename
            
        except Exception as e:
            self.logger.error(f"Video recording start error: {e}")
            return None

    def _recording_loop(self, duration, filename):
        """Video recording loop"""
        start_time = time.time()
        frame_count = 0
        
        try:
            while self.is_recording and (time.time() - start_time) < duration:
                ret, frame = self.camera.read()
                if ret:
                    self.video_writer.write(frame)
                    frame_count += 1
                else:
                    self.logger.warning("Failed to read frame")
                    break
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
            
            self.logger.info(f"Video recording completed: {frame_count} frames recorded")
            
        except Exception as e:
            self.logger.error(f"Recording loop error: {e}")
        finally:
            self.stop_video_recording()

    def stop_video_recording(self):
        """Stop video recording"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        try:
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            
            if self.camera:
                self.camera.release()
                self.camera = None
            
            self.logger.info("Video recording stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")

    def capture_evidence_sequence(self, num_images=5, interval=1):
        """Capture a sequence of images for evidence"""
        evidence_files = []
        
        try:
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                self.logger.error("Could not open camera for evidence capture")
                return evidence_files
            
            timestamp_base = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for i in range(num_images):
                ret, frame = cam.read()
                if ret:
                    filename = f"data/evidence/evidence_{timestamp_base}_{i+1:02d}.jpg"
                    cv2.imwrite(filename, frame)
                    evidence_files.append(filename)
                    self.logger.info(f"Evidence image {i+1}/{num_images}: {filename}")
                    
                    if i < num_images - 1:  # Don't wait after the last image
                        time.sleep(interval)
                else:
                    self.logger.warning(f"Failed to capture evidence image {i+1}")
            
            cam.release()
            self.logger.info(f"Evidence sequence completed: {len(evidence_files)} images")
            return evidence_files
            
        except Exception as e:
            self.logger.error(f"Evidence capture error: {e}")
            return evidence_files

    def emergency_capture_all(self, video_duration=30):
        """Capture both images and video for emergency evidence"""
        evidence = {
            'images': [],
            'video': None,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        try:
            # Capture immediate image
            image = self.capture_image("emergency_immediate")
            if image:
                evidence['images'].append(image)
            
            # Start video recording
            video_file = self.start_video_recording(video_duration, "emergency")
            if video_file:
                evidence['video'] = video_file
            
            # Capture evidence sequence (while video is recording)
            sequence_images = self.capture_evidence_sequence(3, 2)
            evidence['images'].extend(sequence_images)
            
            self.logger.info(f"Emergency evidence capture initiated")
            return evidence
            
        except Exception as e:
            self.logger.error(f"Emergency capture error: {e}")
            return evidence

    def get_available_cameras(self):
        """Get list of available cameras"""
        cameras = []
        
        for i in range(5):  # Check first 5 camera indices
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    cameras.append(i)
                cap.release()
            except:
                pass
        
        return cameras

    def test_camera(self, camera_index=0):
        """Test camera functionality"""
        try:
            cam = cv2.VideoCapture(camera_index)
            if not cam.isOpened():
                return False, "Camera not accessible"
            
            ret, frame = cam.read()
            cam.release()
            
            if ret:
                return True, "Camera working properly"
            else:
                return False, "Camera accessible but cannot capture frames"
                
        except Exception as e:
            return False, f"Camera test error: {e}"

# Backward compatibility functions
def capture_image():
    """Simple image capture (backward compatibility)"""
    capture_system = EnhancedCameraCapture()
    filename = capture_system.capture_image()
    if filename:
        print(f"[CAPTURED] {filename}")
    else:
        print("[ERROR] Failed to capture image")

def capture_emergency_evidence():
    """Capture comprehensive emergency evidence"""
    capture_system = EnhancedCameraCapture()
    evidence = capture_system.emergency_capture_all()
    
    print("[EMERGENCY EVIDENCE] Capture initiated:")
    if evidence['images']:
        print(f"  Images: {len(evidence['images'])} captured")
    if evidence['video']:
        print(f"  Video: {evidence['video']} (30s recording)")
    
    return evidence

# Example usage
if __name__ == "__main__":
    capture_system = EnhancedCameraCapture()
    
    # Test camera
    available, message = capture_system.test_camera()
    print(f"Camera test: {message}")
    
    if available:
        print("Available cameras:", capture_system.get_available_cameras())
        
        # Test image capture
        image_file = capture_system.capture_image("test")
        if image_file:
            print(f"✅ Image captured: {image_file}")
        
        # Test emergency evidence capture
        evidence = capture_system.emergency_capture_all(10)  # 10 second video for test
        print(f"✅ Emergency evidence: {evidence}")
    else:
        print("❌ No camera available for testing")
    def cleanup_old_evidence(self, max_age_hours=24, max_files=50):
        """Clean up old evidence files to save space"""
        try:
            evidence_dir = "data/evidence"
            if not os.path.exists(evidence_dir):
                return
            
            import glob
            import time
            
            # Get all evidence files
            files = glob.glob(os.path.join(evidence_dir, "*"))
            
            # Sort by modification time (newest first)
            files.sort(key=os.path.getmtime, reverse=True)
            
            current_time = time.time()
            files_removed = 0
            
            # Remove files older than max_age_hours
            for file_path in files:
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > (max_age_hours * 3600):  # Convert hours to seconds
                    try:
                        os.remove(file_path)
                        files_removed += 1
                        self.logger.info(f"Removed old evidence: {os.path.basename(file_path)}")
                    except Exception as e:
                        self.logger.error(f"Failed to remove {file_path}: {e}")
            
            # Keep only the most recent max_files
            if len(files) > max_files:
                for file_path in files[max_files:]:
                    try:
                        os.remove(file_path)
                        files_removed += 1
                        self.logger.info(f"Removed excess evidence: {os.path.basename(file_path)}")
                    except Exception as e:
                        self.logger.error(f"Failed to remove {file_path}: {e}")
            
            if files_removed > 0:
                self.logger.info(f"Cleanup complete: {files_removed} files removed")
                
        except Exception as e:
            self.logger.error(f"Evidence cleanup error: {e}")

# Global cleanup function
def cleanup_evidence_files():
    """Global function to cleanup evidence files"""
    try:
        camera = EnhancedCameraCapture()
        camera.cleanup_old_evidence(max_age_hours=2, max_files=20)  # Keep only 2 hours, max 20 files
    except Exception as e:
        print(f"Evidence cleanup error: {e}")