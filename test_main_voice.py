#!/usr/bin/env python3
"""
Test Voice Detection in Main Application
Quick test to verify voice detection works in the main HerShield app
"""

import threading
import time

def test_main_app_voice():
    """Test voice detection in the main application"""
    print("🛡️ Testing Voice Detection in Main HerShield App")
    print("=" * 50)
    
    try:
        # Import the main application
        from main import FuturisticHerShield
        
        print("🚀 Starting HerShield with voice detection...")
        
        # Create app instance
        app = FuturisticHerShield()
        
        # Start voice monitoring in a separate thread
        def start_voice_test():
            time.sleep(2)  # Wait for app to initialize
            print("\n🎤 Starting voice monitoring test...")
            app.start_protection()  # This should start voice detection
            
            # Let it run for 30 seconds
            time.sleep(30)
            
            print("\n🛑 Stopp