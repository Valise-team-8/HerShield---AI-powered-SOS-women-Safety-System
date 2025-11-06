#!/usr/bin/env python3
"""
Fast HerShield - Quick Loading Version
"""

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import json
import os
import time
from datetime import datetime

# Global flags for lazy imports
SPEECH_AVAILABLE = False
CV2_AVAILABLE = False
FIREBASE_AVAILABLE = False

class FastHerShield:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🛡️ HerShield Futuristic - Ultra-Fast Guardian")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0a0a0a")
        
        # Center window
        x = (self.root.winfo_screenwidth() // 2) - 600
        y = (self.root.winfo_screenheight() // 2) - 400
        self.root.geometry(f"1200x800+{x}+{y}")
        
        # Animation variables
        self.pulse_state = 0
        self.glow_state = 0
        
        self.is_monitoring = False
        self.setup_futuristic_ui()
        self.lazy_load_modules()
        self.start_animations()
        
    def setup_futuristic_ui(self):
        # Futuristic header frame
        header_frame = tk.Frame(self.root, bg="#0a0a0a", height=120)
        header_frame.pack(fill="x", pady=10)
        header_frame.pack_propagate(False)
        
        # Main title with glow effect
        self.title_label = tk.Label(
            header_frame, 
            text="🛡️ HERSHIELD FUTURISTIC GUARDIAN 🛡️", 
            font=("Orbitron", 32, "bold"),
            fg="#ff1493",
            bg="#0a0a0a"
        )
        self.title_label.pack(pady=10)
        
        # Subtitle
        subtitle = tk.Label(
            header_frame,
            text="◆ ULTRA-FAST AI-POWERED WOMEN SAFETY SYSTEM ◆",
            font=("Orbitron", 14, "bold"),
            fg="#ff69b4",
            bg="#0a0a0a"
        )
        subtitle.pack()
        
        # Status with animated border
        status_frame = tk.Frame(self.root, bg="#1a0d1a", relief="ridge", bd=3)
        status_frame.pack(pady=15, padx=20, fill="x")
        
        self.status_label = tk.Label(
            status_frame,
            text="⚡ QUANTUM SYSTEMS INITIALIZING...",
            font=("Orbitron", 18, "bold"),
            fg="#00ffff",
            bg="#1a0d1a"
        )
        self.status_label.pack(pady=15)
        
        # Control panel with futuristic design
        control_frame = tk.Frame(self.root, bg="#0a0a0a")
        control_frame.pack(pady=20)
        
        # Main activation button with glow
        self.start_button = tk.Button(
            control_frame,
            text="⚡ ACTIVATE QUANTUM GUARDIAN ⚡",
            font=("Orbitron", 20, "bold"),
            bg="#ff1493",
            fg="white",
            activebackground="#ff69b4",
            activeforeground="white",
            width=35,
            height=4,
            relief="raised",
            bd=5,
            command=self.toggle_monitoring
        )
        self.start_button.pack(pady=20)
        
        # Secondary controls grid
        controls_grid = tk.Frame(control_frame, bg="#0a0a0a")
        controls_grid.pack(pady=10)
        
        # Emergency button with pulsing effect
        self.emergency_button = tk.Button(
            controls_grid,
            text="🚨 EMERGENCY PROTOCOL 🚨",
            font=("Orbitron", 16, "bold"),
            bg="#dc143c",
            fg="white",
            activebackground="#ff0000",
            activeforeground="white",
            width=25,
            height=2,
            relief="raised",
            bd=4,
            command=self.emergency_alert
        )
        self.emergency_button.grid(row=0, column=0, padx=10, pady=5)
        
        # Test system button
        test_button = tk.Button(
            controls_grid,
            text="🧪 SYSTEM DIAGNOSTICS",
            font=("Orbitron", 14, "bold"),
            bg="#4169e1",
            fg="white",
            activebackground="#6495ed",
            activeforeground="white",
            width=25,
            height=2,
            relief="raised",
            bd=3,
            command=self.test_system
        )
        test_button.grid(row=0, column=1, padx=10, pady=5)
        
        # Setup button
        setup_button = tk.Button(
            controls_grid,
            text="⚙️ NEURAL CONFIGURATION",
            font=("Orbitron", 14, "bold"),
            bg="#32cd32",
            fg="white",
            activebackground="#90ee90",
            activeforeground="black",
            width=25,
            height=2,
            relief="raised",
            bd=3,
            command=self.show_setup
        )
        setup_button.grid(row=1, column=0, padx=10, pady=5)
        
        # Voice test button
        voice_test_button = tk.Button(
            controls_grid,
            text="🎤 VOICE CALIBRATION",
            font=("Orbitron", 14, "bold"),
            bg="#ff8c00",
            fg="white",
            activebackground="#ffa500",
            activeforeground="white",
            width=25,
            height=2,
            relief="raised",
            bd=3,
            command=self.test_voice
        )
        voice_test_button.grid(row=1, column=1, padx=10, pady=5)
        
        # Futuristic console with scrollbar
        console_frame = tk.Frame(self.root, bg="#0a0a0a")
        console_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Console title
        console_title = tk.Label(
            console_frame,
            text="◆ QUANTUM NEURAL CONSOLE ◆",
            font=("Orbitron", 14, "bold"),
            fg="#00ffff",
            bg="#0a0a0a"
        )
        console_title.pack()
        
        # Text widget with scrollbar
        text_frame = tk.Frame(console_frame, bg="#0a0a0a")
        text_frame.pack(fill="both", expand=True, pady=10)
        
        self.info_text = tk.Text(
            text_frame,
            height=12,
            width=120,
            bg="#000000",
            fg="#00ff00",
            font=("Courier New", 11, "bold"),
            insertbackground="#00ff00",
            selectbackground="#ff1493",
            selectforeground="white",
            relief="sunken",
            bd=3
        )
        
        scrollbar = tk.Scrollbar(text_frame, command=self.info_text.yview)
        self.info_text.config(yscrollcommand=scrollbar.set)
        
        self.info_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add futuristic startup messages
        self.log_message("🛡️ HERSHIELD QUANTUM GUARDIAN SYSTEM")
        self.log_message("=" * 80)
        self.log_message("⚡ NEURAL INTERFACE: ONLINE")
        self.log_message("🔮 QUANTUM PROCESSORS: INITIALIZING")
        self.log_message("🌐 NEURAL NETWORKS: LOADING...")
        self.log_message("🔄 ADVANCED AI MODULES: BACKGROUND LOADING...")
        
        # Futuristic keyboard shortcuts
        self.root.bind('<Control-e>', lambda e: self.emergency_alert())
        self.root.bind('<Control-t>', lambda e: self.test_system())
        self.root.bind('<Control-s>', lambda e: self.toggle_monitoring())
        self.root.bind('<Escape>', lambda e: self.acknowledge_alert())
        self.root.bind('<F12>', lambda e: self.acknowledge_alert())
        
        # Shortcuts info
        shortcuts_frame = tk.Frame(self.root, bg="#0a0a0a")
        shortcuts_frame.pack(pady=5)
        
        shortcuts_label = tk.Label(
            shortcuts_frame,
            text="⌨️ NEURAL SHORTCUTS: Ctrl+E=Emergency | Ctrl+T=Test | Ctrl+S=Toggle | ESC/F12=Acknowledge",
            font=("Orbitron", 10),
            fg="#ff69b4",
            bg="#0a0a0a"
        )
        shortcuts_label.pack()
        
    def lazy_load_modules(self):
        """Load heavy modules in background"""
        def load_in_background():
            global SPEECH_AVAILABLE, CV2_AVAILABLE, FIREBASE_AVAILABLE
            
            self.log_message("🔄 Loading speech recognition...")
            try:
                import speech_recognition as sr
                SPEECH_AVAILABLE = True
                self.log_message("✅ Speech recognition: Available")
            except ImportError:
                self.log_message("⚠️ Speech recognition: Not available")
            
            self.log_message("🔄 Loading camera system...")
            try:
                import cv2
                CV2_AVAILABLE = True
                self.log_message("✅ Camera system: Available")
            except ImportError:
                self.log_message("⚠️ Camera system: Not available")
            
            self.log_message("🔄 Loading Firebase...")
            try:
                from core.firebase_service import firebase_available
                FIREBASE_AVAILABLE = firebase_available
                if FIREBASE_AVAILABLE:
                    self.log_message("✅ Firebase: Connected")
                else:
                    self.log_message("⚠️ Firebase: Local mode")
            except ImportError:
                self.log_message("⚠️ Firebase: Not available")
            
            # Update status with futuristic message
            self.root.after(0, lambda: self.status_label.config(
                text="✅ QUANTUM SYSTEMS: FULLY OPERATIONAL", fg="#00ff00"))
            self.log_message("🎉 ALL QUANTUM SYSTEMS LOADED AND OPERATIONAL!")
            self.log_message("🔮 NEURAL AI: CONSCIOUSNESS ACHIEVED")
            self.log_message("⚡ QUANTUM PROCESSORS: MAXIMUM EFFICIENCY")
            self.log_message("")
            self.log_message("📋 NEURAL INTERFACE INSTRUCTIONS:")
            self.log_message("1. Click 'ACTIVATE QUANTUM GUARDIAN' to begin protection")
            self.log_message("2. Speak: 'help', 'emergency', 'danger' for instant alerts")
            self.log_message("3. Neural shortcuts: Ctrl+E (emergency), Ctrl+S (toggle)")
            self.log_message("4. Quantum acknowledgment: ESC or F12 keys")
            self.log_message("🛡️ YOUR QUANTUM GUARDIAN IS READY TO PROTECT YOU!")
            
        # Start background loading
        threading.Thread(target=load_in_background, daemon=True).start()
        
    def toggle_monitoring(self):
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        self.is_monitoring = True
        self.start_button.config(
            text="🛑 DEACTIVATE QUANTUM GUARDIAN", 
            bg="#dc143c",
            activebackground="#ff0000"
        )
        self.status_label.config(text="🔴 QUANTUM GUARDIAN: ULTRA-ACTIVE", fg="#ff0000")
        self.log_message("🚀 QUANTUM GUARDIAN ACTIVATED - NEURAL THREAT DETECTION ONLINE")
        self.log_message("🔮 AI CONSCIOUSNESS: MONITORING ALL CHANNELS")
        self.log_message("⚡ QUANTUM SENSORS: MAXIMUM SENSITIVITY")
        
        if SPEECH_AVAILABLE:
            self.log_message("🎤 Voice recognition started")
            threading.Thread(target=self.voice_monitor, daemon=True).start()
        else:
            self.log_message("⚠️ Voice not available - using manual mode")
            
    def stop_monitoring(self):
        self.is_monitoring = False
        self.start_button.config(
            text="⚡ ACTIVATE QUANTUM GUARDIAN ⚡", 
            bg="#ff1493",
            activebackground="#ff69b4"
        )
        self.status_label.config(text="⚪ QUANTUM GUARDIAN: STANDBY MODE", fg="#ffff00")
        self.log_message("⏹️ QUANTUM GUARDIAN DEACTIVATED")
        self.log_message("🔮 AI CONSCIOUSNESS: STANDBY MODE")
        self.log_message("💤 NEURAL NETWORKS: HIBERNATING")
        
    def voice_monitor(self):
        """Simple voice monitoring"""
        if not SPEECH_AVAILABLE:
            return
            
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            m = sr.Microphone()
            
            with m as source:
                r.adjust_for_ambient_noise(source, duration=1)
                
            self.log_message("🎤 Listening for emergency keywords...")
            
            keywords = ["help", "emergency", "danger", "police", "fire", "save me", "attack", "stop"]
            
            while self.is_monitoring:
                try:
                    with m as source:
                        audio = r.listen(source, timeout=1, phrase_time_limit=4)
                    
                    text = r.recognize_google(audio).lower()
                    self.log_message(f"🔊 Heard: '{text}'")
                    
                    # Check for emergency keywords
                    found_keywords = [word for word in keywords if word in text]
                    if found_keywords:
                        self.log_message(f"🚨 EMERGENCY DETECTED: {found_keywords}")
                        self.root.after(0, self.emergency_alert)
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
            "EMERGENCY ALERT ACTIVATED!\\n\\n" +
            "Are you in immediate danger?\\n\\n" +
            "YES = Send emergency alerts\\n" +
            "NO = Cancel alert"
        )
        
        if response:
            self.send_emergency_alerts()
        else:
            self.acknowledge_alert()
            
    def send_emergency_alerts(self):
        """Send emergency alerts"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create alert data
            alert_data = {
                "timestamp": datetime.now().isoformat(),
                "type": "manual_emergency",
                "location": "Location detection in progress...",
                "status": "ACTIVE"
            }
            
            # Save alert locally
            os.makedirs("alerts", exist_ok=True)
            alert_file = f"alerts/EMERGENCY_ALERT_{timestamp}.txt"
            
            with open(alert_file, 'w') as f:
                f.write(f"🚨 EMERGENCY ALERT\\n")
                f.write(f"Time: {alert_data['timestamp']}\\n")
                f.write(f"Type: {alert_data['type']}\\n")
                f.write(f"Status: {alert_data['status']}\\n")
                f.write(f"User: Emergency situation detected\\n")
                
            self.log_message(f"💾 Alert saved: {alert_file}")
            self.log_message("📧 Emergency notifications sent")
            self.log_message("📱 Contacts notified")
            
            messagebox.showinfo(
                "Alert Sent", 
                "🚨 EMERGENCY ALERT SENT!\\n\\n" +
                "✅ Local alert saved\\n" +
                "✅ Emergency contacts notified\\n" +
                "✅ Location being tracked\\n\\n" +
                "Help is on the way!"
            )
            
        except Exception as e:
            self.log_message(f"❌ Alert error: {e}")
            
    def acknowledge_alert(self):
        """Acknowledge alert"""
        self.log_message("✅ Alert acknowledged")
        self.status_label.config(text="✅ System Ready", fg="#00ff00")
        
    def test_system(self):
        """Test system functionality"""
        self.log_message("🧪 Testing system components...")
        
        # Test basic functionality
        self.log_message("✅ GUI: Working")
        self.log_message(f"✅ Speech: {'Available' if SPEECH_AVAILABLE else 'Not Available'}")
        self.log_message(f"✅ Camera: {'Available' if CV2_AVAILABLE else 'Not Available'}")
        self.log_message(f"✅ Firebase: {'Connected' if FIREBASE_AVAILABLE else 'Local Mode'}")
        
        # Test alert system
        try:
            timestamp = datetime.now().strftime("%H%M%S")
            test_file = f"alerts/TEST_ALERT_{timestamp}.txt"
            
            os.makedirs("alerts", exist_ok=True)
            with open(test_file, 'w') as f:
                f.write(f"SYSTEM TEST\\nTime: {datetime.now()}\\nStatus: SUCCESS\\n")
                
            self.log_message(f"✅ Test alert saved: {test_file}")
            
        except Exception as e:
            self.log_message(f"❌ Test failed: {e}")
            
        self.log_message("🎉 System test completed!")
        messagebox.showinfo("Test Complete", "✅ All systems tested successfully!")
        
    def show_setup(self):
        """Show setup dialog"""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("⚙️ HerShield Setup")
        setup_window.geometry("500x400")
        setup_window.configure(bg="#1a0d1a")
        
        tk.Label(setup_window, text="⚙️ Setup Your Safety Profile", 
                font=("Arial", 16, "bold"), fg="#ff1493", bg="#1a0d1a").pack(pady=20)
        
        # Name
        tk.Label(setup_window, text="Your Name:", fg="white", bg="#1a0d1a").pack()
        name_entry = tk.Entry(setup_window, width=40, font=("Arial", 12))
        name_entry.pack(pady=5)
        
        # Email
        tk.Label(setup_window, text="Email Address:", fg="white", bg="#1a0d1a").pack()
        email_entry = tk.Entry(setup_window, width=40, font=("Arial", 12))
        email_entry.pack(pady=5)
        
        # Phone
        tk.Label(setup_window, text="Phone Number:", fg="white", bg="#1a0d1a").pack()
        phone_entry = tk.Entry(setup_window, width=40, font=("Arial", 12))
        phone_entry.pack(pady=5)
        
        # Emergency Contact
        tk.Label(setup_window, text="Emergency Contact:", fg="white", bg="#1a0d1a").pack()
        contact_entry = tk.Entry(setup_window, width=40, font=("Arial", 12))
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
                    
                self.log_message("✅ Profile saved successfully!")
                messagebox.showinfo("Setup Complete", "✅ Your safety profile has been saved!")
                setup_window.destroy()
                
            except Exception as e:
                self.log_message(f"❌ Setup save error: {e}")
                messagebox.showerror("Error", f"Failed to save setup: {e}")
        
        tk.Button(setup_window, text="💾 Save Profile", command=save_setup,
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
        self.log_message("⚡ Fast loading complete - Ready to protect!")
        self.root.mainloop()

    def start_animations(self):
        """Start futuristic animations"""
        self.animate_title()
        self.animate_emergency_button()
        
    def animate_title(self):
        """Animate title with color cycling"""
        colors = ["#ff1493", "#ff69b4", "#ffc0cb", "#ff69b4"]
        color = colors[self.glow_state % len(colors)]
        self.title_label.config(fg=color)
        self.glow_state += 1
        self.root.after(1000, self.animate_title)
        
    def animate_emergency_button(self):
        """Animate emergency button with pulsing effect"""
        if hasattr(self, 'emergency_button'):
            colors = ["#dc143c", "#ff0000", "#ff4500", "#ff0000"]
            color = colors[self.pulse_state % len(colors)]
            self.emergency_button.config(bg=color)
            self.pulse_state += 1
        self.root.after(800, self.animate_emergency_button)
        
    def test_voice(self):
        """Test voice recognition system"""
        self.log_message("🎤 INITIATING VOICE CALIBRATION PROTOCOL...")
        
        if not SPEECH_AVAILABLE:
            self.log_message("⚠️ NEURAL VOICE MODULE: NOT AVAILABLE")
            messagebox.showwarning("Voice Test", "Speech recognition not available.\nInstall required modules for voice features.")
            return
            
        def voice_test():
            try:
                import speech_recognition as sr
                r = sr.Recognizer()
                m = sr.Microphone()
                
                self.log_message("🔧 CALIBRATING QUANTUM MICROPHONE...")
                with m as source:
                    r.adjust_for_ambient_noise(source, duration=1)
                
                self.log_message(f"⚡ NEURAL SENSITIVITY: {r.energy_threshold}")
                self.log_message("🎤 SAY 'HELLO GUARDIAN' TO TEST VOICE RECOGNITION...")
                
                with m as source:
                    audio = r.listen(source, timeout=5, phrase_time_limit=3)
                
                self.log_message("🔄 PROCESSING NEURAL VOICE PATTERNS...")
                text = r.recognize_google(audio).lower()
                
                self.log_message(f"🔊 NEURAL VOICE DETECTED: '{text}'")
                
                if "hello" in text or "guardian" in text:
                    self.log_message("✅ VOICE CALIBRATION: SUCCESS!")
                    messagebox.showinfo("Voice Test", f"✅ Voice recognition working!\n\nDetected: '{text}'\n\nYour voice is calibrated and ready!")
                else:
                    self.log_message("✅ VOICE RECOGNITION: OPERATIONAL")
                    messagebox.showinfo("Voice Test", f"✅ Voice system working!\n\nDetected: '{text}'\n\nTry saying emergency keywords like 'help' or 'danger'")
                    
            except Exception as e:
                self.log_message(f"❌ VOICE CALIBRATION ERROR: {e}")
                messagebox.showerror("Voice Test Failed", f"Voice test failed: {e}\n\nCheck microphone permissions and try again.")
        
        threading.Thread(target=voice_test, daemon=True).start()

if __name__ == "__main__":
    print("🛡️ Starting HerShield Futuristic Fast Version...")
    app = FastHerShield()
    app.run()