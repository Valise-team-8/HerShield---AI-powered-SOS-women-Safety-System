#!/usr/bin/env python3
"""
Physical Distress Detection System
Detects signs of physical struggle: running, pushing, visible blood
Uses video analysis and motion detection
"""

import cv2
import numpy as np
import time
from datetime import datetime

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV not available for distress detection")


class DistressDetector:
    """
    Detects physical distress indicators:
    - Rapid movement (running, struggling)
    - Pushing/shoving motions
    - Red color detection (blood)
    - Unusual body positions
    """
    
    def __init__(self):
        # Enhanced thresholds for better accuracy
        self.motion_threshold = 3000  # Lower threshold for earlier detection
        self.red_threshold = 0.08  # More sensitive to blood detection
        self.prev_frame = None
        self.motion_history = []
        self.max_history = 15  # Longer history for better pattern analysis
        
        # Advanced detection parameters
        self.motion_variance_threshold = 2.5  # Detect sudden motion changes
        self.red_cluster_min_size = 300  # Minimum red region size
        self.optical_flow_threshold = 2.8  # Pushing detection sensitivity
        
        # Calibration for different lighting conditions
        self.adaptive_threshold = True
        self.frame_count = 0
        
    def detect_rapid_movement(self, frame):
        """
        ENHANCED: Detect rapid movement with improved accuracy
        Uses adaptive thresholding and motion pattern analysis
        
        Returns:
            dict with motion_detected, intensity, type, and confidence
        """
        if not CV2_AVAILABLE:
            return {'motion_detected': False, 'reason': 'OpenCV not available'}
        
        try:
            self.frame_count += 1
            
            # Convert to grayscale with enhanced preprocessing
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Adaptive Gaussian blur based on frame size
            blur_size = max(15, min(25, frame.shape[0] // 30))
            if blur_size % 2 == 0:
                blur_size += 1
            gray = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)
            
            # First frame initialization
            if self.prev_frame is None:
                self.prev_frame = gray
                return {'motion_detected': False, 'reason': 'Initializing', 'confidence': 0}
            
            # Compute difference with enhanced sensitivity
            frame_delta = cv2.absdiff(self.prev_frame, gray)
            
            # Adaptive thresholding based on lighting
            if self.adaptive_threshold:
                threshold_value = max(20, min(35, int(np.mean(frame_delta) * 1.5)))
            else:
                threshold_value = 25
            
            thresh = cv2.threshold(frame_delta, threshold_value, 255, cv2.THRESH_BINARY)[1]
            
            # Enhanced morphological operations
            kernel = np.ones((3, 3), np.uint8)
            thresh = cv2.dilate(thresh, kernel, iterations=2)
            thresh = cv2.erode(thresh, kernel, iterations=1)
            
            # Find contours with hierarchy
            contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Calculate total motion with weighted areas
            total_motion = 0
            significant_contours = 0
            max_contour_area = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Filter noise
                    total_motion += area
                    significant_contours += 1
                    max_contour_area = max(max_contour_area, area)
            
            # Update history
            self.motion_history.append(total_motion)
            if len(self.motion_history) > self.max_history:
                self.motion_history.pop(0)
            
            # Advanced motion pattern analysis
            avg_motion = np.mean(self.motion_history) if self.motion_history else 0
            std_motion = np.std(self.motion_history) if len(self.motion_history) > 2 else 0
            
            # Detect motion spikes (sudden movements)
            motion_spike = total_motion > (avg_motion + std_motion * self.motion_variance_threshold)
            
            # Calculate motion variance (erratic movement indicator)
            motion_variance = std_motion / (avg_motion + 1)  # Avoid division by zero
            
            # Update previous frame
            self.prev_frame = gray
            
            # Enhanced motion type classification with confidence
            motion_type = "NONE"
            confidence = 0
            
            if total_motion > self.motion_threshold * 4:
                motion_type = "RUNNING"
                confidence = min(100, (total_motion / (self.motion_threshold * 4)) * 100)
            elif total_motion > self.motion_threshold * 2 and motion_variance > 0.5:
                motion_type = "STRUGGLING"
                confidence = min(100, (total_motion / (self.motion_threshold * 2)) * 80)
            elif total_motion > self.motion_threshold * 1.5:
                motion_type = "RAPID_MOVEMENT"
                confidence = min(100, (total_motion / (self.motion_threshold * 1.5)) * 60)
            elif motion_spike and significant_contours > 3:
                motion_type = "SUDDEN_MOVEMENT"
                confidence = 70
            
            return {
                'motion_detected': total_motion > self.motion_threshold,
                'intensity': total_motion,
                'type': motion_type,
                'spike_detected': motion_spike,
                'average_motion': avg_motion,
                'variance': motion_variance,
                'confidence': confidence,
                'contour_count': significant_contours,
                'max_area': max_contour_area
            }
            
        except Exception as e:
            return {'motion_detected': False, 'error': str(e), 'confidence': 0}
    
    def detect_red_color(self, frame):
        """
        ENHANCED: Detect red color with improved accuracy
        Filters out false positives (red clothing, objects)
        Focuses on blood-like patterns
        
        Returns:
            dict with red_detected, percentage, locations, and confidence
        """
        if not CV2_AVAILABLE:
            return {'red_detected': False, 'reason': 'OpenCV not available'}
        
        try:
            # Convert to multiple color spaces for better detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            
            # Enhanced red color ranges for blood detection
            # Dark red (dried blood)
            lower_red1 = np.array([0, 80, 80])
            upper_red1 = np.array([10, 255, 255])
            # Bright red (fresh blood)
            lower_red2 = np.array([160, 80, 80])
            upper_red2 = np.array([180, 255, 255])
            
            # Create masks
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = cv2.bitwise_or(mask1, mask2)
            
            # Additional filtering using LAB color space
            # Blood has specific L*a*b* values
            l_channel, a_channel, b_channel = cv2.split(lab)
            # High 'a' channel indicates red
            a_mask = cv2.inRange(a_channel, 140, 255)
            
            # Combine masks
            combined_mask = cv2.bitwise_and(red_mask, a_mask)
            
            # Morphological operations to remove noise
            kernel = np.ones((5, 5), np.uint8)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            
            # Calculate percentage
            total_pixels = frame.shape[0] * frame.shape[1]
            red_pixels = cv2.countNonZero(combined_mask)
            red_percentage = red_pixels / total_pixels
            
            # Find red regions with enhanced filtering
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            red_regions = []
            total_red_area = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter by size (blood patterns are typically medium-sized)
                if area > self.red_cluster_min_size and area < (total_pixels * 0.3):
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate shape features
                    perimeter = cv2.arcLength(contour, True)
                    circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                    aspect_ratio = float(w) / h if h > 0 else 0
                    
                    # Blood patterns are typically irregular (low circularity)
                    # and not perfectly rectangular
                    is_blood_like = circularity < 0.8 and 0.3 < aspect_ratio < 3.0
                    
                    if is_blood_like:
                        red_regions.append({
                            'x': x, 'y': y, 'width': w, 'height': h, 
                            'area': area,
                            'circularity': circularity,
                            'aspect_ratio': aspect_ratio
                        })
                        total_red_area += area
            
            # Calculate confidence based on multiple factors
            confidence = 0
            if len(red_regions) > 0:
                # More regions = higher confidence (splatter pattern)
                region_score = min(50, len(red_regions) * 10)
                # Larger total area = higher confidence
                area_score = min(30, (total_red_area / total_pixels) * 1000)
                # Percentage score
                percentage_score = min(20, red_percentage * 200)
                
                confidence = region_score + area_score + percentage_score
            
            return {
                'red_detected': red_percentage > self.red_threshold and len(red_regions) > 0,
                'percentage': red_percentage * 100,
                'pixel_count': red_pixels,
                'regions': red_regions,
                'region_count': len(red_regions),
                'total_area': total_red_area,
                'confidence': min(100, confidence)
            }
            
        except Exception as e:
            return {'red_detected': False, 'error': str(e), 'confidence': 0}
    
    def detect_pushing_motion(self, frame):
        """
        ENHANCED: Detect pushing/shoving with improved accuracy
        Uses dense optical flow and directional analysis
        
        Returns:
            dict with pushing_detected, direction, and confidence
        """
        if not CV2_AVAILABLE:
            return {'pushing_detected': False, 'reason': 'OpenCV not available'}
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if self.prev_frame is None:
                self.prev_frame = gray
                return {'pushing_detected': False, 'reason': 'Initializing', 'confidence': 0}
            
            # Enhanced optical flow parameters for better accuracy
            flow = cv2.calcOpticalFlowFarneback(
                self.prev_frame, gray, None,
                pyr_scale=0.5,      # Pyramid scale
                levels=3,           # Number of pyramid layers
                winsize=15,         # Window size
                iterations=3,       # Iterations at each level
                poly_n=5,           # Polynomial expansion
                poly_sigma=1.2,     # Gaussian sigma
                flags=0
            )
            
            # Analyze flow magnitude and direction
            magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            
            # Statistical analysis
            avg_magnitude = np.mean(magnitude)
            max_magnitude = np.max(magnitude)
            std_magnitude = np.std(magnitude)
            
            # Detect pushing: sudden, strong, directional movement
            # Enhanced threshold using standard deviation
            pushing_threshold = avg_magnitude + (std_magnitude * self.optical_flow_threshold)
            pushing_detected = max_magnitude > pushing_threshold and avg_magnitude > 0.5
            
            # Analyze direction consistency (pushing has consistent direction)
            angle_degrees = np.degrees(angle)
            
            # Calculate dominant direction
            hist, bins = np.histogram(angle_degrees.flatten(), bins=8, range=(0, 360))
            dominant_direction_idx = np.argmax(hist)
            dominant_direction_angle = bins[dominant_direction_idx]
            
            # Direction consistency (higher = more consistent = more likely pushing)
            direction_consistency = hist[dominant_direction_idx] / np.sum(hist)
            
            # Determine primary direction with enhanced accuracy
            direction = "UNKNOWN"
            if pushing_detected:
                if 337.5 <= dominant_direction_angle or dominant_direction_angle < 22.5:
                    direction = "RIGHT"
                elif 22.5 <= dominant_direction_angle < 67.5:
                    direction = "DOWN-RIGHT"
                elif 67.5 <= dominant_direction_angle < 112.5:
                    direction = "DOWN"
                elif 112.5 <= dominant_direction_angle < 157.5:
                    direction = "DOWN-LEFT"
                elif 157.5 <= dominant_direction_angle < 202.5:
                    direction = "LEFT"
                elif 202.5 <= dominant_direction_angle < 247.5:
                    direction = "UP-LEFT"
                elif 247.5 <= dominant_direction_angle < 292.5:
                    direction = "UP"
                else:
                    direction = "UP-RIGHT"
            
            # Calculate confidence
            confidence = 0
            if pushing_detected:
                # Magnitude score
                magnitude_score = min(40, (max_magnitude / pushing_threshold) * 40)
                # Consistency score
                consistency_score = direction_consistency * 40
                # Strength score
                strength_score = min(20, avg_magnitude * 20)
                
                confidence = magnitude_score + consistency_score + strength_score
            
            self.prev_frame = gray
            
            return {
                'pushing_detected': pushing_detected and direction_consistency > 0.3,
                'magnitude': float(avg_magnitude),
                'max_magnitude': float(max_magnitude),
                'direction': direction,
                'consistency': float(direction_consistency),
                'confidence': min(100, confidence)
            }
            
        except Exception as e:
            return {'pushing_detected': False, 'error': str(e), 'confidence': 0}
    
    def analyze_frame(self, frame):
        """
        Comprehensive frame analysis for all distress indicators
        
        Returns:
            dict with all detection results and overall distress score
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'motion': self.detect_rapid_movement(frame),
            'red_color': self.detect_red_color(frame),
            'pushing': self.detect_pushing_motion(frame),
            'distress_detected': False,
            'distress_score': 0,
            'indicators': []
        }
        
        # ENHANCED: Calculate distress score with confidence weighting
        score = 0
        indicators = []
        confidence_total = 0
        
        # Motion analysis with confidence weighting
        if results['motion'].get('motion_detected'):
            motion_type = results['motion'].get('type', 'NONE')
            motion_confidence = results['motion'].get('confidence', 0)
            
            if motion_type == "RUNNING":
                base_score = 45
                weighted_score = base_score * (motion_confidence / 100)
                score += weighted_score
                indicators.append(f"Rapid running detected (confidence: {motion_confidence:.0f}%)")
            elif motion_type == "STRUGGLING":
                base_score = 40
                weighted_score = base_score * (motion_confidence / 100)
                score += weighted_score
                indicators.append(f"Struggling motion detected (confidence: {motion_confidence:.0f}%)")
            elif motion_type == "RAPID_MOVEMENT":
                base_score = 30
                weighted_score = base_score * (motion_confidence / 100)
                score += weighted_score
                indicators.append(f"Rapid movement detected (confidence: {motion_confidence:.0f}%)")
            elif motion_type == "SUDDEN_MOVEMENT":
                base_score = 25
                weighted_score = base_score * (motion_confidence / 100)
                score += weighted_score
                indicators.append(f"Sudden movement detected (confidence: {motion_confidence:.0f}%)")
            
            confidence_total += motion_confidence
        
        # Red color analysis with confidence weighting
        if results['red_color'].get('red_detected'):
            red_confidence = results['red_color'].get('confidence', 0)
            base_score = 35
            weighted_score = base_score * (red_confidence / 100)
            score += weighted_score
            
            region_count = results['red_color'].get('region_count', 0)
            percentage = results['red_color']['percentage']
            indicators.append(f"Blood-like pattern detected: {region_count} regions, {percentage:.1f}% (confidence: {red_confidence:.0f}%)")
            confidence_total += red_confidence
        
        # Pushing analysis with confidence weighting
        if results['pushing'].get('pushing_detected'):
            push_confidence = results['pushing'].get('confidence', 0)
            base_score = 30
            weighted_score = base_score * (push_confidence / 100)
            score += weighted_score
            
            direction = results['pushing']['direction']
            consistency = results['pushing'].get('consistency', 0)
            indicators.append(f"Pushing motion detected: {direction} (consistency: {consistency:.0%}, confidence: {push_confidence:.0f}%)")
            confidence_total += push_confidence
        
        # Calculate overall confidence
        num_detections = len([r for r in [results['motion'], results['red_color'], results['pushing']] 
                             if r.get('motion_detected') or r.get('red_detected') or r.get('pushing_detected')])
        overall_confidence = confidence_total / num_detections if num_detections > 0 else 0
        
        results['distress_score'] = min(100, score)
        results['indicators'] = indicators
        results['overall_confidence'] = overall_confidence
        
        # Enhanced threshold with confidence requirement
        # Require either high score OR high confidence with moderate score
        high_confidence_threshold = score >= 40 and overall_confidence >= 70
        high_score_threshold = score >= 60
        
        results['distress_detected'] = high_score_threshold or high_confidence_threshold
        
        return results
    
    def reset(self):
        """Reset detector state"""
        self.prev_frame = None
        self.motion_history = []


# Global instance
distress_detector = DistressDetector()


def analyze_video_for_distress(video_source=0, duration=10):
    """
    Analyze video feed for distress indicators
    
    Args:
        video_source: Camera index or video file path
        duration: How long to analyze (seconds)
    
    Returns:
        dict with analysis results
    """
    if not CV2_AVAILABLE:
        return {'error': 'OpenCV not available'}
    
    try:
        cap = cv2.VideoCapture(video_source)
        start_time = time.time()
        frame_count = 0
        distress_frames = 0
        max_score = 0
        all_indicators = set()
        
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Analyze every 5th frame for performance
            if frame_count % 5 == 0:
                result = distress_detector.analyze_frame(frame)
                
                if result['distress_detected']:
                    distress_frames += 1
                
                max_score = max(max_score, result['distress_score'])
                all_indicators.update(result['indicators'])
        
        cap.release()
        
        distress_percentage = (distress_frames / (frame_count / 5)) * 100 if frame_count > 0 else 0
        
        return {
            'duration': duration,
            'frames_analyzed': frame_count // 5,
            'distress_frames': distress_frames,
            'distress_percentage': distress_percentage,
            'max_distress_score': max_score,
            'indicators': list(all_indicators),
            'distress_detected': distress_percentage > 20 or max_score >= 70
        }
        
    except Exception as e:
        return {'error': str(e)}
