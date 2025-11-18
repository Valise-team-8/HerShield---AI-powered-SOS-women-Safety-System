#!/usr/bin/env python3
"""
Double-Tap Detection System
Implements the 7-second window double-tap confirmation as per project requirements
"""

import time
import threading

class DoubleTapDetector:
    """
    Detects double-tap pattern within 7-second window
    First tap: Activates SOS mode
    Second tap within 7 seconds: Confirms genuine emergency
    """
    
    def __init__(self, window_seconds=7, callback=None):
        self.window_seconds = window_seconds
        self.first_tap_time = None
        self.callback = callback
        self.timer_thread = None
        self.lock = threading.Lock()
        
    def register_tap(self):
        """
        Register a tap and return the current state
        Returns: 'FIRST_TAP', 'CONFIRMED_EMERGENCY', or 'WINDOW_EXPIRED'
        """
        with self.lock:
            current_time = time.time()
            
            if self.first_tap_time is None:
                # First tap - start the window
                self.first_tap_time = current_time
                self._start_expiry_timer()
                return {
                    'status': 'FIRST_TAP',
                    'message': f'SOS Mode Activated! Tap again within {self.window_seconds} seconds to confirm emergency.',
                    'time_remaining': self.window_seconds
                }
                
            elif current_time - self.first_tap_time <= self.window_seconds:
                # Second tap within window - confirmed emergency
                time_taken = current_time - self.first_tap_time
                self.first_tap_time = None
                self._cancel_expiry_timer()
                
                if self.callback:
                    self.callback('CONFIRMED_EMERGENCY')
                    
                return {
                    'status': 'CONFIRMED_EMERGENCY',
                    'message': f'Emergency Confirmed! Response time: {time_taken:.1f}s',
                    'response_time': time_taken
                }
                
            else:
                # Window expired - reset and start new window
                self.first_tap_time = current_time
                self._start_expiry_timer()
                return {
                    'status': 'WINDOW_EXPIRED',
                    'message': f'Previous window expired. New SOS mode activated! Tap again within {self.window_seconds} seconds.',
                    'time_remaining': self.window_seconds
                }
    
    def get_time_remaining(self):
        """Get remaining time in current window"""
        with self.lock:
            if self.first_tap_time is None:
                return 0
            
            elapsed = time.time() - self.first_tap_time
            remaining = max(0, self.window_seconds - elapsed)
            return remaining
    
    def is_window_active(self):
        """Check if tap window is currently active"""
        with self.lock:
            if self.first_tap_time is None:
                return False
            return (time.time() - self.first_tap_time) <= self.window_seconds
    
    def reset(self):
        """Reset the detector"""
        with self.lock:
            self.first_tap_time = None
            self._cancel_expiry_timer()
    
    def _start_expiry_timer(self):
        """Start timer to auto-reset after window expires"""
        self._cancel_expiry_timer()
        self.timer_thread = threading.Timer(self.window_seconds + 0.5, self._on_window_expired)
        self.timer_thread.daemon = True
        self.timer_thread.start()
    
    def _cancel_expiry_timer(self):
        """Cancel the expiry timer"""
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.cancel()
    
    def _on_window_expired(self):
        """Called when window expires without second tap"""
        with self.lock:
            if self.first_tap_time is not None:
                print("⏰ Double-tap window expired - resetting")
                self.first_tap_time = None
                if self.callback:
                    self.callback('WINDOW_EXPIRED')


# Global instance
double_tap_detector = DoubleTapDetector()
