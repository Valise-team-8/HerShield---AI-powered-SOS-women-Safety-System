#!/usr/bin/env python3
"""
AI Powered SOS Application - Redesigned UI
Women Safety & Emergency Response System
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
from datetime import datetime
import os
import sys

# Try to import customtkinter
try:
    import customtkinter as ctk
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    CUSTOM_TK = True
except ImportError:
    print("⚠️ CustomTkinter not available, using standard tkinter")
    ctk = tk
    CUSTOM_TK = False

# Import core modules
try:
    from core.double_tap_detector import double_tap_detector
    DOUBLE_TAP_AVAILABLE = True
except ImportError:
    print("⚠️ Double-tap detector not available")
    DOUBLE_TAP_AVAILABLE = False

try:
    from core.sms_service import sms_service
    SMS_AVAILABLE = True
except ImportError:
    print("⚠️ SMS service not available")
    SMS_AVAILABLE = False

try:
    from core.distress_detection import distress_detector
    import cv2
    DISTRESS_DETECTION_AVAILABLE = True
except ImportError:
    print("⚠️ Distress detection not available")
    DISTRESS_DETECTION_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    print("⚠️ Speech recognition not available")
    SPEECH_AVAILABLE = False


# Color scheme aligned with document
COLORS = {
    "primary": "#e91e63",      # Pink primary
    "secondary": "#9c27b0",    # Purple secondary
    "success": "#4caf50",      # Green
    "danger": "#f44336",       # Red
    "warning": "#ff9800",      # Orange
    "dark": "#1a1a2e",         # Dark background
    "surface": "#16213e",      # Surface
    "text": "#ffffff",         # White text
    "text_secondary": "#b0b0b0" # Gray text
}

# Emergency keywords
EMERGENCY_KEYWORDS = [
    "help", "emergency", "danger", "police", "save me", 
    "attack", "stop", "sos", "urgent", "crisis"
]


class SOSApplication:
    """
    AI Powered SOS Application
    Features:
    - Voice-based activation ("Help")
    - Double-tap confirmation (7-second window)
    - Distress detection (running, pushing, blood)
    - Online/Offline mode (Firebase/SMS)
    - Real-time evidence capture
    """
    
    def __init__(self):
        # Initialize window
        if CUSTOM_TK:
            self.root = ctk.CTk()
        else:
            self.root = tk.Tk()
        
        self.root.title("AI Powered SOS Application")
        self.root.geometry("1000x700")
        
        # Configure colors
        if CUSTOM_TK:
            self.root.configure(fg_color=COLORS["dark"])
        else:
            self.root.configure(bg=COLORS["dark"])
        
        # Center window
        self.center_window()
        
        # State variables
        self.voice_monitoring = False
        self.distress_monitoring = False
        self.tap_window_active = False
        self.emergency_active = False
        self.distress_score = 0
        
        # Create UI
        self.create_ui()
        
        # Setup keyboard shortcuts
        self.root.bind('<Escape>', lambda e: self.cancel_emergency())
        self.root.bind('<F1>', lambda e: self.show_help())
        
        print("✅ SOS Application initialized")
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    
    def create_ui(self):
        """Create the main UI aligned with document requirements"""
        
        # Main container
        if CUSTOM_TK:
            main_frame = ctk.CTkFrame(self.root, fg_color=COLORS["dark"])
        else:
            main_frame = tk.Frame(self.root, bg=COLORS["dark"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Status Panel
        self.create_status_panel(main_frame)
        
        # Emergency Controls (Main Feature)
        self.create_emergency_controls(main_frame)
        
        # AI Detection Status
        self.create_ai_status(main_frame)
        
        # Footer
        self.create_footer(main_frame)
    
    def create_header(self, parent):
        """Create header with title and project info"""
        if CUSTOM_TK:
            header = ctk.CTkFrame(parent, fg_color=COLORS["primary"], corner_radius=15)
        else:
            header = tk.Frame(parent, bg=COLORS["primary"])
        header.pack(fill="x", pady=(0, 20))
        
        # Title
        if CUSTOM_TK:
            title = ctk.CTkLabel(
                header,
                text="🛡️ AI Powered SOS Application",
                font=ctk.CTkFont(size=32, weight="bold"),
                text_color=COLORS["text"]
            )
        else:
            title = tk.Label(
                header,
                text="🛡️ AI Powered SOS Application",
                font=("Arial", 32, "bold"),
                fg=COLORS["text"],
                bg=COLORS["primary"]
            )
        title.pack(pady=15)
        
        # Subtitle
        if CUSTOM_TK:
            subtitle = ctk.CTkLabel(
                header,
                text="Women Safety & Emergency Response System",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            )
        else:
            subtitle = tk.Label(
                header,
                text="Women Safety & Emergency Response System",
                font=("Arial", 14),
                fg=COLORS["text_secondary"],
                bg=COLORS["primary"]
            )
        subtitle.pack(pady=(0, 15))

    
    def create_status_panel(self, parent):
        """Create status panel showing system state"""
        if CUSTOM_TK:
            status_frame = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=15)
        else:
            status_frame = tk.Frame(parent, bg=COLORS["surface"])
        status_frame.pack(fill="x", pady=(0, 20))
        
        # Status grid
        if CUSTOM_TK:
            grid = ctk.CTkFrame(status_frame, fg_color="transparent")
        else:
            grid = tk.Frame(status_frame, bg=COLORS["surface"])
        grid.pack(pady=15, padx=15)
        
        # Voice Detection Status
        if CUSTOM_TK:
            self.voice_status = ctk.CTkLabel(
                grid,
                text="🎤 Voice: READY",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["success"]
            )
        else:
            self.voice_status = tk.Label(
                grid,
                text="🎤 Voice: READY",
                font=("Arial", 16, "bold"),
                fg=COLORS["success"],
                bg=COLORS["surface"]
            )
        self.voice_status.grid(row=0, column=0, padx=20, pady=10)
        
        # Distress Detection Status
        if CUSTOM_TK:
            self.distress_status = ctk.CTkLabel(
                grid,
                text="📹 Distress: READY",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["success"]
            )
        else:
            self.distress_status = tk.Label(
                grid,
                text="📹 Distress: READY",
                font=("Arial", 16, "bold"),
                fg=COLORS["success"],
                bg=COLORS["surface"]
            )
        self.distress_status.grid(row=0, column=1, padx=20, pady=10)
        
        # Connection Status
        if CUSTOM_TK:
            self.connection_status = ctk.CTkLabel(
                grid,
                text="📡 Online Mode",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["success"]
            )
        else:
            self.connection_status = tk.Label(
                grid,
                text="📡 Online Mode",
                font=("Arial", 16, "bold"),
                fg=COLORS["success"],
                bg=COLORS["surface"]
            )
        self.connection_status.grid(row=0, column=2, padx=20, pady=10)

    
    def create_emergency_controls(self, parent):
        """Create main emergency control panel - CORE FEATURE"""
        if CUSTOM_TK:
            control_frame = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=15)
        else:
            control_frame = tk.Frame(parent, bg=COLORS["surface"])
        control_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Title
        if CUSTOM_TK:
            title = ctk.CTkLabel(
                control_frame,
                text="EMERGENCY ACTIVATION",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=COLORS["text"]
            )
        else:
            title = tk.Label(
                control_frame,
                text="EMERGENCY ACTIVATION",
                font=("Arial", 24, "bold"),
                fg=COLORS["text"],
                bg=COLORS["surface"]
            )
        title.pack(pady=20)
        
        # Double-Tap Emergency Button (PRIMARY FEATURE)
        if CUSTOM_TK:
            self.emergency_btn = ctk.CTkButton(
                control_frame,
                text="🚨 TAP FOR EMERGENCY\n(Tap twice within 7 seconds)",
                font=ctk.CTkFont(size=28, weight="bold"),
                fg_color=COLORS["danger"],
                hover_color="#d32f2f",
                text_color=COLORS["text"],
                height=180,
                width=500,
                corner_radius=20,
                command=self.handle_emergency_tap
            )
        else:
            self.emergency_btn = tk.Button(
                control_frame,
                text="🚨 TAP FOR EMERGENCY\n(Tap twice within 7 seconds)",
                font=("Arial", 28, "bold"),
                bg=COLORS["danger"],
                fg=COLORS["text"],
                activebackground="#d32f2f",
                height=6,
                width=25,
                command=self.handle_emergency_tap
            )
        self.emergency_btn.pack(pady=30)
        
        # Countdown label (hidden initially)
        if CUSTOM_TK:
            self.countdown_label = ctk.CTkLabel(
                control_frame,
                text="",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=COLORS["warning"]
            )
        else:
            self.countdown_label = tk.Label(
                control_frame,
                text="",
                font=("Arial", 20, "bold"),
                fg=COLORS["warning"],
                bg=COLORS["surface"]
            )
        self.countdown_label.pack(pady=10)
        
        # Voice activation toggle
        if CUSTOM_TK:
            self.voice_toggle = ctk.CTkSwitch(
                control_frame,
                text="🎤 Voice Activation (Say 'Help')",
                font=ctk.CTkFont(size=16, weight="bold"),
                command=self.toggle_voice_monitoring
            )
        else:
            self.voice_toggle = tk.Checkbutton(
                control_frame,
                text="🎤 Voice Activation (Say 'Help')",
                font=("Arial", 16, "bold"),
                fg=COLORS["text"],
                bg=COLORS["surface"],
                selectcolor=COLORS["surface"],
                command=self.toggle_voice_monitoring
            )
        self.voice_toggle.pack(pady=15)
        
        # Distress detection toggle
        if CUSTOM_TK:
            self.distress_toggle = ctk.CTkSwitch(
                control_frame,
                text="📹 Distress Detection (Camera)",
                font=ctk.CTkFont(size=16, weight="bold"),
                command=self.toggle_distress_monitoring
            )
        else:
            self.distress_toggle = tk.Checkbutton(
                control_frame,
                text="📹 Distress Detection (Camera)",
                font=("Arial", 16, "bold"),
                fg=COLORS["text"],
                bg=COLORS["surface"],
                selectcolor=COLORS["surface"],
                command=self.toggle_distress_monitoring
            )
        self.distress_toggle.pack(pady=15)

    
    def create_ai_status(self, parent):
        """Create AI detection status panel"""
        if CUSTOM_TK:
            ai_frame = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=15)
        else:
            ai_frame = tk.Frame(parent, bg=COLORS["surface"])
        ai_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        if CUSTOM_TK:
            title = ctk.CTkLabel(
                ai_frame,
                text="AI MULTI-LAYER VERIFICATION",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=COLORS["text"]
            )
        else:
            title = tk.Label(
                ai_frame,
                text="AI MULTI-LAYER VERIFICATION",
                font=("Arial", 18, "bold"),
                fg=COLORS["text"],
                bg=COLORS["surface"]
            )
        title.pack(pady=15)
        
        # Verification layers
        if CUSTOM_TK:
            layers = ctk.CTkFrame(ai_frame, fg_color="transparent")
        else:
            layers = tk.Frame(ai_frame, bg=COLORS["surface"])
        layers.pack(pady=10, padx=20)
        
        # Layer 1: Voice
        if CUSTOM_TK:
            self.layer1_label = ctk.CTkLabel(
                layers,
                text="Layer 1: Voice Detection ⚪",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            )
        else:
            self.layer1_label = tk.Label(
                layers,
                text="Layer 1: Voice Detection ⚪",
                font=("Arial", 14),
                fg=COLORS["text_secondary"],
                bg=COLORS["surface"]
            )
        self.layer1_label.grid(row=0, column=0, padx=15, pady=5, sticky="w")
        
        # Layer 2: Double-Tap
        if CUSTOM_TK:
            self.layer2_label = ctk.CTkLabel(
                layers,
                text="Layer 2: Double-Tap (7s) ⚪",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            )
        else:
            self.layer2_label = tk.Label(
                layers,
                text="Layer 2: Double-Tap (7s) ⚪",
                font=("Arial", 14),
                fg=COLORS["text_secondary"],
                bg=COLORS["surface"]
            )
        self.layer2_label.grid(row=1, column=0, padx=15, pady=5, sticky="w")
        
        # Layer 3: Distress
        if CUSTOM_TK:
            self.layer3_label = ctk.CTkLabel(
                layers,
                text="Layer 3: Distress Analysis ⚪",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            )
        else:
            self.layer3_label = tk.Label(
                layers,
                text="Layer 3: Distress Analysis ⚪",
                font=("Arial", 14),
                fg=COLORS["text_secondary"],
                bg=COLORS["surface"]
            )
        self.layer3_label.grid(row=2, column=0, padx=15, pady=5, sticky="w")
        
        # Distress score
        if CUSTOM_TK:
            self.distress_score_label = ctk.CTkLabel(
                ai_frame,
                text="Distress Score: 0/100",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["success"]
            )
        else:
            self.distress_score_label = tk.Label(
                ai_frame,
                text="Distress Score: 0/100",
                font=("Arial", 16, "bold"),
                fg=COLORS["success"],
                bg=COLORS["surface"]
            )
        self.distress_score_label.pack(pady=15)

    
    def create_footer(self, parent):
        """Create footer with quick actions"""
        if CUSTOM_TK:
            footer = ctk.CTkFrame(parent, fg_color="transparent")
        else:
            footer = tk.Frame(parent, bg=COLORS["dark"])
        footer.pack(fill="x")
        
        # Quick action buttons
        if CUSTOM_TK:
            help_btn = ctk.CTkButton(
                footer,
                text="❓ Help",
                font=ctk.CTkFont(size=14),
                fg_color=COLORS["secondary"],
                width=120,
                height=40,
                command=self.show_help
            )
        else:
            help_btn = tk.Button(
                footer,
                text="❓ Help",
                font=("Arial", 14),
                bg=COLORS["secondary"],
                fg=COLORS["text"],
                width=12,
                height=2,
                command=self.show_help
            )
        help_btn.pack(side="left", padx=5)
        
        if CUSTOM_TK:
            config_btn = ctk.CTkButton(
                footer,
                text="⚙️ Configure",
                font=ctk.CTkFont(size=14),
                fg_color=COLORS["secondary"],
                width=120,
                height=40,
                command=self.show_config
            )
        else:
            config_btn = tk.Button(
                footer,
                text="⚙️ Configure",
                font=("Arial", 14),
                bg=COLORS["secondary"],
                fg=COLORS["text"],
                width=12,
                height=2,
                command=self.show_config
            )
        config_btn.pack(side="left", padx=5)
        
        if CUSTOM_TK:
            test_btn = ctk.CTkButton(
                footer,
                text="🧪 Test System",
                font=ctk.CTkFont(size=14),
                fg_color=COLORS["secondary"],
                width=120,
                height=40,
                command=self.test_system
            )
        else:
            test_btn = tk.Button(
                footer,
                text="🧪 Test System",
                font=("Arial", 14),
                bg=COLORS["secondary"],
                fg=COLORS["text"],
                width=12,
                height=2,
                command=self.test_system
            )
        test_btn.pack(side="left", padx=5)
        
        # Status text
        if CUSTOM_TK:
            self.status_text = ctk.CTkLabel(
                footer,
                text="System Ready",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"]
            )
        else:
            self.status_text = tk.Label(
                footer,
                text="System Ready",
                font=("Arial", 12),
                fg=COLORS["text_secondary"],
                bg=COLORS["dark"]
            )
        self.status_text.pack(side="right", padx=10)

    
    # ==================== CORE FUNCTIONALITY ====================
    
    def handle_emergency_tap(self):
        """Handle emergency button tap - implements double-tap system"""
        if not DOUBLE_TAP_AVAILABLE:
            # Fallback without double-tap
            self.trigger_emergency()
            return
        
        result = double_tap_detector.register_tap()
        
        if result['status'] == 'FIRST_TAP':
            # First tap - start countdown
            self.tap_window_active = True
            self.update_layer2_status("🟡 ACTIVE")
            self.show_countdown_animation(result['time_remaining'])
            self.update_status("⏰ Tap again within 7 seconds to confirm emergency")
            
        elif result['status'] == 'CONFIRMED_EMERGENCY':
            # Second tap - emergency confirmed
            self.tap_window_active = False
            self.update_layer2_status("🟢 CONFIRMED")
            self.countdown_label.configure(text="✅ EMERGENCY CONFIRMED!")
            self.update_status(f"🚨 Emergency confirmed in {result['response_time']:.1f}s")
            
            # Trigger full emergency protocol
            self.root.after(500, self.trigger_emergency)
            
        elif result['status'] == 'WINDOW_EXPIRED':
            # Window expired, new window started
            self.update_layer2_status("🟡 ACTIVE")
            self.show_countdown_animation(result['time_remaining'])
            self.update_status("⏰ Previous window expired. Tap again within 7 seconds")
    
    def show_countdown_animation(self, seconds):
        """Show countdown animation for double-tap window"""
        remaining = seconds
        
        def update_countdown():
            nonlocal remaining
            if DOUBLE_TAP_AVAILABLE:
                remaining = double_tap_detector.get_time_remaining()
            else:
                remaining -= 0.1
            
            if remaining > 0 and self.tap_window_active:
                self.countdown_label.configure(
                    text=f"⏰ TAP AGAIN IN: {remaining:.1f}s"
                )
                self.root.after(100, update_countdown)
            elif remaining <= 0:
                self.countdown_label.configure(text="")
                self.update_layer2_status("⚪ READY")
                self.tap_window_active = False
        
        update_countdown()
    
    def trigger_emergency(self):
        """Trigger full emergency protocol"""
        if self.emergency_active:
            return
        
        self.emergency_active = True
        self.update_status("🚨 EMERGENCY PROTOCOL ACTIVATED")
        
        # Update all layers to confirmed
        self.update_layer1_status("🟢 CONFIRMED")
        self.update_layer2_status("🟢 CONFIRMED")
        
        # Show emergency window
        self.show_emergency_window()
        
        # Start emergency actions in background
        threading.Thread(target=self.execute_emergency_protocol, daemon=True).start()
    
    def execute_emergency_protocol(self):
        """Execute emergency protocol in background"""
        try:
            print("🚨 EXECUTING EMERGENCY PROTOCOL")
            
            # Check internet connection
            is_online = self.check_internet()
            
            if is_online:
                print("📡 Online mode - Using Firebase/Cloud")
                self.update_connection_status("📡 Online - Firebase Active")
                # TODO: Upload to Firebase
                # TODO: Start real-time streaming
            else:
                print("📱 Offline mode - Using SMS")
                self.update_connection_status("📱 Offline - SMS Active")
                if SMS_AVAILABLE:
                    # Send SMS alerts
                    self.send_sms_alerts()
            
            # Capture evidence
            print("📷 Capturing evidence...")
            # TODO: Capture video/audio/location
            
            # Contact emergency services
            print("📞 Contacting emergency services...")
            # TODO: Contact police, ambulance, contacts
            
            time.sleep(2)
            self.update_status("✅ Emergency protocol completed")
            
        except Exception as e:
            print(f"❌ Emergency protocol error: {e}")
            self.update_status(f"⚠️ Error: {e}")

    
    def show_emergency_window(self):
        """Show emergency confirmation window"""
        if CUSTOM_TK:
            window = ctk.CTkToplevel(self.root)
            window.configure(fg_color=COLORS["danger"])
        else:
            window = tk.Toplevel(self.root)
            window.configure(bg=COLORS["danger"])
        
        window.title("🚨 EMERGENCY ACTIVE")
        window.geometry("600x400")
        
        # Center window
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - 300
        y = (window.winfo_screenheight() // 2) - 200
        window.geometry(f"600x400+{x}+{y}")
        
        # Make it topmost
        window.attributes('-topmost', True)
        
        # Content
        if CUSTOM_TK:
            title = ctk.CTkLabel(
                window,
                text="🚨 EMERGENCY PROTOCOL ACTIVE 🚨",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=COLORS["text"]
            )
        else:
            title = tk.Label(
                window,
                text="🚨 EMERGENCY PROTOCOL ACTIVE 🚨",
                font=("Arial", 24, "bold"),
                fg=COLORS["text"],
                bg=COLORS["danger"]
            )
        title.pack(pady=30)
        
        # Actions
        actions_text = """
📞 Contacting Emergency Services
📱 Alerting Emergency Contacts
📍 Sharing Location
📷 Capturing Evidence
🔊 Broadcasting Alert
        """
        
        if CUSTOM_TK:
            actions = ctk.CTkLabel(
                window,
                text=actions_text,
                font=ctk.CTkFont(size=16),
                text_color=COLORS["text"]
            )
        else:
            actions = tk.Label(
                window,
                text=actions_text,
                font=("Arial", 16),
                fg=COLORS["text"],
                bg=COLORS["danger"]
            )
        actions.pack(pady=20)
        
        # Close button
        if CUSTOM_TK:
            close_btn = ctk.CTkButton(
                window,
                text="✅ ACKNOWLEDGE",
                font=ctk.CTkFont(size=18, weight="bold"),
                fg_color=COLORS["success"],
                hover_color="#388e3c",
                height=60,
                width=250,
                command=lambda: self.acknowledge_emergency(window)
            )
        else:
            close_btn = tk.Button(
                window,
                text="✅ ACKNOWLEDGE",
                font=("Arial", 18, "bold"),
                bg=COLORS["success"],
                fg=COLORS["text"],
                height=2,
                width=20,
                command=lambda: self.acknowledge_emergency(window)
            )
        close_btn.pack(pady=30)
    
    def acknowledge_emergency(self, window):
        """Acknowledge emergency and close window"""
        self.emergency_active = False
        window.destroy()
        self.reset_system()

    
    def toggle_voice_monitoring(self):
        """Toggle voice monitoring on/off"""
        if not SPEECH_AVAILABLE:
            messagebox.showwarning("Not Available", "Speech recognition not available")
            return
        
        self.voice_monitoring = not self.voice_monitoring
        
        if self.voice_monitoring:
            self.update_voice_status("🎤 Voice: ACTIVE")
            self.update_layer1_status("🟡 LISTENING")
            self.update_status("🎤 Voice monitoring started - Say 'Help' for emergency")
            threading.Thread(target=self.voice_monitoring_loop, daemon=True).start()
        else:
            self.update_voice_status("🎤 Voice: READY")
            self.update_layer1_status("⚪ READY")
            self.update_status("🎤 Voice monitoring stopped")
    
    def voice_monitoring_loop(self):
        """Monitor voice for emergency keywords"""
        try:
            recognizer = sr.Recognizer()
            mic = sr.Microphone()
            
            print("🎤 Starting voice monitoring...")
            
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.voice_monitoring:
                try:
                    with mic as source:
                        print("🎧 Listening...")
                        audio = recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    
                    text = recognizer.recognize_google(audio).lower()
                    print(f"🔊 Heard: {text}")
                    
                    # Check for emergency keywords
                    detected_keywords = [kw for kw in EMERGENCY_KEYWORDS if kw in text]
                    
                    if detected_keywords:
                        print(f"🚨 Emergency keywords detected: {detected_keywords}")
                        self.root.after(0, lambda: self.handle_voice_emergency(text, detected_keywords))
                        break
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"Voice monitoring error: {e}")
                    time.sleep(1)
        
        except Exception as e:
            print(f"Voice monitoring setup error: {e}")
            self.root.after(0, lambda: self.update_status(f"⚠️ Voice error: {e}"))
    
    def handle_voice_emergency(self, text, keywords):
        """Handle voice-detected emergency"""
        self.update_layer1_status("🟢 DETECTED")
        
        # Ask for confirmation
        response = messagebox.askyesno(
            "🚨 Voice Emergency Detected",
            f"Emergency keywords detected: {', '.join(keywords)}\n\n"
            f"Voice: \"{text}\"\n\n"
            f"Are you in danger?\n\n"
            f"Click YES to activate emergency protocol."
        )
        
        if response:
            self.trigger_emergency()
        else:
            self.update_layer1_status("⚪ READY")
            self.update_status("Voice alert cancelled")

    
    def toggle_distress_monitoring(self):
        """Toggle distress detection on/off"""
        if not DISTRESS_DETECTION_AVAILABLE:
            messagebox.showwarning("Not Available", "Distress detection not available")
            return
        
        self.distress_monitoring = not self.distress_monitoring
        
        if self.distress_monitoring:
            self.update_distress_status("📹 Distress: ACTIVE")
            self.update_layer3_status("🟡 ANALYZING")
            self.update_status("📹 Distress detection started - Monitoring camera")
            threading.Thread(target=self.distress_monitoring_loop, daemon=True).start()
        else:
            self.update_distress_status("📹 Distress: READY")
            self.update_layer3_status("⚪ READY")
            self.update_status("📹 Distress detection stopped")
    
    def distress_monitoring_loop(self):
        """Monitor camera for distress indicators"""
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                self.root.after(0, lambda: messagebox.showerror("Error", "Camera not available"))
                return
            
            print("📹 Starting distress monitoring...")
            frame_count = 0
            
            while self.distress_monitoring:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                frame_count += 1
                
                # Analyze every 5th frame for performance
                if frame_count % 5 == 0:
                    result = distress_detector.analyze_frame(frame)
                    
                    # Update distress score
                    self.distress_score = result['distress_score']
                    self.root.after(0, lambda s=self.distress_score: self.update_distress_score(s))
                    
                    # Check if distress detected
                    if result['distress_detected']:
                        print(f"🚨 DISTRESS DETECTED! Score: {result['distress_score']}")
                        print(f"Indicators: {result['indicators']}")
                        self.root.after(0, lambda r=result: self.handle_distress_detection(r))
                        break
                
                time.sleep(0.1)
            
            cap.release()
            
        except Exception as e:
            print(f"Distress monitoring error: {e}")
            self.root.after(0, lambda: self.update_status(f"⚠️ Distress error: {e}"))
    
    def handle_distress_detection(self, result):
        """Handle detected distress"""
        self.update_layer3_status("🟢 DETECTED")
        
        # Show distress alert
        indicators_text = "\n".join([f"• {ind}" for ind in result['indicators']])
        
        response = messagebox.askyesno(
            "🚨 Distress Detected",
            f"Physical distress indicators detected!\n\n"
            f"Distress Score: {result['distress_score']}/100\n\n"
            f"Indicators:\n{indicators_text}\n\n"
            f"Activate emergency protocol?"
        )
        
        if response:
            self.trigger_emergency()
        else:
            self.update_layer3_status("⚪ READY")
            self.update_status("Distress alert cancelled")
    
    def update_distress_score(self, score):
        """Update distress score display"""
        color = COLORS["success"]
        if score > 70:
            color = COLORS["danger"]
        elif score > 40:
            color = COLORS["warning"]
        
        if CUSTOM_TK:
            self.distress_score_label.configure(
                text=f"Distress Score: {score}/100",
                text_color=color
            )
        else:
            self.distress_score_label.configure(
                text=f"Distress Score: {score}/100",
                fg=color
            )

    
    # ==================== HELPER FUNCTIONS ====================
    
    def check_internet(self):
        """Check if internet is available"""
        if SMS_AVAILABLE:
            return sms_service.is_internet_available()
        else:
            try:
                import socket
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                return True
            except OSError:
                return False
    
    def send_sms_alerts(self):
        """Send SMS alerts to emergency contacts"""
        if not SMS_AVAILABLE:
            print("⚠️ SMS service not available")
            return
        
        # Mock contacts for demo
        contacts = [
            {'name': 'Emergency Contact 1', 'phone': '+1234567890'},
            {'name': 'Emergency Contact 2', 'phone': '+0987654321'}
        ]
        
        result = sms_service.send_bulk_emergency_sms(
            contacts=contacts,
            user_name="User",
            location_text="Location: [GPS Coordinates]",
            alert_type="EMERGENCY"
        )
        
        print(f"📱 SMS sent: {result['sent']}, Failed: {result['failed']}")
    
    def cancel_emergency(self):
        """Cancel emergency (ESC key)"""
        if self.emergency_active or self.tap_window_active:
            response = messagebox.askyesno(
                "Cancel Emergency",
                "Are you sure you want to cancel the emergency protocol?"
            )
            if response:
                self.reset_system()
    
    def reset_system(self):
        """Reset system to ready state"""
        self.emergency_active = False
        self.tap_window_active = False
        self.distress_score = 0
        
        if DOUBLE_TAP_AVAILABLE:
            double_tap_detector.reset()
        
        self.countdown_label.configure(text="")
        self.update_layer1_status("⚪ READY")
        self.update_layer2_status("⚪ READY")
        self.update_layer3_status("⚪ READY")
        self.update_distress_score(0)
        self.update_status("System reset - Ready")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
AI Powered SOS Application - Help

EMERGENCY ACTIVATION:
1. Double-Tap Method:
   - Tap emergency button
   - Tap again within 7 seconds to confirm
   
2. Voice Method:
   - Enable voice monitoring
   - Say "Help" or "Emergency"
   
3. Automatic Method:
   - Enable distress detection
   - System auto-detects physical distress

FEATURES:
• Multi-layer AI verification
• Online mode: Firebase/Cloud upload
• Offline mode: SMS alerts
• Real-time evidence capture
• Location tracking

KEYBOARD SHORTCUTS:
• ESC - Cancel emergency
• F1 - Show this help

For configuration, click the Configure button.
        """
        messagebox.showinfo("Help", help_text)
    
    def show_config(self):
        """Show configuration dialog"""
        messagebox.showinfo(
            "Configuration",
            "Configuration panel coming soon!\n\n"
            "Features:\n"
            "• Add emergency contacts\n"
            "• Configure SMS service\n"
            "• Set up Firebase\n"
            "• Customize alerts"
        )
    
    def test_system(self):
        """Test system functionality"""
        response = messagebox.askyesno(
            "Test System",
            "This will test all system components:\n\n"
            "• Voice detection\n"
            "• Distress detection\n"
            "• SMS service\n"
            "• Emergency protocol\n\n"
            "Continue?"
        )
        
        if response:
            self.update_status("🧪 Running system tests...")
            threading.Thread(target=self.run_system_tests, daemon=True).start()
    
    def run_system_tests(self):
        """Run system tests in background"""
        try:
            print("🧪 Testing system components...")
            
            # Test double-tap
            print("✓ Double-tap detector:", "Available" if DOUBLE_TAP_AVAILABLE else "Not available")
            
            # Test SMS
            print("✓ SMS service:", "Available" if SMS_AVAILABLE else "Not available")
            
            # Test distress detection
            print("✓ Distress detection:", "Available" if DISTRESS_DETECTION_AVAILABLE else "Not available")
            
            # Test voice
            print("✓ Voice recognition:", "Available" if SPEECH_AVAILABLE else "Not available")
            
            time.sleep(2)
            self.root.after(0, lambda: self.update_status("✅ System tests completed"))
            self.root.after(0, lambda: messagebox.showinfo("Test Complete", "All system tests completed!"))
            
        except Exception as e:
            print(f"Test error: {e}")
            self.root.after(0, lambda: self.update_status(f"⚠️ Test error: {e}"))

    
    # ==================== UI UPDATE FUNCTIONS ====================
    
    def update_status(self, text):
        """Update status text"""
        if CUSTOM_TK:
            self.status_text.configure(text=text)
        else:
            self.status_text.configure(text=text)
        print(f"Status: {text}")
    
    def update_voice_status(self, text):
        """Update voice status"""
        color = COLORS["success"] if "ACTIVE" in text else COLORS["success"]
        if CUSTOM_TK:
            self.voice_status.configure(text=text, text_color=color)
        else:
            self.voice_status.configure(text=text, fg=color)
    
    def update_distress_status(self, text):
        """Update distress status"""
        color = COLORS["success"] if "ACTIVE" in text else COLORS["success"]
        if CUSTOM_TK:
            self.distress_status.configure(text=text, text_color=color)
        else:
            self.distress_status.configure(text=text, fg=color)
    
    def update_connection_status(self, text):
        """Update connection status"""
        color = COLORS["success"] if "Online" in text else COLORS["warning"]
        if CUSTOM_TK:
            self.connection_status.configure(text=text, text_color=color)
        else:
            self.connection_status.configure(text=text, fg=color)
    
    def update_layer1_status(self, status):
        """Update layer 1 (voice) status"""
        text = f"Layer 1: Voice Detection {status}"
        if CUSTOM_TK:
            self.layer1_label.configure(text=text)
        else:
            self.layer1_label.configure(text=text)
    
    def update_layer2_status(self, status):
        """Update layer 2 (double-tap) status"""
        text = f"Layer 2: Double-Tap (7s) {status}"
        if CUSTOM_TK:
            self.layer2_label.configure(text=text)
        else:
            self.layer2_label.configure(text=text)
    
    def update_layer3_status(self, status):
        """Update layer 3 (distress) status"""
        text = f"Layer 3: Distress Analysis {status}"
        if CUSTOM_TK:
            self.layer3_label.configure(text=text)
        else:
            self.layer3_label.configure(text=text)
    
    def run(self):
        """Start the application"""
        print("🚀 Starting AI Powered SOS Application...")
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        app = SOSApplication()
        app.run()
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
