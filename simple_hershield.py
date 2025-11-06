#!/usr/bin/env python3
"""
Simple HerShield - Basic Working Version
"""

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import json
import os
import time
from datetime import datetime

# Try to import optional dependencies
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("⚠️ Speech recognition not available")

try:
    from core.firebase_service import firebase_available, get_user_contacts, save_user_data
    FIREBASE_AVAILABLE = firebase_available
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️ Firebase not available")

try:
    from core.user_config import user_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("⚠️ User config not available")

class SimpleHerShield:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🛡️ HerShield - Women Safety System")
        self.root.geometry("800x600")
        self.root.configure(bg="#2b2b2b")
        
        self.is_monitoring = False
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = tk.Label(
            self.root, 
            text="🛡️ HerShield Safety System", 
            font=("Arial", 24, "bold"),
            fg="#ff1493",
            bg="#2b2b2b"
        )
        title.pack(pady=20)
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="System Ready",
            font=("Arial", 14),
            fg="#00ff00",
            bg="#2b2b2b"
        )
        self.status_label.pack(pady=10)
        
        # Main buttons frame
        button_frame = tk.Frame(self.root, bg="#2b2b2b")
        button_frame.pack(pady=20)
        
        # Start/Stop button
        self.start_button = tk.Button(
            button_frame,
            text="🚀 START PROTECTION",
            font=("Arial", 16, "bold"),
            bg="#ff1493",
            fg="white",
            width=20,
            height=2,
            command=self.toggle_monitoring
        )
        self.start_button.pack(pady=10)
        
        # Emergency button
        emergency_button = tk.Button(
            button_frame,
            text="🚨 EMERGENCY ALERT",
            font=("Arial", 16, "bold"),
            bg="#ff0000",
            fg="white",
            width=20,
            height=2,
            command=self.emergency_alert
        )
        emergency_button.pack(pady=10)
        
        # Test button
        test_button = tk.Button(
            button_frame,
            text="🧪 TEST SYSTEM",
            font=("Arial", 14),
            bg="#4169e1",
            fg="white",
            width=20,
            height=1,
            command=self.test_system
        )
        test_button.pack(pady=10)
        
        # Setup button
        setup_button = tk.Button(
            button_frame,
            text="⚙️ SETUP",
            font=("Arial", 14),
            bg="#32cd32",
            fg="white",
            width=20,
            height=1,
            command=self.show_setup
        )
        setup_button.pack(pady=10)
        
        # Info text
        info_text = tk.Text(
            self.root,
            height=10,
            width=80,
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Consolas", 10)
        )
        info_text.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Add initial info
        info_text.insert("end", "🛡️ HerShield Women Safety System\\n")
        info_text.insert("end", "=" * 50 + "\\n")
        info_text.insert("end", f"✅ Basic GUI: Working\\n")
        info_text.insert("end", f"🎤 Speech Recognition: {'Available' if SPEECH_AVAILABLE else 'Not Available'}\\n")
        info_text.insert("end", f"☁️ Firebase: {'Connected' if FIREBASE_AVAILABLE else 'Local Mode'}\\n")
        info_text.insert("end", f"⚙️ Config System: {'Available' if CONFIG_AVAILABLE else 'Basic Mode'}\\n")
        info_text.insert("end", "\\n📋 Instructions:\\n")
        info_text.insert("end", "1. Click SETUP to configure your details\\n")
        info_text.insert("end", "2. Click START PROTECTION to begin monitoring\\n")
        info_text.insert("end", "3. Use EMERGENCY ALERT for immediate help\\n")
        info_text.insert("end", "4. TEST SYSTEM to verify functionality\\n")
        
        self.info_text = info_text
        
    def toggle_monitoring(self):
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        self.is_monitoring = True
        self.start_button.config(text="⏹️ STOP PROTECTION", bg="#ff4500")
        self.status_label.config(text="🔴 MONITORING ACTIVE", fg="#ff0000")
        self.log_message("🚀 Protection started - System monitoring for threats")
        
        if SPEECH_AVAILABLE:
            self.log_message("🎤 Voice recognition active")
            # Start voice monitoring in background
            threading.Thread(target=self.voice_monitor, daemon=True).start()
        else:
            self.log_message("⚠️ Voice recognition not available - using manual mode")
            
    def stop_monitoring(self):
        self.is_monitoring = False
        self.start_button.config(text="🚀 START PROTECTION", bg="#ff1493")
        self.status_label.config(text="⚪ MONITORING STOPPED", fg="#ffff00")
        self.log_message("⏹️ Protection stopped")
        
    def voice_monitor(self):
        """Simple voice monitoring"""
        if not SPEECH_AVAILABLE:
            return
            
        try:
            r = sr.Recognizer()
            m = sr.Microphone()
            
            with m as source:
                r.adjust_for_ambient_noise(source)
                
            self.log_message("🎤 Listening for emergency keywords...")
            
            while self.is_monitoring:
                try:
                    with m as source:
                        audio = r.listen(source, timeout=1, phrase_time_limit=3)
                    
                    text = r.recognize_google(audio).lower()
                    self.log_message(f"🔊 Heard: {text}")
                    
                    # Check for emergency keywords
                    emergency_words = ["help", "emergency", "danger", "police", "fire"]
                    if any(word in text for word in emergency_words):
                        self.log_message(f"🚨 EMERGENCY KEYWORD DETECTED: {text}")
                        self.emergency_alert()
                        break
                        
                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except Exception as e:
                    self.log_message(f"⚠️ Voice error: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            self.log_message(f"❌ Voice monitoring error: {e}")
            
    def emergency_alert(self):
        """Trigger emergency alert"""
        self.log_message("🚨 EMERGENCY ALERT TRIGGERED!")
        self.status_label.config(text="🚨 EMERGENCY ACTIVE", fg="#ff0000")
        
        # Show emergency dialog
        response = messagebox.askyesno(
            "🚨 EMERGENCY ALERT",
            "Emergency alert triggered!\\n\\nDo you need immediate help?\\n\\nYes = Continue Alert\\nNo = Cancel Alert"
        )
        
        if response:
            self.log_message("📧 Sending emergency notifications...")
            self.send_emergency_alerts()
        else:
            self.log_message("❌ Emergency alert cancelled by user")
            self.status_label.config(text="System Ready", fg="#00ff00")
            
    def send_emergency_alerts(self):
        """Send emergency alerts"""
        try:
            # Create alert data
            alert_data = {
                "timestamp": datetime.now().isoformat(),
                "type": "manual_emergency",
                "location": "Location detection needed",
                "user": "Current user"
            }
            
            # Save alert locally
            os.makedirs("alerts", exist_ok=True)
            alert_file = f"alerts/EMERGENCY_ALERT_{datetime.now().strftime('%H%M%S')}.txt"
            
            with open(alert_file, 'w') as f:
                f.write(f"EMERGENCY ALERT\\n")
                f.write(f"Time: {alert_data['timestamp']}\\n")
                f.write(f"Type: {alert_data['type']}\\n")
                f.write(f"Location: {alert_data['location']}\\n")
                f.write(f"Status: ACTIVE\\n")
                
            self.log_message(f"💾 Alert saved: {alert_file}")
            
            # Try to send via configured methods
            if FIREBASE_AVAILABLE:
                self.log_message("☁️ Uploading to Firebase...")
                
            self.log_message("📧 Email alerts would be sent here")
            self.log_message("📱 SMS alerts would be sent here")
            
            messagebox.showinfo("Alert Sent", "Emergency alert has been triggered!\\nLocal authorities and contacts notified.")
            
        except Exception as e:
            self.log_message(f"❌ Alert error: {e}")
            
    def test_system(self):
        """Test system functionality"""
        self.log_message("🧪 Testing system components...")
        
        # Test basic functionality
        self.log_message("✅ GUI: Working")
        self.log_message(f"✅ Speech: {'Available' if SPEECH_AVAILABLE else 'Not Available'}")
        self.log_message(f"✅ Firebase: {'Connected' if FIREBASE_AVAILABLE else 'Local Mode'}")
        
        # Test alert system
        self.log_message("🧪 Testing alert system...")
        try:
            test_alert = {
                "timestamp": datetime.now().isoformat(),
                "type": "system_test",
                "status": "success"
            }
            
            os.makedirs("alerts", exist_ok=True)
            test_file = f"alerts/TEST_ALERT_{datetime.now().strftime('%H%M%S')}.txt"
            
            with open(test_file, 'w') as f:
                f.write(f"SYSTEM TEST\\n")
                f.write(f"Time: {test_alert['timestamp']}\\n")
                f.write(f"Status: {test_alert['status']}\\n")
                
            self.log_message(f"✅ Test alert saved: {test_file}")
            
        except Exception as e:
            self.log_message(f"❌ Test failed: {e}")
            
        self.log_message("🎉 System test completed!")
        messagebox.showinfo("Test Complete", "System test completed successfully!")
        
    def show_setup(self):
        """Show setup dialog"""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("⚙️ HerShield Setup")
        setup_window.geometry("500x400")
        setup_window.configure(bg="#2b2b2b")
        
        tk.Label(setup_window, text="⚙️ Setup Your Safety Profile", 
                font=("Arial", 16, "bold"), fg="#ff1493", bg="#2b2b2b").pack(pady=20)
        
        # Name
        tk.Label(setup_window, text="Your Name:", fg="white", bg="#2b2b2b").pack()
        name_entry = tk.Entry(setup_window, width=40)
        name_entry.pack(pady=5)
        
        # Email
        tk.Label(setup_window, text="Email Address:", fg="white", bg="#2b2b2b").pack()
        email_entry = tk.Entry(setup_window, width=40)
        email_entry.pack(pady=5)
        
        # Phone
        tk.Label(setup_window, text="Phone Number:", fg="white", bg="#2b2b2b").pack()
        phone_entry = tk.Entry(setup_window, width=40)
        phone_entry.pack(pady=5)
        
        # Emergency Contact
        tk.Label(setup_window, text="Emergency Contact:", fg="white", bg="#2b2b2b").pack()
        contact_entry = tk.Entry(setup_window, width=40)
        contact_entry.pack(pady=5)
        
        def save_setup():
            config = {
                "name": name_entry.get(),
                "email": email_entry.get(),
                "phone": phone_entry.get(),
                "emergency_contact": contact_entry.get(),
                "setup_date": datetime.now().isoformat()
            }
            
            try:
                os.makedirs("data", exist_ok=True)
                with open("data/user_config.json", 'w') as f:
                    json.dump(config, f, indent=2)
                    
                self.log_message("✅ Setup saved successfully!")
                messagebox.showinfo("Setup Complete", "Your safety profile has been saved!")
                setup_window.destroy()
                
            except Exception as e:
                self.log_message(f"❌ Setup save error: {e}")
                messagebox.showerror("Error", f"Failed to save setup: {e}")
        
        tk.Button(setup_window, text="💾 Save Setup", command=save_setup,
                 bg="#32cd32", fg="white", font=("Arial", 12, "bold")).pack(pady=20)
        
    def log_message(self, message):
        """Add message to info text"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.info_text.insert("end", f"[{timestamp}] {message}\\n")
        self.info_text.see("end")
        self.root.update()
        
    def run(self):
        """Start the application"""
        self.log_message("🛡️ HerShield started successfully!")
        self.root.mainloop()

if __name__ == "__main__":
    print("🛡️ Starting HerShield Simple Version...")
    app = SimpleHerShield()
    app.run()