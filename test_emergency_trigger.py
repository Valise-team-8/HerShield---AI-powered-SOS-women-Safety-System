#!/usr/bin/env python3
"""
Test Emergency Trigger - Simulate keyword detection and dialog appearance
"""

import tkinter as tk
try:
    import customtkinter as ctk
    CUSTOM_TK_AVAILABLE = True
    ctk.set_appearance_mode("dark")
except ImportError:
    ctk = tk
    CUSTOM_TK_AVAILABLE = False

import time
import threading

# Import the main application
try:
    from main import FuturisticHerShield
    MAIN_AVAILABLE = True
except ImportError as e:
    print(f"Main import error: {e}")
    MAIN_AVAILABLE = False

def test_emergency_trigger():
    """Test the emergency trigger functionality"""
    print("🧪 Testing Emergency Trigger")
    
    if not MAIN_AVAILABLE:
        print("❌ Main application not available")
        return
    
    try:
        # Create HerShield app
        print("🚀 Creating HerShield application...")
        app = FuturisticHerShield()
        
        def simulate_keyword_detection():
            """Simulate keyword detection after 5 seconds"""
            print("⏰ Waiting 5 seconds before simulating keyword detection...")
            time.sleep(5)
            
            print("🎤 Simulating voice detection: 'help emergency'")
            # Trigger the emergency protocol directly
            app.root.after(0, lambda: app.trigger_voice_alert("help emergency", ["help", "emergency"]))
            
        # Start simulation in background
        simulation_thread = threading.Thread(target=simulate_keyword_detection, daemon=True)
        simulation_thread.start()
        
        print("🖥️ Starting HerShield GUI...")
        print("🎯 Emergency dialog should appear automatically in 5 seconds...")
        
        # Run the app
        app.run()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_emergency_trigger()