#!/usr/bin/env python3
"""
HerShield Launcher - Ensures GUI starts properly
"""

import sys
import os

def launch_hershield():
    """Launch HerShield with proper GUI initialization"""
    print("🛡️ HerShield Launcher")
    print("=" * 30)
    
    try:
        # Import and run HerShield
        print("📦 Importing HerShield...")
        from main import FuturisticHerShield
        
        print("🚀 Creating HerShield application...")
        app = FuturisticHerShield()
        
        print("🖥️ Starting GUI...")
        # Force window to appear
        app.root.deiconify()
        app.root.lift()
        app.root.focus_force()
        
        print("✅ HerShield GUI ready!")
        print("🎯 Click 'ACTIVATE INSTANT GUARDIAN' to start voice monitoring")
        
        # Run the application
        app.run()
        
    except KeyboardInterrupt:
        print("\n🛑 HerShield stopped by user")
    except Exception as e:
        print(f"❌ HerShield launch failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Try basic fallback
        print("\n🔄 Trying basic GUI fallback...")
        try:
            import tkinter as tk
            root = tk.Tk()
            root.title("🛡️ HerShield - Basic Mode")
            root.geometry("400x200")
            
            tk.Label(root, text="🛡️ HerShield", font=("Arial", 20, "bold")).pack(pady=20)
            tk.Label(root, text="Basic mode - Full features unavailable").pack(pady=10)
            tk.Button(root, text="Close", command=root.quit).pack(pady=20)
            
            root.mainloop()
        except Exception as e2:
            print(f"❌ Basic GUI also failed: {e2}")

if __name__ == "__main__":
    launch_hershield()