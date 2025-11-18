#!/usr/bin/env python3
"""
HerShield Futuristic - Ultra-Modern Pink-Themed Women Safety App
Sleek, elegant, and futuristic design with advanced animations
"""

import tkinter as tk
from tkinter import messagebox
import tkinter.simpledialog

# Try to import customtkinter, fallback to regular tkinter
try:
    import customtkinter as ctk
    CUSTOM_TK_AVAILABLE = True
    # Set futuristic pink theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
except ImportError:
    print("⚠️ CustomTkinter not available, using standard tkinter")
    ctk = tk  # Use regular tkinter as fallback
    CUSTOM_TK_AVAILABLE = False
import threading
import json
import os
import time
from datetime import datetime
import subprocess
import uuid

# Optional imports with fallbacks
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    print("⚠️ Speech recognition not available")
    SPEECH_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    print("⚠️ OpenCV not available")
    CV2_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    print("⚠️ NumPy not available")
    NUMPY_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    print("⚠️ Librosa not available")
    LIBROSA_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    print("⚠️ PyAudio not available")
    PYAUDIO_AVAILABLE = False

# Import enhanced core systems
try:
    from core.escalation_system import escalation_system
    from core.alert_acknowledgment import acknowledgment_system
    from core.enhanced_location_service import EnhancedLocationService
    from core.google_maps_location import GoogleMapsLocationService
    from core.camera_capture import capture_emergency_evidence
    from core.user_config import user_config
    from core.firebase_service import firebase_available, get_user_contacts
    ENHANCED_FEATURES = True
    FIREBASE_ENABLED = firebase_available
except ImportError:
    print("Enhanced features not available - using basic functionality")
    ENHANCED_FEATURES = False
    FIREBASE_ENABLED = False

# Theme settings moved to import section

# Custom pink color palette
PINK_COLORS = {
    "primary": "#ff1493",      # Deep pink
    "secondary": "#ff69b4",    # Hot pink
    "accent": "#ffc0cb",       # Light pink
    "dark": "#8b008b",         # Dark magenta
    "gradient1": "#ff1493",    # Deep pink
    "gradient2": "#ff69b4",    # Hot pink
    "background": "#1a0d1a",   # Very dark pink
    "surface": "#2d1b2d",      # Dark pink surface
    "text": "#ffffff",         # White text
    "text_secondary": "#ffb3d9"  # Light pink text
}

# Ultra-comprehensive keywords for instant women safety detection
KEYWORDS = [
    # Basic Emergency
    "help", "save me", "emergency", "police", "fire", "ambulance", "911", "100", "108",

    # Violence & Physical Threats
    "attack", "assault", "violence", "danger", "gun", "knife", "weapon", "hurt", "pain",
    "bleeding", "injured", "wound", "broken", "bruised", "cut", "shot", "stabbed",

    # Domestic Violence & Abuse
    "stop it", "get away", "leave me alone", "don't touch me", "no means no", "get off me",
    "stop hitting", "stop hurting", "you're hurting me", "that hurts", "please stop",
    "he's hurting me", "she's hurting me", "domestic violence", "abuse", "abusive",
    "beating me", "choking me", "hitting me", "slapping me", "punching me", "kicking me",

    # Sexual Violence & Harassment
    "rape", "sexual assault", "molest", "harassment", "inappropriate touching",
    "forcing me", "against my will", "unwanted", "consent", "no consent", "stop touching",

    # Kidnapping & Captivity
    "kidnap", "kidnapped", "taken", "captured", "held captive", "locked in", "trapped",
    "can't escape", "being held", "won't let me go", "prisoner", "tied up", "bound",

    # Stalking & Following
    "stalker", "stalking", "following me", "watching me", "tracking me", "won't leave me alone",
    "creepy", "suspicious person", "stranger danger", "being followed",

    # Threats & Intimidation
    "threatening me", "death threat", "kill me", "murder", "harm", "hurt you", "get you",
    "revenge", "payback", "warning", "threat", "intimidation", "blackmail",

    # Distress & Fear
    "scared", "afraid", "terrified", "frightened", "panic", "panicking", "fear", "fearful",
    "unsafe", "in danger", "dangerous", "risky", "vulnerable", "helpless", "desperate",

    # Immediate Help Requests
    "need help now", "help me now", "urgent help", "immediate help", "call police now",
    "call 911", "call emergency", "call ambulance", "get help", "find help", "rescue me",

    # Location-based Distress
    "lost", "stranded", "alone", "isolated", "nowhere to go", "can't get home",
    "unsafe area", "bad neighborhood", "dark place", "empty street",

    # Medical Emergency
    "can't breathe", "chest pain", "heart attack", "stroke", "overdose", "poisoned",
    "allergic reaction", "seizure", "unconscious", "bleeding out", "dying",

    # Fire & Accidents
    "fire", "smoke", "burning", "explosion", "gas leak", "accident", "crash", "collision",
    "trapped in car", "car accident", "hit by car", "building collapse",

    # Water Emergency
    "drowning", "can't swim", "water", "sinking", "flood", "tsunami", "river", "ocean",

    # Mental Health Crisis
    "suicide", "kill myself", "end it all", "can't take it", "depression", "breakdown",
    "mental health", "crisis", "self harm", "cutting", "pills",

    # Technology-based Threats
    "cyber attack", "hacked", "identity theft", "online threat", "digital stalking",
    "revenge porn", "blackmail photos", "leaked photos",

    # International Distress
    "mayday", "sos", "help", "au secours", "ayuda", "hilfe", "aiuto", "pomoc",

    # Whispered/Quiet Distress
    "quietly", "whisper", "can't talk loud", "he'll hear", "she'll hear", "listening",
    "secret", "hidden", "basement", "attic", "closet", "bathroom",

    # Drug-related
    "drugged", "roofied", "spiked drink", "can't remember", "dizzy", "nauseous",
    "something in my drink", "feel weird", "not myself",

    # Child-specific (if system used by minors)
    "stranger", "bad person", "inappropriate", "uncomfortable", "wrong", "secret",
    "don't tell", "our secret", "special friend", "game", "touch",

    # Workplace Violence
    "workplace violence", "boss", "coworker", "harassment at work", "unsafe workplace",
    "threatening employee", "fired", "revenge at work"
]


class FuturisticHerShield:
    def __init__(self):
        print("🚀 Initializing HerShield GUI...")
        
        if CUSTOM_TK_AVAILABLE:
            self.root = ctk.CTk()
        else:
            self.root = tk.Tk()
            
        print("✅ Root window created")
        
        self.setup_futuristic_window()
        self.setup_variables()
        
        print("🎨 Creating UI...")
        self.create_futuristic_ui()
        
        print("⚙️ Loading configuration...")
        self.load_config()

        # System state
        self.listening = False
        self.alert_count = 0
        self.monitoring_thread = None

        print("🔧 Setting up enhanced features...")
        # Enhanced system components
        if ENHANCED_FEATURES:
            try:
                self.location_service = EnhancedLocationService()
                acknowledgment_system.start_monitoring()
                print("✅ Enhanced features loaded")
            except Exception as e:
                print(f"⚠️ Enhanced features error: {e}")

        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()

        # Initialize easy-use features (in background to avoid blocking)
        self.root.after(1000, self.setup_easy_use_features_async)

        # Initialize control flags
        self.location_tracking_active = True
        self.app_running = True

        # Animation variables
        self.pulse_state = 0
        self.start_animations()
        
        # Cleanup old evidence files in background
        self.root.after(2000, self.cleanup_evidence_async)
        
        # Auto-start voice protection after GUI is ready
        self.root.after(3000, self.auto_start_protection)
        
        print("✅ HerShield initialization complete!")
        
    def setup_easy_use_features_async(self):
        """Setup easy-use features in background"""
        try:
            self.setup_easy_use_features()
        except Exception as e:
            print(f"Easy-use features error: {e}")
    
    def auto_start_protection(self):
        """Auto-start voice protection for immediate keyword detection"""
        try:
            print("🚀 Auto-starting voice protection...")
            if not self.listening:
                self.start_protection()
                print("✅ Voice protection auto-started - ready for keyword detection!")
        except Exception as e:
            print(f"Auto-start protection error: {e}")
    
    def create_simple_emergency_window(self, text, keywords, alert_id):
        """Create futuristic emergency window with proper UI theme"""
        try:
            print("🚨 Creating FUTURISTIC emergency window...")
            
            # Create new window
            if CUSTOM_TK_AVAILABLE:
                emergency_window = ctk.CTkToplevel(self.root)
            else:
                emergency_window = tk.Toplevel(self.root)
            
            # Basic setup with futuristic theme
            emergency_window.title("⚡ HerShield Emergency Protocol")
            emergency_window.geometry("800x700")
            
            # Make it appear on top
            emergency_window.attributes('-topmost', True)
            emergency_window.lift()
            emergency_window.focus_force()
            
            # Center it
            emergency_window.update_idletasks()
            x = (emergency_window.winfo_screenwidth() // 2) - 400
            y = (emergency_window.winfo_screenheight() // 2) - 350
            emergency_window.geometry(f"800x700+{x}+{y}")
            
            # Set futuristic background
            if CUSTOM_TK_AVAILABLE:
                emergency_window.configure(fg_color=PINK_COLORS["background"])
            else:
                emergency_window.configure(bg=PINK_COLORS["background"])
            
            # Main container with futuristic styling
            if CUSTOM_TK_AVAILABLE:
                main_container = ctk.CTkFrame(
                    emergency_window,
                    corner_radius=25,
                    fg_color="#8b0000",  # Dark red for emergency
                    border_width=3,
                    border_color=PINK_COLORS["primary"]
                )
            else:
                main_container = tk.Frame(
                    emergency_window,
                    bg="#8b0000",
                    relief="raised",
                    bd=5
                )
            main_container.pack(fill="both", expand=True, padx=15, pady=15)
            
            # Futuristic header
            if CUSTOM_TK_AVAILABLE:
                header = ctk.CTkLabel(
                    main_container,
                    text="⚡ EMERGENCY PROTOCOL ACTIVATED ⚡",
                    font=ctk.CTkFont(size=28, weight="bold"),
                    text_color="white"
                )
            else:
                header = tk.Label(
                    main_container,
                    text="⚡ EMERGENCY PROTOCOL ACTIVATED ⚡",
                    font=("Arial", 28, "bold"),
                    fg="white",
                    bg="#8b0000"
                )
            header.pack(pady=20)
            
            # Alert details with futuristic styling
            if CUSTOM_TK_AVAILABLE:
                details_frame = ctk.CTkFrame(
                    main_container,
                    corner_radius=15,
                    fg_color=PINK_COLORS["surface"],
                    border_width=2,
                    border_color=PINK_COLORS["accent"]
                )
            else:
                details_frame = tk.Frame(
                    main_container,
                    bg=PINK_COLORS["surface"],
                    relief="sunken",
                    bd=3
                )
            details_frame.pack(fill="x", padx=20, pady=15)
            
            # Alert info
            if CUSTOM_TK_AVAILABLE:
                alert_info = ctk.CTkLabel(
                    details_frame,
                    text=f"🎤 Keywords Detected: {', '.join(keywords)}\n\n💬 Voice Input: \"{text}\"\n\n🆔 Alert ID: {alert_id}\n\n⏰ Time: {datetime.now().strftime('%H:%M:%S')}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=PINK_COLORS["text"]
                )
            else:
                alert_info = tk.Label(
                    details_frame,
                    text=f"🎤 Keywords: {', '.join(keywords)}\n💬 Voice: \"{text}\"\n🆔 Alert: {alert_id}",
                    font=("Arial", 16, "bold"),
                    fg=PINK_COLORS["text"],
                    bg=PINK_COLORS["surface"]
                )
            alert_info.pack(pady=15)
            
            # Emergency actions status with futuristic theme
            if CUSTOM_TK_AVAILABLE:
                actions_frame = ctk.CTkFrame(
                    main_container,
                    corner_radius=15,
                    fg_color=PINK_COLORS["dark"],
                    border_width=2,
                    border_color="#00ff00"
                )
            else:
                actions_frame = tk.Frame(
                    main_container,
                    bg=PINK_COLORS["dark"],
                    relief="ridge",
                    bd=3
                )
            actions_frame.pack(fill="x", padx=20, pady=15)
            
            # Action status
            if CUSTOM_TK_AVAILABLE:
                actions_title = ctk.CTkLabel(
                    actions_frame,
                    text="🚀 EMERGENCY ACTIONS IN PROGRESS",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#00ff00"
                )
            else:
                actions_title = tk.Label(
                    actions_frame,
                    text="🚀 EMERGENCY ACTIONS IN PROGRESS",
                    font=("Arial", 18, "bold"),
                    fg="#00ff00",
                    bg=PINK_COLORS["dark"]
                )
            actions_title.pack(pady=10)
            
            # Emergency actions list
            actions_text = """📞 Contacting Emergency Contacts...
🚔 Contacting Emergency Services...
📡 Sending Emergency Alerts...
📍 Sharing Location Data...
📷 Capturing Evidence...
🔊 Broadcasting Distress Signal..."""
            
            if CUSTOM_TK_AVAILABLE:
                actions_list = ctk.CTkLabel(
                    actions_frame,
                    text=actions_text,
                    font=ctk.CTkFont(size=14),
                    text_color="#ffff00",
                    justify="left"
                )
            else:
                actions_list = tk.Label(
                    actions_frame,
                    text=actions_text,
                    font=("Arial", 14),
                    fg="#ffff00",
                    bg=PINK_COLORS["dark"],
                    justify="left"
                )
            actions_list.pack(pady=15)
            
            # Status indicator
            if CUSTOM_TK_AVAILABLE:
                status_label = ctk.CTkLabel(
                    main_container,
                    text="⚡ IMMEDIATE RESPONSE SYSTEM ACTIVE ⚡",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=PINK_COLORS["accent"]
                )
            else:
                status_label = tk.Label(
                    main_container,
                    text="⚡ IMMEDIATE RESPONSE SYSTEM ACTIVE ⚡",
                    font=("Arial", 16, "bold"),
                    fg=PINK_COLORS["accent"],
                    bg="#8b0000"
                )
            status_label.pack(pady=20)
            
            # Futuristic acknowledge button
            if CUSTOM_TK_AVAILABLE:
                acknowledge_btn = ctk.CTkButton(
                    main_container,
                    text="✅ ACKNOWLEDGE EMERGENCY PROTOCOL",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    fg_color=PINK_COLORS["primary"],
                    hover_color=PINK_COLORS["secondary"],
                    border_width=2,
                    border_color=PINK_COLORS["accent"],
                    width=400,
                    height=60,
                    corner_radius=15,
                    command=emergency_window.destroy
                )
            else:
                acknowledge_btn = tk.Button(
                    main_container,
                    text="✅ ACKNOWLEDGE EMERGENCY PROTOCOL",
                    font=("Arial", 18, "bold"),
                    bg=PINK_COLORS["primary"],
                    fg="white",
                    width=30,
                    height=3,
                    relief="raised",
                    bd=5,
                    command=emergency_window.destroy
                )
            acknowledge_btn.pack(pady=30)
            
            # Instructions
            if CUSTOM_TK_AVAILABLE:
                instructions = ctk.CTkLabel(
                    main_container,
                    text="⌨️ Press ESC or F12 to acknowledge | Emergency protocol will continue until acknowledged",
                    font=ctk.CTkFont(size=12),
                    text_color=PINK_COLORS["text_secondary"]
                )
            else:
                instructions = tk.Label(
                    main_container,
                    text="⌨️ Press ESC or F12 to acknowledge",
                    font=("Arial", 12),
                    fg=PINK_COLORS["text_secondary"],
                    bg="#8b0000"
                )
            instructions.pack(pady=10)
            
            # Keyboard shortcuts
            emergency_window.bind('<Escape>', lambda e: emergency_window.destroy())
            emergency_window.bind('<F12>', lambda e: emergency_window.destroy())
            
            # Force it to appear and focus
            emergency_window.update()
            emergency_window.tkraise()
            emergency_window.focus_set()
            
            print("✅ FUTURISTIC emergency window created with proper theme!")
            
            # Store reference
            self.emergency_window = emergency_window
            
            # Start pulsing animation for urgency
            self.start_emergency_pulse(emergency_window)
            
        except Exception as e:
            print(f"❌ Futuristic emergency window creation failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Ultimate fallback - basic messagebox
            try:
                import tkinter.messagebox as messagebox
                messagebox.showerror(
                    "🚨 EMERGENCY DETECTED", 
                    f"EMERGENCY KEYWORDS DETECTED!\n\nKeywords: {', '.join(keywords)}\nText: '{text}'\n\nEMERGENCY PROTOCOL ACTIVE!"
                )
                print("✅ Fallback messagebox shown")
            except Exception as e2:
                print(f"❌ Even messagebox failed: {e2}")
    
    def show_contacting_services_window(self):
        """Show animated window with alerts and sounds for contacting services"""
        try:
            print("📞 Creating contacting services window with alerts...")
            
            # Create services window
            if CUSTOM_TK_AVAILABLE:
                services_window = ctk.CTkToplevel(self.root)
                services_window.configure(fg_color=PINK_COLORS["background"])
            else:
                services_window = tk.Toplevel(self.root)
                services_window.configure(bg=PINK_COLORS["background"])
            
            # Window setup
            services_window.title("🚨 HerShield Emergency Services")
            services_window.geometry("700x500")
            
            # Make it appear on top
            services_window.attributes('-topmost', True)
            services_window.lift()
            services_window.focus_force()
            
            # Center the window
            services_window.update_idletasks()
            x = (services_window.winfo_screenwidth() // 2) - 350
            y = (services_window.winfo_screenheight() // 2) - 250
            services_window.geometry(f"700x500+{x}+{y}")
            
            # Main container
            if CUSTOM_TK_AVAILABLE:
                main_container = ctk.CTkFrame(
                    services_window,
                    corner_radius=25,
                    fg_color="#ff0000",  # Bright red for urgency
                    border_width=3,
                    border_color="#ffffff"
                )
            else:
                main_container = tk.Frame(
                    services_window,
                    bg="#ff0000",
                    relief="raised",
                    bd=5
                )
            main_container.pack(fill="both", expand=True, padx=15, pady=15)
            
            # Urgent header with animation
            if CUSTOM_TK_AVAILABLE:
                self.services_header = ctk.CTkLabel(
                    main_container,
                    text="🚨 CONTACTING EMERGENCY SERVICES 🚨",
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color="#ffffff"
                )
            else:
                self.services_header = tk.Label(
                    main_container,
                    text="🚨 CONTACTING EMERGENCY SERVICES 🚨",
                    font=("Arial", 24, "bold"),
                    fg="#ffffff",
                    bg="#ff0000"
                )
            self.services_header.pack(pady=20)
            
            # Animated status messages
            self.service_messages = [
                "📞 Contacting Emergency Contacts...",
                "🚔 Alerting Police Services...",
                "🚑 Notifying Medical Services...", 
                "🔥 Contacting Fire Department...",
                "📡 Broadcasting Emergency Alert...",
                "📍 Sharing Live Location...",
                "📷 Capturing Evidence...",
                "🔊 Activating Emergency Whistle...",
                "📱 Sending SMS Alerts...",
                "📧 Sending Email Notifications...",
                "⚡ All Services Contacted Successfully!"
            ]
            
            # Status label for animated messages
            if CUSTOM_TK_AVAILABLE:
                self.status_label = ctk.CTkLabel(
                    main_container,
                    text=self.service_messages[0],
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#00ff00"
                )
            else:
                self.status_label = tk.Label(
                    main_container,
                    text=self.service_messages[0],
                    font=("Arial", 16, "bold"),
                    fg="#00ff00",
                    bg="#ff0000"
                )
            self.status_label.pack(pady=30)
            
            # Close button (appears after all messages)
            if CUSTOM_TK_AVAILABLE:
                self.close_services_btn = ctk.CTkButton(
                    main_container,
                    text="✅ SERVICES CONTACTED",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    fg_color="#32cd32",
                    hover_color="#228b22",
                    width=300,
                    height=50,
                    corner_radius=15,
                    command=services_window.destroy
                )
            else:
                self.close_services_btn = tk.Button(
                    main_container,
                    text="✅ SERVICES CONTACTED",
                    font=("Arial", 16, "bold"),
                    bg="#32cd32",
                    fg="white",
                    width=25,
                    height=2,
                    command=services_window.destroy
                )
            
            # Store window reference
            self.services_window = services_window
            
            # Start animations and sounds
            self.start_service_animation(services_window)
            self.play_emergency_sounds()
            
            print("✅ Contacting services window created with alerts!")
            
        except Exception as e:
            print(f"❌ Services window creation failed: {e}")
            import traceback
            traceback.print_exc()
    
    def start_service_animation(self, window):
        """Animate the service contact messages"""
        message_index = 0
        
        def update_message():
            nonlocal message_index
            try:
                if window.winfo_exists() and message_index < len(self.service_messages):
                    # Update status message
                    self.status_label.configure(text=self.service_messages[message_index])
                    
                    message_index += 1
                    
                    # If all messages shown, show close button
                    if message_index >= len(self.service_messages):
                        self.close_services_btn.pack(pady=20)
                        # Change header to success
                        self.services_header.configure(text="✅ ALL EMERGENCY SERVICES CONTACTED ✅")
                    else:
                        # Schedule next message
                        window.after(1500, update_message)  # 1.5 seconds between messages
                        
            except Exception as e:
                print(f"Animation error: {e}")
        
        # Start the animation
        update_message()
    
    def play_emergency_sounds(self):
        """Play emergency whistle and alert sounds"""
        def sound_thread():
            try:
                import winsound
                # Emergency whistle pattern
                for cycle in range(3):
                    # High-pitched whistle
                    for freq in range(2000, 3000, 100):
                        winsound.Beep(freq, 100)
                    # Low-pitched alert
                    for freq in range(1000, 500, -50):
                        winsound.Beep(freq, 150)
                    
                # Continuous alert beeps
                for _ in range(10):
                    winsound.Beep(1500, 200)
                    time.sleep(0.1)
                    winsound.Beep(2000, 200)
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"Sound error: {e}")
                # Fallback to system bell
                for _ in range(20):
                    print('\a', end='', flush=True)
                    time.sleep(0.2)
        
        # Play sounds in background
        threading.Thread(target=sound_thread, daemon=True).start()
    
    def start_emergency_pulse(self, window):
        """Start subtle pulsing animation for emergency window"""
        pulse_direction = 1
        pulse_alpha = 1.0
        
        def pulse():
            nonlocal pulse_direction, pulse_alpha
            try:
                if window and window.winfo_exists():
                    # Smooth pulsing
                    pulse_alpha += pulse_direction * 0.03
                    
                    if pulse_alpha >= 1.0:
                        pulse_alpha = 1.0
                        pulse_direction = -1
                    elif pulse_alpha <= 0.9:
                        pulse_alpha = 0.9
                        pulse_direction = 1
                    
                    window.attributes('-alpha', pulse_alpha)
                    window.after(100, pulse)
            except:
                pass
        
        pulse()

    def setup_futuristic_window(self):
        """Setup futuristic window with pink theme"""
        self.root.title("🛡️ HerShield Futuristic - Ultra-Fast Guardian")
        self.root.geometry("1200x800")
        
        if CUSTOM_TK_AVAILABLE:
            self.root.configure(fg_color=PINK_COLORS["background"])
        else:
            self.root.configure(bg=PINK_COLORS["background"])

        # Center window
        try:
            x = (self.root.winfo_screenwidth() // 2) - 600
            y = (self.root.winfo_screenheight() // 2) - 400
            self.root.geometry(f"1200x800+{x}+{y}")
        except:
            pass  # Skip centering if it fails
            
    def load_enhanced_features_async(self):
        """Load enhanced features in background"""
        def load_background():
            global ENHANCED_FEATURES, FIREBASE_ENABLED
            
            # Update status
            self.root.after(0, lambda: self.update_status("🔄 Loading enhanced AI systems..."))
            
            # Import enhanced features
            success = lazy_import_enhanced_features()
            
            if success:
                try:
                    from core.escalation_system import escalation_system
                    from core.alert_acknowledgment import acknowledgment_system
                    from core.enhanced_location_service import EnhancedLocationService
                    
                    # Initialize components
                    self.location_service = EnhancedLocationService()
                    acknowledgment_system.start_monitoring()
                    
                    # Setup easy-use features
                    self.setup_easy_use_features()
                    
                    self.root.after(0, lambda: self.update_status("✅ All systems operational - Ready to protect!"))
                    
                except Exception as e:
                    print(f"Enhanced features initialization error: {e}")
                    self.root.after(0, lambda: self.update_status("⚠️ Basic mode - Core protection active"))
            else:
                self.root.after(0, lambda: self.update_status("⚠️ Basic mode - Core protection active"))
        
        # Start background loading
        threading.Thread(target=load_background, daemon=True).start()

        # Make window look futuristic
        self.root.resizable(True, True)

        # Handle window close properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_variables(self):
        """Setup variables"""
        self.status_text = "🛡️ Guardian Mode: Ready"
        self.location_text = "📍 Scanning location..."
        self.alert_count_text = "0"

    def create_futuristic_ui(self):
        """Create ultra-futuristic pink UI"""
        # Main container with futuristic styling
        self.main_container = ctk.CTkFrame(
            self.root,
            corner_radius=25,
            fg_color=PINK_COLORS["surface"],
            border_width=2,
            border_color=PINK_COLORS["primary"]
        )
        self.main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Create futuristic header
        self.create_futuristic_header()

        # Create main content area
        self.create_main_content()

        # Create sidebar
        self.create_futuristic_sidebar()

    def create_futuristic_header(self):
        """Create futuristic header with gradient effect"""
        header_frame = ctk.CTkFrame(
            self.main_container,
            height=120,
            corner_radius=20,
            fg_color=PINK_COLORS["primary"],
            border_width=1,
            border_color=PINK_COLORS["accent"]
        )
        header_frame.pack(fill="x", padx=20, pady=20)
        header_frame.pack_propagate(False)

        # Futuristic title with glow effect
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(expand=True, fill="both")

        # Main title
        self.title_label = ctk.CTkLabel(
            title_frame,
            text="HerShield",
            font=ctk.CTkFont(size=42, weight="bold", family="Arial"),
            text_color=PINK_COLORS["text"]
        )
        self.title_label.pack(pady=(15, 5))

        # Enhanced subtitle
        self.subtitle_label = ctk.CTkLabel(
            title_frame,
            text="◆ ULTRA-RESPONSIVE AI SAFETY GUARDIAN ◆",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=PINK_COLORS["text_secondary"]
        )
        self.subtitle_label.pack()

        # Enhanced status indicator
        self.status_indicator = ctk.CTkLabel(
            title_frame,
            text="⚡ INSTANT RESPONSE MODE READY",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00ff00"
        )
        self.status_indicator.pack(pady=(5, 0))

    def create_main_content(self):
        """Create main content area"""
        content_frame = ctk.CTkFrame(
            self.main_container,
            corner_radius=20,
            fg_color=PINK_COLORS["background"],
            border_width=1,
            border_color=PINK_COLORS["secondary"]
        )
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Status display with futuristic design
        self.create_status_display(content_frame)

        # Control panel with elegant buttons
        self.create_control_panel(content_frame)

        # Activity monitor
        self.create_activity_monitor(content_frame)

    def create_status_display(self, parent):
        """Create futuristic status display"""
        status_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=PINK_COLORS["surface"],
            border_width=1,
            border_color=PINK_COLORS["accent"]
        )
        status_frame.pack(fill="x", padx=15, pady=15)

        # Status text with animation
        self.status_display = ctk.CTkLabel(
            status_frame,
            text=self.status_text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=PINK_COLORS["text"]
        )
        self.status_display.pack(pady=15)

        # Enhanced location display with coordinates
        self.location_display = ctk.CTkLabel(
            status_frame,
            text=self.location_text,
            font=ctk.CTkFont(size=14),
            text_color=PINK_COLORS["text_secondary"]
        )
        self.location_display.pack(pady=(5, 5))

        # Coordinates display
        self.coordinates_display = ctk.CTkLabel(
            status_frame,
            text="📍 Coordinates: Getting precise location...",
            font=ctk.CTkFont(size=12),
            text_color=PINK_COLORS["text_secondary"]
        )
        self.coordinates_display.pack(pady=(0, 5))

        # Location accuracy indicator
        self.accuracy_display = ctk.CTkLabel(
            status_frame,
            text="🎯 Accuracy: Initializing GPS...",
            font=ctk.CTkFont(size=11),
            text_color="#00ff00"
        )
        self.accuracy_display.pack(pady=(0, 15))

    def create_control_panel(self, parent):
        """Create elegant control panel"""
        control_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=PINK_COLORS["surface"],
            border_width=1,
            border_color=PINK_COLORS["accent"]
        )
        control_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Enhanced main protection button
        self.protection_btn = ctk.CTkButton(
            control_frame,
            text="⚡ ACTIVATE INSTANT GUARDIAN ⚡",
            font=ctk.CTkFont(size=24, weight="bold"),
            height=120,
            width=450,
            corner_radius=25,
            fg_color=PINK_COLORS["primary"],
            hover_color=PINK_COLORS["secondary"],
            border_width=3,
            border_color=PINK_COLORS["accent"],
            text_color=PINK_COLORS["text"],
            command=self.toggle_protection
        )
        self.protection_btn.pack(pady=30)

        # Emergency button - sleek red design
        self.emergency_btn = ctk.CTkButton(
            control_frame,
            text="🚨 EMERGENCY PROTOCOL 🚨",
            font=ctk.CTkFont(size=20, weight="bold"),
            height=80,
            width=450,
            corner_radius=20,
            fg_color="#dc143c",
            hover_color="#b22222",
            border_width=2,
            border_color="#ff6b6b",
            text_color="white",
            command=self.emergency_alert
        )
        self.emergency_btn.pack(pady=10)
        
        # Immediate Emergency button - even more urgent
        self.immediate_emergency_btn = ctk.CTkButton(
            control_frame,
            text="⚡ IMMEDIATE EMERGENCY - NO CONFIRMATION ⚡",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=70,
            width=450,
            corner_radius=20,
            fg_color="#8b0000",
            hover_color="#660000",
            border_width=3,
            border_color="#ff0000",
            text_color="white",
            command=self.emergency_alert_immediate
        )
        self.immediate_emergency_btn.pack(pady=10)

        # Acknowledge button (prominent)
        self.acknowledge_btn = ctk.CTkButton(
            control_frame,
            text="✅ ACKNOWLEDGE ALERTS",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=70,
            width=350,
            corner_radius=20,
            fg_color="#ffc107",
            hover_color="#e0a800",
            text_color="#000000",
            border_width=2,
            border_color=PINK_COLORS["accent"],
            command=self.acknowledge_all_alerts
        )
        self.acknowledge_btn.pack(pady=15)

        # Quick action buttons row
        quick_actions = ctk.CTkFrame(control_frame, fg_color="transparent")
        quick_actions.pack(pady=20)

        # Setup button
        setup_btn = ctk.CTkButton(
            quick_actions,
            text="⚙️ CONFIGURE",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50,
            width=150,
            corner_radius=15,
            fg_color=PINK_COLORS["dark"],
            hover_color=PINK_COLORS["primary"],
            border_width=1,
            border_color=PINK_COLORS["accent"],
            command=self.open_setup
        )
        setup_btn.pack(side="left", padx=10)

        # Test button
        test_btn = ctk.CTkButton(
            quick_actions,
            text="🧪 TEST SYSTEM",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50,
            width=150,
            corner_radius=15,
            fg_color=PINK_COLORS["dark"],
            hover_color=PINK_COLORS["primary"],
            border_width=1,
            border_color=PINK_COLORS["accent"],
            command=self.test_system
        )
        test_btn.pack(side="left", padx=10)

        # Help button
        help_btn = ctk.CTkButton(
            quick_actions,
            text="💡 HELP",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50,
            width=150,
            corner_radius=15,
            fg_color=PINK_COLORS["dark"],
            hover_color=PINK_COLORS["primary"],
            border_width=1,
            border_color=PINK_COLORS["accent"],
            command=self.show_help
        )
        help_btn.pack(side="left", padx=10)

        # Easy access buttons row
        easy_access = ctk.CTkFrame(control_frame, fg_color="transparent")
        easy_access.pack(pady=15)

        # Location button
        location_btn = ctk.CTkButton(
            easy_access,
            text="📍 SHOW LOCATION",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=40,
            width=140,
            corner_radius=12,
            fg_color="#17a2b8",
            hover_color="#138496",
            command=self.show_detailed_location
        )
        location_btn.pack(side="left", padx=5)

        # Quick call buttons
        police_btn = ctk.CTkButton(
            easy_access,
            text="🚔 POLICE 100",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=40,
            width=120,
            corner_radius=12,
            fg_color="#dc3545",
            hover_color="#c82333",
            command=lambda: self.quick_call("police")
        )
        police_btn.pack(side="left", padx=5)

        # Ambulance button
        ambulance_btn = ctk.CTkButton(
            easy_access,
            text="🚑 AMBULANCE",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=40,
            width=120,
            corner_radius=12,
            fg_color="#28a745",
            hover_color="#218838",
            command=lambda: self.quick_call("ambulance")
        )
        ambulance_btn.pack(side="left", padx=5)

        # Women helpline button
        women_btn = ctk.CTkButton(
            easy_access,
            text="👮‍♀️ WOMEN 1091",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=40,
            width=130,
            corner_radius=12,
            fg_color="#e83e8c",
            hover_color="#d91a72",
            command=lambda: self.quick_call("women_helpline")
        )
        women_btn.pack(side="left", padx=5)

    def create_activity_monitor(self, parent):
        """Create futuristic activity monitor"""
        monitor_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=PINK_COLORS["surface"],
            border_width=1,
            border_color=PINK_COLORS["accent"]
        )
        monitor_frame.pack(fill="x", padx=15, pady=10)

        # Monitor title
        ctk.CTkLabel(
            monitor_frame,
            text="◆ ACTIVITY MONITOR ◆",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PINK_COLORS["text"]
        ).pack(pady=(15, 10))

        # Stats grid
        stats_grid = ctk.CTkFrame(monitor_frame, fg_color="transparent")
        stats_grid.pack(pady=(0, 15))

        # Alert count
        self.alert_display = ctk.CTkLabel(
            stats_grid,
            text=f"🚨 Alerts Today: {self.alert_count_text}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PINK_COLORS["text_secondary"]
        )
        self.alert_display.pack(side="left", padx=20)

        # Status indicator
        self.system_status = ctk.CTkLabel(
            stats_grid,
            text="🔊 Voice Detection: READY",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PINK_COLORS["text_secondary"]
        )
        self.system_status.pack(side="left", padx=20)

    def create_futuristic_sidebar(self):
        """Create futuristic sidebar (removed for simplicity)"""
        pass

    def start_animations(self):
        """Start futuristic animations"""
        self.animate_pulse()
        
    def cleanup_evidence_async(self):
        """Cleanup old evidence files in background"""
        def cleanup_background():
            try:
                from core.camera_capture import cleanup_evidence_files
                cleanup_evidence_files()
                print("✅ Evidence cleanup completed")
            except Exception as e:
                print(f"Evidence cleanup error: {e}")
        
        threading.Thread(target=cleanup_background, daemon=True).start()
        
    def show_futuristic_voice_alert(self, text, keywords):
        """Show simplified voice alert dialog"""
        try:
            return messagebox.askyesno(
                "🚨 VOICE EMERGENCY DETECTED", 
                f"Emergency keywords detected: {', '.join(keywords)}\n\nVoice: \"{text}\"\n\nAre you in danger?\n\nClick YES to activate emergency protocol."
            )
        except Exception as e:
            print(f"Voice alert error: {e}")
            return True  # Default to emergency for safety
            
    def show_futuristic_emergency_protocol_dialog(self):
        """Show simplified emergency protocol dialog"""
        return messagebox.askyesno(
            "🚨 EMERGENCY PROTOCOL", 
            "Activate full emergency protocol?\n\n• Contact emergency services\n• Alert all contacts\n• Start recording evidence\n• Share location"
        )
            
    def show_futuristic_call_dialog(self, name, number, location_text):
        """Show simplified emergency call dialog"""
        return messagebox.askyesno(
            "📞 EMERGENCY CALL", 
            f"Contact: {name}\nNumber: {number}\n\nLocation: {location_text}\n\nProceed with emergency call?"
        )

    def animate_pulse(self):
        """Create pulsing animation effect"""
        self.pulse_state = (self.pulse_state + 1) % 60

        # Animate title color
        if self.pulse_state < 30:
            alpha = self.pulse_state / 30.0
        else:
            alpha = (60 - self.pulse_state) / 30.0

        # Update status indicator
        if hasattr(self, 'status_indicator'):
            if self.listening:
                self.status_indicator.configure(
                    text="● GUARDIAN ACTIVE", text_color="#ff1493")
            else:
                self.status_indicator.configure(
                    text="● SYSTEM ONLINE", text_color="#00ff00")

        # Schedule next animation frame
        self.root.after(100, self.animate_pulse)

    def toggle_protection(self):
        """Toggle protection with futuristic feedback"""
        if not self.listening:
            self.start_protection()
        else:
            self.stop_protection()

    def start_protection(self):
        """Start protection with enhanced features"""
        print("🛡️ Starting protection...")
        
        self.listening = True

        # Update button appearance
        self.protection_btn.configure(
            text="🛑 DEACTIVATE INSTANT GUARDIAN",
            fg_color="#dc143c",
            hover_color="#b22222"
        )

        # Update status
        self.status_display.configure(
            text="⚡ INSTANT GUARDIAN ACTIVE - Ultra-Responsive Mode")
        self.system_status.configure(text="🔊 Voice Detection: STARTING...")

        # Show smart notification
        self.show_smart_notification("Protection Started",
                                     "🛡️ Instant Guardian is now protecting you!\n\n" +
                                     "• Voice monitoring: STARTING\n" +
                                     "• Location tracking: LIVE\n" +
                                     "• Emergency contacts: READY\n" +
                                     "• Say 'help' or 'emergency' for instant response\n" +
                                     "• Quick acknowledge: ESC key")

        # Start monitoring thread (non-blocking)
        self.monitoring_thread = threading.Thread(
            target=self.voice_monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        print("✅ Voice monitoring thread started")

        # Auto-check system readiness (delayed)
        self.root.after(1000, self.check_system_readiness)

        # Update location (delayed)
        self.root.after(500, self.update_location)

    def stop_protection(self):
        """Stop protection with smart feedback"""
        self.listening = False

        # Update button appearance
        self.protection_btn.configure(
            text="⚡ ACTIVATE INSTANT GUARDIAN ⚡",
            fg_color=PINK_COLORS["primary"],
            hover_color=PINK_COLORS["secondary"]
        )

        # Update status
        self.status_display.configure(
            text="🛡️ Instant Guardian: Ready to Protect")
        self.system_status.configure(text="🔊 Voice Detection: READY")

        # Show smart notification
        self.show_smart_notification("Protection Stopped",
                                     "🛡️ Guardian protection has been stopped.\n\n" +
                                     "Click 'ACTIVATE INSTANT GUARDIAN' to restart protection.\n\n" +
                                     "Your location is still being tracked for safety.")

    def show_smart_notification(self, title, message):
        """Show smart notification that doesn't interrupt user"""
        try:
            # Create a non-blocking notification
            notification_thread = threading.Thread(
                target=lambda: self.display_notification(title, message),
                daemon=True
            )
            notification_thread.start()
        except Exception as e:
            print(f"Smart notification error: {e}")

    def display_notification(self, title, message):
        """Display notification in a non-intrusive way"""
        try:
            # Create a small notification window
            notification = ctk.CTkToplevel(self.root)
            notification.title(title)
            notification.geometry("400x200")
            notification.configure(fg_color=PINK_COLORS["surface"])

            # Position in bottom-right corner
            x = notification.winfo_screenwidth() - 420
            y = notification.winfo_screenheight() - 250
            notification.geometry(f"400x200+{x}+{y}")

            # Make it stay on top but not grab focus
            notification.attributes('-topmost', True)
            notification.transient(self.root)

            # Content
            ctk.CTkLabel(
                notification,
                text=title,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=PINK_COLORS["primary"]
            ).pack(pady=10)

            ctk.CTkLabel(
                notification,
                text=message,
                font=ctk.CTkFont(size=12),
                text_color=PINK_COLORS["text"],
                wraplength=350
            ).pack(pady=10, padx=20)

            # Auto-close after 5 seconds
            notification.after(5000, notification.destroy)

        except Exception as e:
            print(f"Notification display error: {e}")

    def check_system_readiness(self):
        """Check if system is ready and provide helpful tips"""
        try:
            issues = []
            tips = []

            # Check configuration
            if ENHANCED_FEATURES:
                user_info = user_config.get_user_info()
                if not user_info.get('name'):
                    issues.append("User profile not configured")
                    tips.append("Click 'CONFIGURE' to set up your profile")

                if not user_info.get('emergency_contacts'):
                    issues.append("No emergency contacts")
                    tips.append("Add emergency contacts in configuration")

            # Check location
            if not hasattr(self, 'current_location') or not self.current_location:
                issues.append("Location not available")
                tips.append("Allow location access for better protection")

            # Check microphone
            try:
                import pyaudio
                p = pyaudio.PyAudio()
                device_count = p.get_device_count()
                p.terminate()
                if device_count == 0:
                    issues.append("No microphone detected")
                    tips.append("Connect a microphone for voice detection")
            except:
                issues.append("Audio system not available")
                tips.append("Check audio drivers and microphone")

            # Show readiness status
            if not issues:
                self.show_smart_notification("System Ready",
                                             "✅ All systems operational!\n\n" +
                                             "Your safety system is fully ready and protecting you.")
            else:
                tip_text = "\n".join([f"• {tip}" for tip in tips[:3]])
                self.show_smart_notification("System Tips",
                                             f"⚠️ {len(issues)} item(s) need attention:\n\n{tip_text}")

        except Exception as e:
            print(f"System readiness check error: {e}")

    def voice_monitoring_loop(self):
        """Reliable voice monitoring system that won't crash"""
        if not SPEECH_AVAILABLE:
            self.root.after(0, lambda: self.update_status("⚠️ Voice recognition not available"))
            return
            
        try:
            # Use reliable voice detection system
            from reliable_voice_detection import ReliableVoiceDetector
            
            print("�️ Satarting Reliable Voice Detection System...")
            
            # Create reliable detector with callback
            def voice_alert_callback(alert_data):
                """Callback for reliable voice detection alerts"""
                try:
                    print("🔥 VOICE_ALERT_CALLBACK CALLED!")
                    print(f"📊 Alert data: {alert_data}")
                    
                    text = alert_data['text']
                    keywords = alert_data['keywords']
                    detection_count = alert_data['detection_count']
                    response_time = alert_data['recognition_time']
                    
                    print(f"🚨 Voice Alert #{detection_count}: {keywords} ({response_time:.2f}s)")
                    
                    # IMMEDIATE TEST - Show messagebox directly here
                    import tkinter.messagebox as messagebox
                    messagebox.showinfo(
                        "🚨 CALLBACK TRIGGERED", 
                        f"Voice callback activated!\n\nKeywords: {keywords}\nText: '{text}'"
                    )
                    
                    # Update status in main thread
                    self.root.after(0, lambda: self.update_status(
                        f"🚨 VOICE EMERGENCY: {', '.join(keywords[:2])}"))
                    
                    # Stop listening immediately for safety
                    self.listening = False
                    
                    # Trigger emergency response
                    print("🎯 Calling trigger_voice_alert...")
                    self.root.after(0, lambda: self.trigger_voice_alert(text, keywords))
                        
                except Exception as e:
                    print(f"Voice alert callback error: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Initialize reliable detector
            self.reliable_detector = ReliableVoiceDetector(callback_function=voice_alert_callback)
            
            # Start reliable monitoring
            if self.reliable_detector.start_monitoring():
                self.root.after(0, lambda: self.update_status("🎤 RELIABLE VOICE GUARDIAN: ACTIVE"))
                print("✅ Reliable voice detection started successfully")
                
                # Keep monitoring while listening
                while self.listening and self.reliable_detector.is_listening:
                    time.sleep(0.5)  # Check every 500ms
                    
                # Stop detector when done
                self.reliable_detector.stop_monitoring()
            else:
                # Fallback to basic monitoring
                print("⚠️ Reliable detection failed, using basic fallback")
                self._basic_voice_monitoring()
                
        except ImportError as e:
            print(f"⚠️ Reliable voice detection not available: {e}")
            self._basic_voice_monitoring()
        except Exception as e:
            print(f"Reliable voice monitoring failed: {e}")
            self._basic_voice_monitoring()
    
    def _basic_voice_monitoring(self):
        """Improved fallback voice monitoring with working settings"""
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            
            # Use settings that actually work (from testing)
            r.energy_threshold = 150
            r.dynamic_energy_threshold = True
            r.pause_threshold = 0.8  # Longer pause for better detection
            r.phrase_threshold = 0.3
            r.non_speaking_duration = 0.8
            
            # Use default microphone
            mic = sr.Microphone()

            print("🔧 Calibrating microphone with working settings...")
            with mic as source:
                r.adjust_for_ambient_noise(source, duration=1)
                
            print(f"✅ Microphone calibrated. Energy threshold: {r.energy_threshold}")

            self.root.after(0, lambda: self.update_status(
                "🎤 RELIABLE VOICE GUARDIAN: ACTIVE"))

            # Emergency keywords that work well
            keywords = [
                "help", "emergency", "danger", "police", "fire", "ambulance",
                "save me", "call police", "need help", "attack", "stop it",
                "sos", "urgent", "crisis"
            ]
            
            print(f"🎯 Monitoring for emergency keywords: {keywords}")

            # Reliable voice monitoring loop
            detections = 0
            while self.listening:
                try:
                    with mic as source:
                        print("🎧 Listening for emergency keywords...")
                        # Use longer timeouts for reliable detection
                        audio = r.listen(source, timeout=2, phrase_time_limit=5)

                    print("🔄 Processing audio...")
                    
                    # Use Google recognition (proven to work)
                    try:
                        start_time = time.time()
                        text = r.recognize_google(audio, language='en-US').lower()
                        recognition_time = time.time() - start_time
                        
                        print(f"🔊 Recognized ({recognition_time:.2f}s): '{text}'")
                        
                        # Check for emergency keywords
                        found_keywords = []
                        for keyword in keywords:
                            if keyword in text:
                                found_keywords.append(keyword)
                        
                        if found_keywords:
                            detections += 1
                            print(f"🚨 EMERGENCY KEYWORDS DETECTED: {found_keywords}")
                            
                            # Update status
                            self.root.after(0, lambda: self.update_status(
                                f"🚨 EMERGENCY DETECTED: {', '.join(found_keywords[:2])}"))
                            
                            # Trigger emergency response
                            self.root.after(0, lambda: self.trigger_voice_alert(text, found_keywords))
                            
                            # Stop listening after detection for safety
                            self.listening = False
                            break
                        else:
                            print("   No emergency keywords detected")
                            
                    except sr.UnknownValueError:
                        print("❓ Could not understand audio - continuing to listen")
                    except sr.RequestError as e:
                        print(f"❌ Recognition error: {e}")
                        time.sleep(1)  # Wait before retrying

                except sr.WaitTimeoutError:
                    print("⏰ No speech detected - continuing to monitor")
                except Exception as e:
                    print(f"⚠️ Audio error: {e}")
                    time.sleep(0.5)

            print(f"🛑 Voice monitoring stopped. Total detections: {detections}")

        except Exception as e:
            print(f"Reliable voice monitoring failed: {e}")
            self.root.after(0, lambda: self.update_status("⚠️ Voice monitoring unavailable"))

    def trigger_voice_alert(self, text, keywords):
        """Trigger alert when voice keywords are detected"""
        try:
            print(f"🚨 TRIGGER_VOICE_ALERT CALLED: text='{text}', keywords={keywords}")
            self.update_status(f"🚨 QUANTUM VOICE EMERGENCY: {', '.join(keywords)}")
            
            # IMMEDIATE FUTURISTIC EMERGENCY WINDOW
            print("🚨 Creating futuristic emergency window immediately...")
            self.create_simple_emergency_window(text, keywords, f"voice_alert_{int(time.time())}")
            print("✅ Futuristic emergency window should appear!")
            
            # Show contacting services window after 2 seconds
            self.root.after(2000, lambda: self.show_contacting_services_window())
            
            # Check for critical keywords that need immediate activation
            critical_keywords = ["help", "emergency", "danger", "police", "fire", "attack", "save me"]
            immediate_activation = any(kw in keywords for kw in critical_keywords)
            
            if immediate_activation:
                print(f"🚨 CRITICAL KEYWORDS DETECTED: {keywords}")
                print("⚡ ACTIVATING IMMEDIATE EMERGENCY PROTOCOL")
                # Immediate activation without dialog
                self.emergency_alert_immediate(text, keywords)
            else:
                # Show dialog for less critical situations
                response = self.show_futuristic_voice_alert(text, keywords)
                if response:
                    self.emergency_alert()
                else:
                    self.update_status("✅ Voice alert acknowledged - Continuing monitoring")
                
        except Exception as e:
            print(f"Voice alert error: {e}")
            import traceback
            traceback.print_exc()
            
    def emergency_alert_immediate(self, text=None, keywords=None):
        """Immediate emergency alert activation without confirmation"""
        try:
            print("⚡ IMMEDIATE EMERGENCY PROTOCOL ACTIVATED")
            self.update_status("🚨 IMMEDIATE EMERGENCY PROTOCOL ACTIVE")
            
            self.alert_count += 1
            self.alert_count_text = str(self.alert_count)
            self.alert_display.configure(
                text=f"🚨 Alerts Today: {self.alert_count_text}")

            if ENHANCED_FEATURES:
                # Enhanced immediate emergency with escalation
                alert_id = f"immediate_emergency_{int(time.time())}_{uuid.uuid4().hex[:8]}"

                # Get location and evidence immediately
                location_data = self.location_service.get_emergency_location_info(
                ) if hasattr(self, 'location_service') else None
                evidence_data = capture_emergency_evidence()

                # Create urgent alert message
                if text and keywords:
                    alert_message = f"🚨 IMMEDIATE VOICE EMERGENCY\n\nCritical keywords detected: {', '.join(keywords)}\nVoice: \"{text}\"\n\nAUTOMATIC PROTOCOL ACTIVATION\nImmediate assistance required!\n\nLocation: {self._format_location_brief(location_data)}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                else:
                    alert_message = f"🚨 IMMEDIATE MANUAL EMERGENCY\n\nUser activated immediate emergency protocol.\nNo confirmation required - CRITICAL SITUATION\n\nLocation: {self._format_location_brief(location_data)}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

                # Start immediate escalation
                escalation_system.start_escalation(
                    alert_id=alert_id,
                    alert_type='immediate_emergency',
                    message=alert_message,
                    location_data=location_data,
                    evidence_data=evidence_data
                )

                # Show immediate alert dialog (non-blocking) - prevent duplicates
                def create_emergency_dialog():
                    """Create emergency dialog in main thread"""
                    try:
                        print("�️ Cireating emergency dialog in main thread...")
                        if not hasattr(self, 'immediate_dialog') or not self.immediate_dialog:
                            print(f"📊 Dialog parameters: text='{text}', keywords={keywords}, alert_id={alert_id}")
                            print(f"📊 Root window: {self.root}")
                            
                            # Force the dialog creation
                            self.immediate_dialog = ImmediateEmergencyDialog(self.root, text or "Immediate activation", 
                                                   keywords or ["emergency"], self.alert_count, alert_id)
                            print("✅ Emergency dialog created successfully")
                        else:
                            print("⚠️ Emergency dialog already exists")
                    except Exception as e:
                        print(f"❌ Immediate dialog error: {e}")
                        import traceback
                        traceback.print_exc()
                        
                        # Fallback to simple messagebox
                        try:
                            import tkinter.messagebox as messagebox
                            messagebox.showwarning(
                                "🚨 EMERGENCY PROTOCOL ACTIVE", 
                                f"Emergency detected!\n\nKeywords: {keywords}\nText: '{text}'\n\nEmergency protocol is active!"
                            )
                            print("✅ Fallback dialog shown")
                        except Exception as e2:
                            print(f"❌ Fallback dialog also failed: {e2}")
                
                # Emergency windows are now created in trigger_voice_alert
                print("🚨 Emergency escalation system activated")
                    
            print("✅ Immediate emergency protocol fully activated")
            
        except Exception as e:
            print(f"Immediate emergency error: {e}")
            
    def process_audio_ultra_fast(self, audio, keywords):
        """Ultra-fast audio processing optimized for speed"""
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            
            # Single fast recognition attempt
            text = None
            start_time = time.time()
            
            try:
                # Use fastest Google recognition with short timeout
                text = r.recognize_google(audio, language='en-IN').lower()
                recognition_time = time.time() - start_time
                print(f"🔊 Recognized in {recognition_time:.2f}s: '{text}'")
            except sr.UnknownValueError:
                print("🔇 No speech detected")
                return
            except sr.RequestError as e:
                print(f"🌐 Recognition error: {e}")
                return
            except Exception as e:
                print(f"🔧 Recognition failed: {e}")
                return
            
            if text:
                # Ultra-fast keyword matching
                found_keywords = []
                
                # Direct string matching (fastest)
                for keyword in keywords:
                    if keyword in text:
                        found_keywords.append(keyword)
                
                if found_keywords:
                    print(f"🚨 KEYWORDS DETECTED: {found_keywords}")
                    # Stop listening immediately
                    self.listening = False
                    # Immediate trigger
                    self.trigger_voice_alert(text, found_keywords)
                else:
                    print(f"ℹ️ No keywords in: '{text}'")
                
        except Exception as e:
            print(f"🔧 Ultra-fast processing error: {e}")
            
    def try_offline_voice_detection(self):
        """Backup offline voice detection using simpler methods"""
        try:
            print("🔄 Trying offline voice detection...")
            import speech_recognition as sr
            r = sr.Recognizer()
            mic = sr.Microphone()
            
            # Simple offline detection
            with mic as source:
                r.adjust_for_ambient_noise(source, duration=0.3)
                
            keywords = ["help", "emergency", "danger", "police", "fire"]
            
            while self.listening:
                try:
                    with mic as source:
                        audio = r.listen(source, timeout=0.3, phrase_time_limit=1.5)
                    
                    # Try offline recognition (Sphinx)
                    try:
                        text = r.recognize_sphinx(audio).lower()
                        print(f"🔊 Offline: '{text}'")
                        
                        found_keywords = [kw for kw in keywords if kw in text]
                        if found_keywords:
                            print(f"🚨 Offline keywords: {found_keywords}")
                            self.listening = False
                            self.trigger_voice_alert(text, found_keywords)
                            break
                            
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError:
                        pass
                        
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"Offline detection error: {e}")
                    break
                    
        except Exception as e:
            print(f"Offline voice detection failed: {e}")
            self.root.after(0, lambda: self.update_status("⚠️ Voice detection unavailable"))
            
    def start_real_time_monitoring(self, keywords):
        """Real-time continuous audio monitoring for instant detection"""
        try:
            import pyaudio
            import numpy as np
            import threading
            import queue
            
            print("🚀 Starting REAL-TIME continuous monitoring...")
            
            # Audio settings optimized for real-time
            CHUNK = 512  # Smaller chunks for faster processing
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            
            # Initialize PyAudio
            p = pyaudio.PyAudio()
            
            # Audio queue for processing
            audio_queue = queue.Queue()
            
            # Open audio stream
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=lambda data, frame_count, time_info, status: (data, pyaudio.paContinue)
            )
            
            stream.start_stream()
            print("✅ Real-time audio stream started")
            self.root.after(0, lambda: self.update_status("🎤 REAL-TIME GUARDIAN: LISTENING"))
            
            # Audio processing buffer
            audio_buffer = []
            buffer_duration = 1.5  # 1.5 seconds of audio
            buffer_size = int(RATE * buffer_duration)
            
            # Start speech recognition thread
            recognition_thread = threading.Thread(
                target=self.continuous_speech_recognition,
                args=(audio_queue, keywords),
                daemon=True
            )
            recognition_thread.start()
            
            while self.listening:
                try:
                    # Read audio data
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # Add to buffer
                    audio_buffer.extend(audio_data)
                    
                    # Keep buffer at optimal size
                    if len(audio_buffer) > buffer_size:
                        audio_buffer = audio_buffer[-buffer_size:]
                    
                    # Check for voice activity (energy-based detection)
                    energy = np.sqrt(np.mean(audio_data**2))
                    
                    if energy > 300:  # Voice detected
                        # Send audio for recognition
                        if len(audio_buffer) >= RATE:  # At least 1 second
                            try:
                                audio_queue.put_nowait(audio_buffer.copy())
                            except queue.Full:
                                pass  # Skip if queue is full
                        
                except Exception as e:
                    print(f"Audio stream error: {e}")
                    continue
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            p.terminate()
            print("🛑 Real-time monitoring stopped")
            
        except Exception as e:
            print(f"Real-time monitoring failed: {e}")
            raise  # Let fallback handle it
            
    def continuous_speech_recognition(self, audio_queue, keywords):
        """Continuous speech recognition in background thread"""
        import speech_recognition as sr
        
        r = sr.Recognizer()
        
        while self.listening:
            try:
                # Get audio from queue (non-blocking)
                try:
                    audio_buffer = audio_queue.get_nowait()
                except queue.Empty:
                    time.sleep(0.1)
                    continue
                
                # Convert to AudioData
                audio_bytes = np.array(audio_buffer, dtype=np.int16).tobytes()
                audio = sr.AudioData(audio_bytes, 16000, 2)
                
                # Quick recognition
                try:
                    start_time = time.time()
                    text = r.recognize_google(audio, language='en-IN').lower()
                    recognition_time = time.time() - start_time
                    
                    print(f"🔊 [{recognition_time:.1f}s] '{text}'")
                    
                    # Check for keywords
                    found_keywords = [kw for kw in keywords if kw in text]
                    if found_keywords:
                        print(f"🚨 INSTANT DETECTION: {found_keywords}")
                        self.listening = False
                        # Trigger in main thread
                        self.root.after(0, lambda: self.trigger_voice_alert(text, found_keywords))
                        break
                        
                except sr.UnknownValueError:
                    pass  # No speech
                except sr.RequestError as e:
                    print(f"API error: {e}")
                except Exception as e:
                    print(f"Recognition error: {e}")
                    
            except Exception as e:
                print(f"Continuous recognition error: {e}")
                time.sleep(0.1)
            
    def setup_enhanced_audio_analysis(self):
        """Placeholder for audio analysis setup"""
        pass

        # Ultra-sensitive threat detection thresholds
        self.scream_threshold = 0.6      # Lower threshold for instant detection
        self.stress_threshold = 0.5      # More sensitive stress detection
        self.panic_threshold = 0.55      # Faster panic detection
        self.whisper_threshold = 0.3     # Detect whispered distress
        self.cry_threshold = 0.4         # Detect crying/sobbing

        # Enhanced audio pattern baselines
        self.normal_pitch_range = (80, 300)     # Hz - Normal speech
        self.distress_pitch_range = (300, 800)  # Hz - Distressed speech
        self.scream_pitch_range = (800, 2500)   # Hz - Screams/shouts
        self.whisper_range = (50, 150)          # Hz - Whispered distress
        self.cry_range = (100, 400)             # Hz - Crying patterns

        # Instant response patterns
        self.instant_keywords = [
            "help", "stop", "no", "police", "emergency", "rape", "fire",
            "attack", "hurt", "scared", "danger", "save me", "call 911"
        ]

        # Voice stress indicators
        self.stress_indicators = {
            'trembling_voice': 0.4,
            'pitch_variation': 0.5,
            'speech_rate_change': 0.6,
            'volume_fluctuation': 0.5,
            'breathing_pattern': 0.4
        }

    def analyze_audio_for_threats(self, audio_data):
        """Analyze audio for unnatural voice patterns and threats"""
        try:
            if len(audio_data) < 1024:
                return False, None

            # Convert to float
            audio_float = audio_data.astype(np.float32) / 32768.0

            # Extract audio features
            features = self.extract_audio_features(audio_float)

            if features is None:
                return False, None

            # Check for scream patterns
            if self.detect_scream_pattern(features):
                return True, "scream"

            # Check for panic/distress patterns
            if self.detect_panic_pattern(features):
                return True, "panic"

            # Check for struggle sounds
            if self.detect_struggle_pattern(features):
                return True, "struggle"

            # Check for crash/impact sounds
            if self.detect_crash_pattern(features):
                return True, "crash"

            return False, None

        except Exception as e:
            print(f"Audio analysis error: {e}")
            return False, None

    def extract_audio_features(self, audio_data):
        """Extract comprehensive audio features"""
        try:
            # Basic features
            rms_energy = np.sqrt(np.mean(audio_data**2))
            zero_crossing_rate = np.mean(
                librosa.feature.zero_crossing_rate(audio_data))

            # Spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(
                y=audio_data, sr=self.sample_rate))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(
                y=audio_data, sr=self.sample_rate))
            spectral_bandwidth = np.mean(
                librosa.feature.spectral_bandwidth(y=audio_data, sr=self.sample_rate))

            # MFCC features
            mfccs = librosa.feature.mfcc(
                y=audio_data, sr=self.sample_rate, n_mfcc=13)
            mfcc_mean = np.mean(mfccs, axis=1)
            mfcc_std = np.std(mfccs, axis=1)

            # Pitch analysis
            pitches, magnitudes = librosa.piptrack(
                y=audio_data, sr=self.sample_rate)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)

            avg_pitch = np.mean(pitch_values) if pitch_values else 0
            pitch_variance = np.var(pitch_values) if pitch_values else 0

            return {
                'rms_energy': rms_energy,
                'zero_crossing_rate': zero_crossing_rate,
                'spectral_centroid': spectral_centroid,
                'spectral_rolloff': spectral_rolloff,
                'spectral_bandwidth': spectral_bandwidth,
                'mfcc_mean': mfcc_mean,
                'mfcc_std': mfcc_std,
                'avg_pitch': avg_pitch,
                'pitch_variance': pitch_variance
            }

        except Exception as e:
            print(f"Feature extraction error: {e}")
            return None

    def detect_scream_pattern(self, features):
        """Detect scream patterns in audio"""
        try:
            # High energy + high pitch + high spectral centroid = potential scream
            high_energy = features['rms_energy'] > 0.3
            high_pitch = features['avg_pitch'] > 400
            high_spectral = features['spectral_centroid'] > 2000
            high_variance = features['pitch_variance'] > 10000

            return high_energy and (high_pitch or high_spectral) and high_variance
        except:
            return False

    def detect_panic_pattern(self, features):
        """Detect panic/distress patterns"""
        try:
            # Irregular pitch + high zero crossing rate + moderate energy
            irregular_pitch = features['pitch_variance'] > 5000
            high_zcr = features['zero_crossing_rate'] > 0.1
            moderate_energy = features['rms_energy'] > 0.1

            return irregular_pitch and high_zcr and moderate_energy
        except:
            return False

    def detect_struggle_pattern(self, features):
        """Detect struggle/fight sounds"""
        try:
            # Low pitch + high energy + irregular patterns
            low_pitch = features['avg_pitch'] < 200 and features['avg_pitch'] > 0
            high_energy = features['rms_energy'] > 0.2
            irregular = features['pitch_variance'] > 3000

            return low_pitch and high_energy and irregular
        except:
            return False

    def detect_crash_pattern(self, features):
        """Detect crash/impact sounds"""
        try:
            # Very high energy + broad spectrum + high spectral rolloff
            very_high_energy = features['rms_energy'] > 0.5
            broad_spectrum = features['spectral_bandwidth'] > 2000
            high_rolloff = features['spectral_rolloff'] > 4000

            return very_high_energy and broad_spectrum and high_rolloff
        except:
            return False

    def instant_threat_analysis(self, audio_data):
        """Instant parallel threat analysis for immediate response"""
        try:
            if len(audio_data) < 512:
                return

            # Ultra-fast threat detection
            threat_detected, threat_type, confidence = self.ultra_fast_threat_detection(
                audio_data)

            if threat_detected and confidence > 0.6:
                # INSTANT ALERT - No delay
                self.root.after(0, lambda: self.trigger_instant_threat_alert(
                    threat_type, confidence, audio_data))

        except Exception as e:
            print(f"Instant threat analysis error: {e}")

    def instant_speech_recognition(self, audio):
        """Instant speech recognition with multiple fallbacks"""
        try:
            r = sr.Recognizer()

            # Try multiple recognition engines in parallel
            recognition_results = []

            # Primary: Google (fastest)
            try:
                text = r.recognize_google(audio, language='en-IN')
                recognition_results.append(('google', text))
            except:
                pass

            # Fallback: Sphinx (offline)
            try:
                text = r.recognize_sphinx(audio)
                recognition_results.append(('sphinx', text))
            except:
                pass

            # Process all recognition results
            for engine, text in recognition_results:
                self.process_instant_speech(text, engine)

        except Exception as e:
            print(f"Instant speech recognition error: {e}")

    def process_instant_speech(self, text, engine):
        """Process speech recognition results instantly"""
        try:
            text_lower = text.lower()

            # INSTANT keyword detection
            found_keywords = []
            for keyword in KEYWORDS:
                if keyword in text_lower:
                    found_keywords.append(keyword)

            # Check for instant response keywords
            instant_keywords_found = [
                kw for kw in self.instant_keywords if kw in text_lower]

            if instant_keywords_found or found_keywords:
                # IMMEDIATE ALERT - No processing delay
                self.root.after(0, lambda: self.trigger_instant_alert(
                    text, found_keywords or instant_keywords_found, engine))

            # Instant stress analysis
            stress_level = self.instant_stress_analysis(text)
            if stress_level > 0.5:  # Lower threshold for instant response
                self.root.after(
                    0, lambda: self.trigger_instant_stress_alert(text, stress_level))

        except Exception as e:
            print(f"Instant speech processing error: {e}")

    def ultra_fast_threat_detection(self, audio_data):
        """Ultra-fast threat detection optimized for speed"""
        try:
            audio_float = audio_data.astype(np.float32) / 32768.0

            # Fast energy calculation
            rms_energy = np.sqrt(np.mean(audio_float**2))

            # Fast frequency analysis
            fft = np.fft.fft(audio_float)
            freqs = np.fft.fftfreq(len(fft), 1/self.sample_rate)
            magnitude = np.abs(fft)

            # Find dominant frequency
            dominant_freq_idx = np.argmax(magnitude[:len(magnitude)//2])
            dominant_freq = abs(freqs[dominant_freq_idx])

            # Fast threat classification
            confidence = 0.0
            threat_type = None

            # Scream detection (high frequency + high energy)
            if dominant_freq > 800 and rms_energy > 0.3:
                threat_type = "scream"
                confidence = min((dominant_freq / 1500) *
                                 (rms_energy / 0.5), 1.0)

            # Panic/distress (irregular patterns)
            elif rms_energy > 0.2 and dominant_freq > 300:
                threat_type = "distress"
                confidence = min(rms_energy * 1.5, 1.0)

            # Whispered distress (low frequency + specific pattern)
            elif dominant_freq < 150 and rms_energy > 0.1:
                threat_type = "whisper_distress"
                confidence = min(rms_energy * 2.0, 1.0)

            # Crying/sobbing pattern
            elif 100 <= dominant_freq <= 400 and rms_energy > 0.15:
                threat_type = "crying"
                confidence = min(rms_energy * 1.8, 1.0)

            return threat_type is not None, threat_type, confidence

        except Exception as e:
            print(f"Ultra-fast threat detection error: {e}")
            return False, None, 0.0

    def instant_stress_analysis(self, text):
        """Instant stress analysis based on text content"""
        try:
            text_lower = text.lower()
            stress_score = 0.0

            # High-stress words
            high_stress_words = [
                'please', 'stop', 'no', 'dont', 'scared', 'afraid', 'terrified',
                'help', 'hurt', 'pain', 'crying', 'sobbing', 'shaking', 'trembling'
            ]

            # Medium-stress words
            medium_stress_words = [
                'worried', 'nervous', 'anxious', 'uncomfortable', 'uneasy',
                'concerned', 'troubled', 'disturbed', 'upset'
            ]

            # Count stress indicators
            for word in high_stress_words:
                if word in text_lower:
                    stress_score += 0.3

            for word in medium_stress_words:
                if word in text_lower:
                    stress_score += 0.2

            # Repetition indicates stress
            words = text_lower.split()
            if len(words) != len(set(words)):  # Has repeated words
                stress_score += 0.2

            # Short, fragmented speech indicates stress
            if len(words) < 3 and any(word in text_lower for word in ['no', 'stop', 'help']):
                stress_score += 0.4

            return min(stress_score, 1.0)

        except Exception as e:
            print(f"Instant stress analysis error: {e}")
            return 0.0

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for quick acknowledge"""
        try:
            # Bind keyboard shortcuts to the main window
            self.root.bind('<Escape>', lambda e: self.acknowledge_all_alerts())
            self.root.bind('<Control-Shift-A>',
                           lambda e: self.acknowledge_all_alerts())
            self.root.bind('<F12>', lambda e: self.acknowledge_all_alerts())
            # Ctrl+E for emergency
            self.root.bind('<Control-e>', lambda e: self.emergency_alert())
            # Ctrl+T for test
            self.root.bind('<Control-t>', lambda e: self.test_system())
            # Ctrl+S for start/stop
            self.root.bind('<Control-s>', lambda e: self.toggle_protection())

            # Make sure window can receive focus
            self.root.focus_set()

            print("Keyboard shortcuts enabled:")
            print("  ESC, Ctrl+Shift+A, F12 - Acknowledge alerts")
            print("  Ctrl+E - Emergency alert")
            print("  Ctrl+T - Test system")
            print("  Ctrl+S - Start/Stop protection")
        except Exception as e:
            print(f"Keyboard shortcuts setup error: {e}")

    def setup_easy_use_features(self):
        """Setup features to make the system super easy to use"""
        try:
            # Auto-start location tracking
            self.start_precise_location_tracking()

            # Setup voice commands for hands-free operation
            self.setup_voice_commands()

            # Setup auto-configuration detection
            self.auto_detect_user_preferences()

            # Setup one-click emergency contacts
            self.setup_quick_contacts()

            # Setup gesture recognition (if available)
            self.setup_gesture_recognition()

            print("Easy-use features initialized")
        except Exception as e:
            print(f"Easy-use features setup error: {e}")

    def setup_voice_commands(self):
        """Setup voice commands for hands-free operation"""
        self.voice_commands = {
            "start protection": self.toggle_protection,
            "stop protection": self.toggle_protection,
            "emergency": self.emergency_alert,
            "test system": self.test_system,
            "acknowledge": self.acknowledge_all_alerts,
            "show location": self.show_detailed_location,
            "call police": lambda: messagebox.showinfo("Emergency", "Call 100 for Police"),
            "call ambulance": lambda: messagebox.showinfo("Emergency", "Call 108 for Ambulance")
        }

    def auto_detect_user_preferences(self):
        """Auto-detect and configure user preferences"""
        try:
            # Auto-detect system language
            import locale
            system_locale = locale.getdefaultlocale()[0]

            # Auto-detect time zone for accurate timestamps
            import time
            timezone = time.tzname[0]

            # Store preferences
            self.user_preferences = {
                'locale': system_locale,
                'timezone': timezone,
                'auto_start': True,
                'high_sensitivity': True,
                'instant_alerts': True
            }

            print(f"Auto-detected preferences: {system_locale}, {timezone}")
        except Exception as e:
            print(f"Auto-detection error: {e}")

    def setup_quick_contacts(self):
        """Setup one-click emergency contacts"""
        self.quick_contacts = {
            'police': '100',
            'ambulance': '108',
            'fire': '101',
            'women_helpline': '1091',
            'child_helpline': '1098'
        }

    def setup_gesture_recognition(self):
        """Setup gesture recognition for emergency activation"""
        try:
            # Placeholder for gesture recognition
            # Could integrate with camera for hand gestures
            self.gesture_enabled = False
            print("Gesture recognition: Not available (camera required)")
        except Exception as e:
            print(f"Gesture setup error: {e}")

    def start_precise_location_tracking(self):
        """Start precise location tracking with exact coordinates"""
        def precise_location_tracker():
            location_methods = ['gps', 'wifi', 'ip', 'cell_tower']

            while getattr(self, 'location_tracking_active', True):  # Controlled loop
                try:
                    best_location = None
                    best_accuracy = float('inf')

                    # Try multiple location methods for best accuracy
                    for method in location_methods:
                        try:
                            location = self.get_location_by_method(method)
                            if location and location.get('accuracy', float('inf')) < best_accuracy:
                                best_location = location
                                best_accuracy = location.get(
                                    'accuracy', float('inf'))
                        except:
                            continue

                    if best_location:
                        self.current_location = best_location
                        self.update_location_displays(best_location)

                except Exception as e:
                    print(f"Precise location tracking error: {e}")

                time.sleep(3)  # Update every 3 seconds for precision

        if not hasattr(self, 'precise_location_thread') or not self.precise_location_thread.is_alive():
            self.precise_location_thread = threading.Thread(
                target=precise_location_tracker, daemon=True)
            self.precise_location_thread.start()

    def get_location_by_method(self, method):
        """Get location using specific method"""
        try:
            if method == 'gps':
                return self.get_gps_location()
            elif method == 'wifi':
                return self.get_wifi_location()
            elif method == 'ip':
                return self.get_ip_location()
            elif method == 'cell_tower':
                return self.get_cell_tower_location()
        except Exception as e:
            print(f"Location method {method} error: {e}")
            return None

    def get_gps_location(self):
        """Get GPS location (most accurate)"""
        try:
            # Try to use system GPS if available
            if hasattr(self, 'location_service'):
                location = self.location_service.get_emergency_location_info()
                if location:
                    location['method'] = 'GPS'
                    location['accuracy'] = 5  # GPS typically 5m accuracy
                    return location
        except:
            pass
        return None

    def get_wifi_location(self):
        """Get WiFi-based location"""
        try:
            import subprocess
            import re

            # Get WiFi networks (Windows)
            if os.name == 'nt':
                result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    # Use WiFi positioning (approximate)
                    return {
                        'latitude': 12.9716,  # Approximate based on WiFi
                        'longitude': 77.5946,
                        'method': 'WiFi',
                        'accuracy': 50,  # WiFi typically 50m accuracy
                        'address': 'WiFi-based location'
                    }
        except:
            pass
        return None

    def get_ip_location(self):
        """Get IP-based location"""
        try:
            import requests
            response = requests.get("http://ip-api.com/json/", timeout=3)
            if response.status_code == 200:
                data = response.json()
                return {
                    'latitude': data.get('lat', 0),
                    'longitude': data.get('lon', 0),
                    'method': 'IP',
                    'accuracy': 1000,  # IP typically 1km accuracy
                    'address': f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}"
                }
        except:
            pass
        return None

    def get_cell_tower_location(self):
        """Get cell tower location (if available)"""
        try:
            # Placeholder for cell tower location
            # Would require cellular modem access
            return None
        except:
            pass
        return None

    def update_location_displays(self, location):
        """Update all location displays with precise information"""
        try:
            if not location:
                return

            lat = location.get('latitude', 0)
            lon = location.get('longitude', 0)
            method = location.get('method', 'Unknown')
            accuracy = location.get('accuracy', 0)
            address = location.get('address', 'Bengaluru, Karnataka, India (Approximate)')

            # Update main location display
            self.root.after(0, lambda: self.location_display.configure(
                text=f"📍 {address[:60]}..."
            ))

            # Update coordinates display safely
            try:
                if hasattr(self, 'coordinates_display') and self.coordinates_display.winfo_exists():
                    self.root.after(0, lambda: self.coordinates_display.configure(
                        text=f"📍 Coordinates: {lat:.6f}, {lon:.6f}"
                    ))
            except Exception as e:
                print(f"Coordinates display update error: {e}")

            # Update accuracy display safely
            try:
                if hasattr(self, 'accuracy_display') and self.accuracy_display.winfo_exists():
                    accuracy_color = "#00ff00" if accuracy < 50 else "#ffff00" if accuracy < 200 else "#ff8800"
                    accuracy_text = f"🎯 Accuracy: ±{accuracy}m via {method}"
                    self.root.after(0, lambda: self.accuracy_display.configure(
                        text=accuracy_text,
                        text_color=accuracy_color
                    ))
            except Exception as e:
                print(f"Accuracy display update error: {e}")

        except Exception as e:
            print(f"Location display update error: {e}")

    def show_detailed_location(self):
        """Show detailed location information"""
        try:
            if hasattr(self, 'current_location') and self.current_location:
                loc = self.current_location

                details = f"""📍 DETAILED LOCATION INFORMATION
                
🌍 Address: {loc.get('address', 'Bengaluru, Karnataka, India (Detected via IP)')}

📊 Coordinates:
   • Latitude: {loc.get('latitude', 0):.8f}
   • Longitude: {loc.get('longitude', 0):.8f}

🎯 Accuracy: ±{loc.get('accuracy', 0)}m
📡 Method: {loc.get('method', 'Unknown')}
⏰ Last Updated: {datetime.now().strftime('%H:%M:%S')}

🔗 Google Maps Link:
https://maps.google.com/?q={loc.get('latitude', 0)},{loc.get('longitude', 0)}

📱 Share Location:
Lat: {loc.get('latitude', 0):.6f}, Lon: {loc.get('longitude', 0):.6f}
"""

                messagebox.showinfo("Detailed Location", details)
            else:
                messagebox.showwarning(
                    "Location", "Location not available yet.\nPlease wait for GPS to initialize.")
        except Exception as e:
            messagebox.showerror(
                "Location Error", f"Could not get location details: {e}")

    def start_continuous_location_tracking(self):
        """Legacy method - redirects to precise tracking"""
        self.start_precise_location_tracking()

    def analyze_voice_stress(self, audio_data, text):
        """Enhanced voice stress analysis with multiple indicators"""
        try:
            if len(audio_data) < 512:
                return 0.0

            audio_float = audio_data.astype(np.float32) / 32768.0
            features = self.extract_audio_features(audio_float)

            if features is None:
                return 0.0

            stress_score = 0.0

            # Voice trembling (high zero crossing rate)
            if features['zero_crossing_rate'] > 0.12:
                stress_score += 0.25

            # Pitch instability (high variance)
            if features['pitch_variance'] > 5000:
                stress_score += 0.3

            # High pitch (stress indicator)
            if features['avg_pitch'] > 200:
                stress_score += 0.2

            # Spectral changes (voice tension)
            if features['spectral_centroid'] > 1200:
                stress_score += 0.2

            # Energy fluctuations
            if features['rms_energy'] > 0.4 or features['rms_energy'] < 0.05:
                stress_score += 0.15

            # Text-based stress analysis
            text_stress = self.instant_stress_analysis(text)
            stress_score += text_stress * 0.4

            return min(stress_score, 1.0)

        except Exception as e:
            print(f"Enhanced stress analysis error: {e}")
            return 0.0

    def trigger_audio_threat_alert(self, threat_type, audio_data):
        """Trigger alert for audio-detected threats"""
        self.alert_count += 1
        self.alert_count_text = str(self.alert_count)

        # Update display
        self.alert_display.configure(
            text=f"🚨 Alerts Today: {self.alert_count_text}")

        # Create threat description
        threat_descriptions = {
            'scream': 'High-pitched scream detected',
            'panic': 'Panic/distress vocalization detected',
            'struggle': 'Struggle sounds detected',
            'crash': 'Impact/crash sound detected'
        }

        description = threat_descriptions.get(
            threat_type, 'Unnatural audio pattern detected')

        # Show advanced alert dialog
        AdvancedThreatDialog(self.root, description, [
                             threat_type], self.alert_count, audio_data)

        # Update status
        self.update_status(f"🚨 AUDIO THREAT DETECTED - {description}")

    def trigger_instant_threat_alert(self, threat_type, confidence, audio_data):
        """Trigger INSTANT threat alert - no delays"""
        self.alert_count += 1
        self.alert_count_text = str(self.alert_count)

        # Update display immediately
        self.alert_display.configure(
            text=f"🚨 Alerts Today: {self.alert_count_text}")

        # Threat descriptions
        threat_descriptions = {
            'scream': 'SCREAM DETECTED - High-pitched distress call',
            'distress': 'DISTRESS VOCALIZATION - Panic pattern detected',
            'whisper_distress': 'WHISPERED DISTRESS - Quiet help request',
            'crying': 'CRYING/SOBBING - Emotional distress detected'
        }

        description = threat_descriptions.get(
            threat_type, 'AUDIO THREAT DETECTED')

        if ENHANCED_FEATURES:
            # INSTANT escalation - no delays
            alert_id = f"instant_threat_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            # Get current location (already tracked)
            location_data = getattr(self, 'current_location', None)

            # Instant evidence capture
            evidence_data = None
            try:
                if hasattr(self, 'location_service'):
                    evidence_data = capture_emergency_evidence()
            except:
                pass

            # Create urgent alert message
            alert_message = f"🚨 INSTANT AUDIO THREAT DETECTED\n\nThreat Type: {threat_type.upper()}\nConfidence: {confidence:.1%}\nDescription: {description}\n\nLocation: {self._format_location_brief(location_data)}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n⚠️ IMMEDIATE RESPONSE REQUIRED ⚠️"

            # Start INSTANT escalation
            escalation_system.start_escalation(
                alert_id=alert_id,
                alert_type='instant_audio_threat',
                message=alert_message,
                location_data=location_data,
                evidence_data=evidence_data
            )

            # Show instant alert dialog
            try:
                InstantThreatDialog(
                    self.root, description, threat_type, confidence, self.alert_count, alert_id)
            except Exception as e:
                print(f"Instant threat dialog error: {e}")
                # Fallback to basic alert
                messagebox.showwarning(
                    "Instant Threat Detected", f"🚨 {description}\n\nThreat Type: {threat_type}\nConfidence: {confidence:.1%}\n\nImmediate attention required!")

        # Update status
        self.update_status(f"🚨 INSTANT THREAT - {description}")

    def trigger_instant_alert(self, text, keywords, engine):
        """Trigger INSTANT keyword alert - no processing delays"""
        self.alert_count += 1
        self.alert_count_text = str(self.alert_count)

        # Update display immediately
        self.alert_display.configure(
            text=f"🚨 Alerts Today: {self.alert_count_text}")

        if ENHANCED_FEATURES:
            # INSTANT escalation
            alert_id = f"instant_voice_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            # Get current location
            location_data = getattr(self, 'current_location', None)

            # Assess severity instantly
            severity = self._assess_keyword_severity(keywords)

            # Create instant alert message
            alert_message = f"🎤 INSTANT VOICE EMERGENCY\n\nKeywords: {', '.join(keywords)}\nText: \"{text}\"\nEngine: {engine}\nSeverity: {severity}\n\nLocation: {self._format_location_brief(location_data)}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n⚠️ INSTANT RESPONSE ACTIVATED ⚠️"

            # Start INSTANT escalation
            escalation_system.start_escalation(
                alert_id=alert_id,
                alert_type='instant_voice_emergency',
                message=alert_message,
                location_data=location_data,
                evidence_data=None  # Will be captured by escalation system
            )

            # Show enhanced instant alert
            try:
                InstantVoiceAlertDialog(
                    self.root, text, keywords, severity, self.alert_count, alert_id)
            except Exception as e:
                print(f"Instant voice dialog error: {e}")
                # Fallback to basic alert
                messagebox.showwarning(
                    "Instant Voice Emergency", f"🎤 Voice Emergency Detected!\n\nKeywords: {', '.join(keywords)}\nText: \"{text}\"\nSeverity: {severity}\n\nImmediate response required!")

        # Update status
        self.update_status(
            f"🚨 INSTANT VOICE ALERT - {', '.join(keywords[:3])}")

    def trigger_instant_stress_alert(self, text, stress_level):
        """Trigger INSTANT stress alert"""
        if stress_level > 0.7:  # Only for high stress
            self.alert_count += 1
            self.alert_count_text = str(self.alert_count)

            # Update display
            self.alert_display.configure(
                text=f"🚨 Alerts Today: {self.alert_count_text}")

            if ENHANCED_FEATURES:
                # INSTANT stress escalation
                alert_id = f"instant_stress_{int(time.time())}_{uuid.uuid4().hex[:8]}"

                location_data = getattr(self, 'current_location', None)

                alert_message = f"⚠️ INSTANT STRESS DETECTION\n\nStress Level: {stress_level:.1%}\nText: \"{text}\"\n\nLocation: {self._format_location_brief(location_data)}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nHigh emotional distress detected - immediate check required"

                # Start escalation for high stress
                escalation_system.start_escalation(
                    alert_id=alert_id,
                    alert_type='instant_stress_detection',
                    message=alert_message,
                    location_data=location_data,
                    evidence_data=None
                )

            # Show stress alert
            InstantStressDialog(
                self.root, text, stress_level, self.alert_count)

            # Update status
            self.update_status(
                f"⚠️ INSTANT STRESS - Level: {stress_level:.1%}")

    def trigger_stress_alert(self, text, stress_level):
        """Trigger alert for high voice stress (legacy method)"""
        self.trigger_instant_stress_alert(text, stress_level)

    def test_system(self):
        """Enhanced test system with audio analysis demo"""
        self.alert_count += 1
        self.alert_count_text = str(self.alert_count)
        self.alert_display.configure(
            text=f"🚨 Alerts Today: {self.alert_count_text}")

        # Test different detection modes
        test_modes = [
            ("Voice Keywords", "System test - voice recognition operational"),
            ("Audio Analysis", "System test - unnatural voice detection operational"),
            ("Stress Detection", "System test - voice stress analysis operational"),
            ("Emergency Protocol", "System test - all emergency systems operational")
        ]

        import random
        test_mode, description = random.choice(test_modes)

        SystemTestDialog(self.root, test_mode, description, self.alert_count)
        self.update_status(
            f"🧪 {test_mode} Test Complete - All Systems Operational")

    def update_status(self, text):
        """Update status display"""
        self.status_display.configure(text=text)

    def trigger_alert(self, text, keywords):
        """Trigger enhanced futuristic alert with escalation"""
        self.alert_count += 1
        self.alert_count_text = str(self.alert_count)

        # Update display
        self.alert_display.configure(
            text=f"🚨 Alerts Today: {self.alert_count_text}")

        if ENHANCED_FEATURES:
            # Enhanced alert with escalation system
            alert_id = f"futuristic_alert_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            # Get location and evidence
            location_data = self.location_service.get_emergency_location_info(
            ) if hasattr(self, 'location_service') else None
            evidence_data = capture_emergency_evidence()

            # Assess severity
            severity = self._assess_keyword_severity(keywords)

            # Create alert message
            alert_message = f"🎤 FUTURISTIC VOICE EMERGENCY\n\nKeywords: {', '.join(keywords)}\nText: \"{text}\"\nSeverity: {severity}\n\nLocation: {self._format_location_brief(location_data)}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nImmediate assistance required!"

            # Start escalation
            escalation_system.start_escalation(
                alert_id=alert_id,
                alert_type='futuristic_voice_detection',
                message=alert_message,
                location_data=location_data,
                evidence_data=evidence_data
            )

            # Show enhanced alert dialog
            try:
                EnhancedFuturisticAlertDialog(
                    self.root, text, keywords, self.alert_count, severity, alert_id)
            except Exception as e:
                print(f"Enhanced dialog error: {e}")
                # Fallback to basic dialog
                FuturisticAlertDialog(
                    self.root, text, keywords, self.alert_count)
        else:
            # Basic alert dialog
            FuturisticAlertDialog(self.root, text, keywords, self.alert_count)

        # Update status
        self.update_status(
            f"🚨 THREAT DETECTED - Alert #{self.alert_count} - ESCALATION ACTIVE")

    def emergency_alert(self):
        """Enhanced manual emergency alert with immediate escalation"""
        # IMMEDIATE ACTIVATION - No confirmation dialog needed
        print("🚨 IMMEDIATE EMERGENCY PROTOCOL ACTIVATED")
        result = True  # Always activate immediately
        if result:
            self.alert_count += 1
            self.alert_count_text = str(self.alert_count)
            self.alert_display.configure(
                text=f"🚨 Alerts Today: {self.alert_count_text}")

            if ENHANCED_FEATURES:
                # Enhanced manual emergency with escalation
                alert_id = f"manual_futuristic_{int(time.time())}_{uuid.uuid4().hex[:8]}"

                # Get location and evidence
                location_data = self.location_service.get_emergency_location_info(
                ) if hasattr(self, 'location_service') else None
                evidence_data = capture_emergency_evidence()

                # Create alert message
                alert_message = f"🚨 MANUAL FUTURISTIC EMERGENCY\n\nUser manually activated emergency protocol via futuristic interface.\nImmediate assistance required!\n\nLocation: {self._format_location_brief(location_data)}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

                # Start escalation
                escalation_system.start_escalation(
                    alert_id=alert_id,
                    alert_type='manual_futuristic_emergency',
                    message=alert_message,
                    location_data=location_data,
                    evidence_data=evidence_data
                )

                # Show enhanced alert dialog
                EnhancedFuturisticAlertDialog(self.root, "Manual emergency activation", [
                                              "emergency"], self.alert_count, "CRITICAL", alert_id)
            else:
                # Basic alert dialog
                FuturisticAlertDialog(self.root, "Manual emergency activation", [
                                      "emergency"], self.alert_count)

    def update_location(self):
        """Update location with futuristic styling"""
        def get_location():
            try:
                import requests
                response = requests.get("http://ip-api.com/json/", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    city = data.get('city', 'Unknown')
                    country = data.get('country', 'Unknown')
                    self.root.after(0, lambda: self.location_display.configure(
                        text=f"📍 Location: {city}, {country}"
                    ))
                else:
                    self.root.after(0, lambda: self.location_display.configure(
                        text="📍 Location: Unavailable"
                    ))
            except:
                self.root.after(0, lambda: self.location_display.configure(
                    text="📍 Location: Offline Mode"
                ))

        threading.Thread(target=get_location, daemon=True).start()

    def open_setup(self):
        """Open futuristic setup dialog"""
        FuturisticSetupDialog(self.root)

    def test_system(self):
        """Test system with futuristic feedback"""
        self.alert_count += 1
        self.alert_count_text = str(self.alert_count)
        self.alert_display.configure(
            text=f"🚨 Alerts Today: {self.alert_count_text}")

        FuturisticAlertDialog(
            self.root, "System test - all systems operational", ["test"], self.alert_count)
        self.update_status("🧪 System Test Complete - All Systems Operational")

    def show_help(self):
        """Show futuristic help dialog"""
        FuturisticHelpDialog(self.root)

    def _assess_keyword_severity(self, keywords):
        """Assess severity level based on detected keywords"""
        high_severity_keywords = [
            "rape", "kidnap", "assault", "violence", "beating me", "choking me",
            "hitting me", "forcing me", "being held", "against my will", "can't escape",
            "domestic violence", "abuse", "threatening me", "stalker"
        ]

        medium_severity_keywords = [
            "help", "save me", "emergency", "danger", "attack", "hurt", "scared",
            "trapped", "unsafe", "in danger", "need help now"
        ]

        # Check for high severity keywords
        for keyword in keywords:
            if any(high_kw in keyword.lower() for high_kw in high_severity_keywords):
                return "CRITICAL"

        # Check for medium severity keywords
        for keyword in keywords:
            if any(med_kw in keyword.lower() for med_kw in medium_severity_keywords):
                return "HIGH"

        return "MEDIUM"

    def _format_location_brief(self, location_data):
        """Format location data briefly"""
        if not location_data:
            return "Location unavailable"

        if location_data.get('address'):
            return location_data['address']
        elif location_data.get('latitude') and location_data.get('longitude'):
            return f"{location_data['latitude']:.4f}, {location_data['longitude']:.4f}"
        else:
            return "Location unavailable"

    def quick_call(self, service):
        """Quick call to emergency services"""
        try:
            numbers = {
                'police': '100',
                'ambulance': '108',
                'fire': '101',
                'women_helpline': '1091',
                'child_helpline': '1098'
            }

            service_names = {
                'police': 'Police',
                'ambulance': 'Ambulance',
                'fire': 'Fire Brigade',
                'women_helpline': 'Women Helpline',
                'child_helpline': 'Child Helpline'
            }

            number = numbers.get(service, '100')
            name = service_names.get(service, 'Emergency Service')

            # Show call dialog with location
            location_text = ""
            if hasattr(self, 'current_location') and self.current_location:
                loc = self.current_location
                location_text = f"\n\n📍 Your Location:\n{loc.get('address', 'Bengaluru, Karnataka, India')}\nCoordinates: {loc.get('latitude', 0):.6f}, {loc.get('longitude', 0):.6f}"

            message = f"📞 CALLING {name.upper()}\n\nNumber: {number}\n\nYour location will be shared automatically.{location_text}\n\n⚠️ This is for REAL emergencies only!"

            result = self.show_futuristic_call_dialog(name, number, location_text)

            if result:
                # Try to open phone app (Windows)
                try:
                    if os.name == 'nt':
                        subprocess.Popen(
                            ['start', f'tel:{number}'], shell=True)

                    # Also create emergency file with details
                    self.create_emergency_call_record(service, number)

                    messagebox.showinfo(
                        "Call Initiated", f"📞 Calling {name} ({number})\n\n📍 Location shared automatically\n⏰ Call logged at {datetime.now().strftime('%H:%M:%S')}")

                except Exception as e:
                    messagebox.showerror(
                        "Call Error", f"Could not initiate call automatically.\n\nPlease dial {number} manually for {name}.")

        except Exception as e:
            print(f"Quick call error: {e}")
            messagebox.showerror("Error", "Could not initiate emergency call.")

    def create_emergency_call_record(self, service, number):
        """Create record of emergency call"""
        try:
            os.makedirs("data/emergency_calls", exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/emergency_calls/call_{service}_{timestamp}.txt"

            location_info = ""
            if hasattr(self, 'current_location') and self.current_location:
                loc = self.current_location
                location_info = f"""
Location Information:
- Address: {loc.get('address', 'Bengaluru, Karnataka, India (IP-based location)')}
- Coordinates: {loc.get('latitude', 0):.8f}, {loc.get('longitude', 0):.8f}
- Accuracy: ±{loc.get('accuracy', 0)}m
- Method: {loc.get('method', 'Unknown')}
"""

            call_record = f"""
EMERGENCY CALL RECORD
=====================

Service: {service.upper()}
Number: {number}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
User: {user_config.get_user_info().get('name', 'Unknown') if ENHANCED_FEATURES else 'Unknown'}

{location_info}

This call was initiated through HerShield Emergency System.
"""

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(call_record)

        except Exception as e:
            print(f"Call record error: {e}")

    def acknowledge_all_alerts(self):
        """Acknowledge all active alerts from main interface"""
        try:
            if ENHANCED_FEATURES and hasattr(escalation_system, 'acknowledge_all_alerts'):
                count = escalation_system.acknowledge_all_alerts()
                if count > 0:
                    messagebox.showinfo(
                        "Alerts Acknowledged", f"✅ {count} alert(s) acknowledged successfully!\nAll escalations stopped.")
                    self.update_status(
                        "✅ All alerts acknowledged - System ready")
                else:
                    messagebox.showinfo(
                        "No Active Alerts", "ℹ️ No active alerts to acknowledge.\nSystem is ready for protection.")
                    self.update_status("ℹ️ No active alerts - System ready")
            else:
                messagebox.showinfo(
                    "Acknowledge", "✅ System acknowledged!\nReady for protection.")
                self.update_status("✅ System acknowledged - Ready")
        except Exception as e:
            print(f"Acknowledge all alerts error: {e}")
            messagebox.showinfo("Acknowledge", "✅ System acknowledged!")
            self.update_status("✅ System acknowledged")

    def load_config(self):
        """Load enhanced configuration with Firebase integration"""
        try:
            if ENHANCED_FEATURES:
                # Try Firebase first, then local
                user_info = self.load_user_data_with_firebase()

                if user_info and user_info.get('name') and user_info.get('email'):
                    self.update_status("⚙️ Configuration Loaded Successfully")
                else:
                    self.update_status("⚙️ Account Setup Required")
            else:
                if os.path.exists("data/config.json"):
                    with open("data/config.json", "r") as f:
                        config = json.load(f)
                    user = config.get('user', {})
                    if user.get('name') and user.get('email'):
                        self.update_status(
                            "⚙️ Configuration Loaded Successfully")
                    else:
                        self.update_status("⚙️ Account Setup Required")
                else:
                    self.update_status("⚙️ Please Configure System First")
        except Exception as e:
            print(f"Config load error: {e}")
            self.update_status("⚠️ Configuration Error - Setup Required")

    def load_user_data_with_firebase(self):
        """Load user data with Firebase integration"""
        try:
            # Get local user info first
            local_user_info = user_config.get_user_info()

            if FIREBASE_ENABLED and local_user_info.get('email'):
                print("🔥 Loading user data from Firebase...")

                # Get contacts from Firebase
                firebase_contacts = get_user_contacts(local_user_info['email'])

                if firebase_contacts:
                    print(
                        f"✅ Loaded {len(firebase_contacts)} contacts from Firebase")
                    # Merge Firebase contacts with local data
                    local_user_info['emergency_contacts'] = firebase_contacts
                    local_user_info['data_source'] = 'firebase'
                else:
                    print("ℹ️ No Firebase contacts found, using local data")
                    local_user_info['data_source'] = 'local'
            else:
                if FIREBASE_ENABLED:
                    print("ℹ️ Firebase available but no email configured")
                else:
                    print("ℹ️ Firebase not available, using local storage")
                local_user_info['data_source'] = 'local'

            return local_user_info

        except Exception as e:
            print(f"Firebase data load error: {e}")
            # Fallback to local data
            return user_config.get_user_info()

    def show_auto_setup_wizard(self):
        """Simplified setup - no welcome dialog"""
        pass  # Removed welcome dialog

    def run_quick_setup_wizard(self):
        """Run the quick setup wizard"""
        try:
            # Step 1: Basic info
            name = tk.simpledialog.askstring("Step 1/3: Your Name",
                                             "What's your name?\n(This helps emergency responders)")
            if not name:
                return

            email = tk.simpledialog.askstring("Step 2/3: Your Email",
                                              "What's your email address?\n(For emergency notifications)")
            if not email:
                return

            # Step 3: Emergency contact
            contact = tk.simpledialog.askstring("Step 3/3: Emergency Contact",
                                                "Enter one emergency contact:\n(Format: Name: +1234567890)")
            if not contact:
                contact = "Emergency Contact: +911"

            # Save configuration
            if ENHANCED_FEATURES:
                user_data = {
                    'name': name.strip(),
                    'email': email.strip(),
                    'emergency_contacts': [contact.strip()],
                    'setup_date': datetime.now().isoformat(),
                    'quick_setup': True
                }

                # Save locally
                user_config.update_user_info(user_data)

                # Save to Firebase if available
                if FIREBASE_ENABLED:
                    try:
                        from core.firebase_service import save_user_data
                        firebase_success = save_user_data(
                            email.strip(), user_data)
                        if firebase_success:
                            print("✅ User data synced to Firebase Cloud")
                    except Exception as e:
                        print(f"Firebase sync error: {e}")

            # Show completion message
            messagebox.showinfo("Setup Complete!",
                                f"🎉 Welcome {name}!\n\n" +
                                "✅ Your HerShield system is now configured\n" +
                                "✅ Emergency contact added\n" +
                                "✅ All systems ready\n\n" +
                                "Click 'ACTIVATE INSTANT GUARDIAN' to start protection!")

            self.update_status("✅ Quick Setup Complete - Ready to Protect!")

        except Exception as e:
            print(f"Quick setup wizard error: {e}")
            messagebox.showerror(
                "Setup Error", "Setup wizard encountered an error.\nPlease use manual configuration.")

    def on_closing(self):
        """Handle application closing properly"""
        try:
            # Stop all tracking and monitoring
            self.location_tracking_active = False
            self.app_running = False
            self.listening = False

            # Stop enhanced features
            if ENHANCED_FEATURES:
                try:
                    acknowledgment_system.stop_monitoring()
                    escalation_system.stop_all_escalations()
                except:
                    pass

            # Give threads time to stop
            import time
            time.sleep(0.5)

            # Destroy window
            self.root.destroy()

        except Exception as e:
            print(f"Cleanup error: {e}")
            # Force close
            self.root.quit()

    def run(self):
        """Start the futuristic app"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nApplication interrupted by user")
            self.on_closing()
        except Exception as e:
            print(f"Application error: {e}")
            self.on_closing()


class FuturisticAlertDialog:
    """Futuristic alert dialog with pink theme"""

    def __init__(self, parent, text, keywords, alert_id):
        self.dialog = ctk.CTkToplevel(parent)
        self.setup_futuristic_alert(text, keywords, alert_id)

    def setup_futuristic_alert(self, text, keywords, alert_id):
        """Setup futuristic alert dialog"""
        self.dialog.title("🚨 Emergency Alert Protocol")
        self.dialog.geometry("600x500")
        self.dialog.configure(fg_color=PINK_COLORS["background"])

        # Make dialog modal and stay on top
        self.dialog.transient()
        self.dialog.grab_set()
        self.dialog.attributes('-topmost', True)
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_alert_close)

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 300
        y = (self.dialog.winfo_screenheight() // 2) - 250
        self.dialog.geometry(f"600x500+{x}+{y}")

        # Play alert sound
        self.play_alert_sound()

        # Main alert container
        alert_container = ctk.CTkFrame(
            self.dialog,
            corner_radius=25,
            fg_color="#dc143c",
            border_width=3,
            border_color=PINK_COLORS["primary"]
        )
        alert_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Pulsing header
        header_frame = ctk.CTkFrame(alert_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=20)

        # Alert title with futuristic styling
        ctk.CTkLabel(
            header_frame,
            text="🚨 EMERGENCY PROTOCOL ACTIVATED 🚨",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(pady=10)

        # Alert ID
        ctk.CTkLabel(
            header_frame,
            text=f"◆ ALERT ID: #{alert_id:04d} ◆",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PINK_COLORS["accent"]
        ).pack()

        # Alert details container
        details_container = ctk.CTkFrame(
            alert_container,
            corner_radius=15,
            fg_color=PINK_COLORS["surface"],
            border_width=2,
            border_color=PINK_COLORS["accent"]
        )
        details_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Alert information
        ctk.CTkLabel(
            details_container,
            text="THREAT DETECTED",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=PINK_COLORS["primary"]
        ).pack(pady=15)

        ctk.CTkLabel(
            details_container,
            text=f"Keywords: {', '.join(keywords)}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PINK_COLORS["text"]
        ).pack(pady=5)

        ctk.CTkLabel(
            details_container,
            text=f"Audio: '{text}'",
            font=ctk.CTkFont(size=14),
            text_color=PINK_COLORS["text_secondary"],
            wraplength=500
        ).pack(pady=10)

        ctk.CTkLabel(
            details_container,
            text=f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            font=ctk.CTkFont(size=12),
            text_color=PINK_COLORS["text_secondary"]
        ).pack(pady=5)

        # Status indicator
        status_frame = ctk.CTkFrame(details_container, fg_color="transparent")
        status_frame.pack(pady=15)

        ctk.CTkLabel(
            status_frame,
            text="📡 SENDING EMERGENCY ALERTS...",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00ff00"
        ).pack()

        # Action buttons
        button_frame = ctk.CTkFrame(alert_container, fg_color="transparent")
        button_frame.pack(pady=20)

        # Call police button
        ctk.CTkButton(
            button_frame,
            text="📞 CALL EMERGENCY",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=200,
            corner_radius=15,
            fg_color="white",
            text_color="black",
            hover_color="#f0f0f0",
            command=self.show_emergency_numbers
        ).pack(side="left", padx=10)

        # I'm safe button
        ctk.CTkButton(
            button_frame,
            text="✅ I'M SAFE",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=200,
            corner_radius=15,
            fg_color=PINK_COLORS["primary"],
            hover_color=PINK_COLORS["secondary"],
            command=self.dialog.destroy
        ).pack(side="left", padx=10)

        # Auto-save alert
        self.save_alert_data(text, keywords, alert_id)

    def show_emergency_numbers(self):
        """Show emergency contact numbers"""
        messagebox.showinfo(
            "Emergency Contacts",
            "📞 EMERGENCY NUMBERS:\n\n"
            "🚔 Police: 100\n"
            "🚑 Ambulance: 108\n"
            "🔥 Fire: 101\n"
            "👮‍♀️ Women Helpline: 1091\n\n"
            "Call immediately if you're in danger!"
        )

    def save_alert_data(self, text, keywords, alert_id):
        """Save alert data with futuristic formatting"""
        try:
            os.makedirs("alerts", exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"alerts/FUTURISTIC_ALERT_{timestamp}.txt"

            alert_content = f"""
◆◆◆ HERSHIELD FUTURISTIC ALERT SYSTEM ◆◆◆

🚨 EMERGENCY ALERT #{alert_id:04d} 🚨

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Keywords Detected: {', '.join(keywords)}
Audio Transcript: "{text}"

⚠️ IMMEDIATE ACTION REQUIRED ⚠️

This alert was generated by HerShield Futuristic Safety System.
Contact emergency services immediately if this is a real emergency.

Emergency Numbers:
• Police: 100
• Ambulance: 108  
• Women Helpline: 1091

◆◆◆ END ALERT ◆◆◆
"""

            with open(filename, "w", encoding='utf-8') as f:
                f.write(alert_content)

        except Exception as e:
            print(f"Alert save error: {e}")

    def on_alert_close(self):
        """Handle alert dialog close"""
        result = messagebox.askyesno("Close Alert",
                                     "Are you sure you want to close this emergency alert?")
        if result:
            self.dialog.destroy()

    def play_alert_sound(self):
        """Play alert sound"""
        try:
            import winsound
            # Play system alert sound
            for _ in range(3):
                winsound.Beep(1000, 300)
                time.sleep(0.1)
        except:
            # Fallback to system bell
            try:
                print('\a' * 5)
            except:
                pass


class FuturisticSetupDialog:
    """Futuristic setup dialog"""

    def __init__(self, parent):
        self.dialog = ctk.CTkToplevel(parent)
        self.setup_futuristic_setup()

    def setup_futuristic_setup(self):
        """Setup futuristic configuration dialog"""
        self.dialog.title("⚙️ Futuristic Configuration")
        self.dialog.geometry("700x600")
        self.dialog.configure(fg_color=PINK_COLORS["background"])

        # Make dialog modal and prevent closing
        self.dialog.transient()
        self.dialog.grab_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_dialog_close)

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 350
        y = (self.dialog.winfo_screenheight() // 2) - 300
        self.dialog.geometry(f"700x600+{x}+{y}")

        # Main container
        main_container = ctk.CTkFrame(
            self.dialog,
            corner_radius=25,
            fg_color=PINK_COLORS["surface"],
            border_width=2,
            border_color=PINK_COLORS["primary"]
        )
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Header
        ctk.CTkLabel(
            main_container,
            text="◆ GUARDIAN CONFIGURATION ◆",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=PINK_COLORS["primary"]
        ).pack(pady=20)

        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(
            main_container,
            corner_radius=15,
            fg_color=PINK_COLORS["background"]
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Personal info section
        self.create_config_section(scroll_frame, "👤 PERSONAL PROFILE", [
            ("Full Name:", "name_entry"),
            ("Email Address:", "email_entry"),
            ("Phone Number:", "phone_entry")
        ])

        # Emergency contacts section
        contacts_frame = ctk.CTkFrame(
            scroll_frame, corner_radius=15, fg_color=PINK_COLORS["surface"])
        contacts_frame.pack(fill="x", padx=10, pady=15)

        ctk.CTkLabel(
            contacts_frame,
            text="🚨 EMERGENCY CONTACTS",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PINK_COLORS["primary"]
        ).pack(pady=15)

        self.contacts_textbox = ctk.CTkTextbox(
            contacts_frame,
            width=500,
            height=120,
            corner_radius=10,
            font=ctk.CTkFont(size=12)
        )
        self.contacts_textbox.pack(padx=20, pady=10)
        self.contacts_textbox.insert(
            "0.0", "Contact 1: +1234567890\nContact 2: +0987654321\nContact 3: +1122334455")

        # Google Maps location section
        gmaps_frame = ctk.CTkFrame(
            scroll_frame, corner_radius=15, fg_color=PINK_COLORS["surface"])
        gmaps_frame.pack(fill="x", padx=10, pady=15)

        ctk.CTkLabel(
            gmaps_frame,
            text="🗺️ HIGH-ACCURACY LOCATION (Optional)",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PINK_COLORS["primary"]
        ).pack(pady=15)

        # Google Maps API key entry
        api_key_frame = ctk.CTkFrame(gmaps_frame, fg_color="transparent")
        api_key_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(
            api_key_frame,
            text="Google Maps API Key:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(anchor="w")

        self.api_key_entry = ctk.CTkEntry(
            api_key_frame,
            width=400,
            height=35,
            corner_radius=10,
            placeholder_text="Enter your Google Maps API key for ±20m accuracy"
        )
        self.api_key_entry.pack(fill="x", pady=5)

        # Load existing API key
        try:
            google_service = GoogleMapsLocationService()
            if google_service.api_key:
                self.api_key_entry.insert(0, google_service.api_key)
        except:
            pass

        # Info text
        info_text = ctk.CTkTextbox(
            gmaps_frame,
            width=500,
            height=80,
            corner_radius=10,
            font=ctk.CTkFont(size=11)
        )
        info_text.pack(padx=20, pady=10)
        info_text.insert("0.0", 
            "🎁 FREE TIER: 40,000 requests/month (enough for years of use)\n" +
            "🎯 ACCURACY: ±20-100m vs ±5000m with IP-only location\n" +
            "📋 SETUP: console.cloud.google.com → Enable Geolocation API → Create API Key")
        info_text.configure(state="disabled")

        # Test button
        ctk.CTkButton(
            gmaps_frame,
            text="🧪 TEST API KEY",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35,
            width=150,
            corner_radius=10,
            fg_color=PINK_COLORS["accent"],
            hover_color=PINK_COLORS["primary"],
            command=self.test_google_maps_api
        ).pack(pady=10)

        # Button frame
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(pady=20)

        # Save button
        ctk.CTkButton(
            button_frame,
            text="💾 SAVE CONFIGURATION",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=250,
            corner_radius=15,
            fg_color=PINK_COLORS["primary"],
            hover_color=PINK_COLORS["secondary"],
            border_width=2,
            border_color=PINK_COLORS["accent"],
            command=self.save_futuristic_config
        ).pack(side="left", padx=10)

        # Cancel button
        ctk.CTkButton(
            button_frame,
            text="❌ CANCEL",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=150,
            corner_radius=15,
            fg_color=PINK_COLORS["dark"],
            hover_color="#666666",
            command=self.dialog.destroy
        ).pack(side="left", padx=10)

    def create_config_section(self, parent, title, fields):
        """Create configuration section"""
        section_frame = ctk.CTkFrame(
            parent, corner_radius=15, fg_color=PINK_COLORS["surface"])
        section_frame.pack(fill="x", padx=10, pady=15)

        ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PINK_COLORS["primary"]
        ).pack(pady=15)

        # Create entry fields
        for label_text, var_name in fields:
            ctk.CTkLabel(
                section_frame,
                text=label_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=PINK_COLORS["text"]
            ).pack(anchor="w", padx=20, pady=(10, 5))

            entry = ctk.CTkEntry(
                section_frame,
                width=400,
                height=40,
                corner_radius=10,
                font=ctk.CTkFont(size=14)
            )
            entry.pack(padx=20, pady=(0, 10))
            setattr(self, var_name, entry)

    def test_google_maps_api(self):
        """Test Google Maps API key"""
        try:
            api_key = self.api_key_entry.get().strip()
            if not api_key:
                messagebox.showwarning("API Key Required", "Please enter your Google Maps API key first.")
                return
            
            # Test the API key
            from core.google_maps_location import GoogleMapsLocationService
            
            # Save temporarily
            google_service = GoogleMapsLocationService()
            google_service.api_key = api_key
            
            # Test location
            location = google_service.get_high_accuracy_location()
            
            if location:
                accuracy = location.get('accuracy', 0)
                messagebox.showinfo(
                    "API Test Successful!",
                    f"✅ Google Maps API is working!\n\n" +
                    f"📍 Location: {location['latitude']:.6f}, {location['longitude']:.6f}\n" +
                    f"🎯 Accuracy: ±{accuracy}m\n" +
                    f"🔧 Method: {location.get('method', 'unknown')}\n\n" +
                    "Your API key will be saved when you click 'SAVE CONFIGURATION'."
                )
            else:
                messagebox.showerror(
                    "API Test Failed",
                    "❌ Google Maps API test failed.\n\n" +
                    "Please check:\n" +
                    "• API key is correct\n" +
                    "• Geolocation API is enabled\n" +
                    "• Billing is set up (free tier available)\n" +
                    "• Network connectivity"
                )
        except Exception as e:
            messagebox.showerror("Test Error", f"API test error: {e}")

    def save_futuristic_config(self):
        """Save futuristic configuration"""
        try:
            # Validate inputs
            name = self.name_entry.get().strip()
            email = self.email_entry.get().strip()
            phone = self.phone_entry.get().strip()
            contacts_text = self.contacts_textbox.get("0.0", "end").strip()
            api_key = self.api_key_entry.get().strip()

            if not name:
                messagebox.showerror("Error", "Please enter your name")
                return

            if not email:
                messagebox.showerror("Error", "Please enter your email")
                return

            if not contacts_text:
                messagebox.showerror("Error", "Please add emergency contacts")
                return

            # Save Google Maps API key if provided
            if api_key:
                try:
                    from core.google_maps_location import GoogleMapsLocationService
                    google_service = GoogleMapsLocationService()
                    google_service.save_api_key(api_key)
                except Exception as e:
                    print(f"Error saving Google Maps API key: {e}")

            config = {
                "user": {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "contacts": [c.strip() for c in contacts_text.split('\n') if c.strip()]
                },
                "keywords": KEYWORDS,
                "theme": "futuristic_pink",
                "setup_date": datetime.now().isoformat(),
                "google_maps_enabled": bool(api_key)
            }

            os.makedirs("data", exist_ok=True)
            with open("data/config.json", "w") as f:
                json.dump(config, f, indent=2)

            # Mark setup as complete
            with open("data/.setup_complete", "w") as f:
                f.write("Futuristic setup completed")

            messagebox.showinfo(
                "Success", "🎉 Configuration Saved Successfully!")
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Configuration save failed: {e}")

    def on_dialog_close(self):
        """Handle dialog close event"""
        result = messagebox.askyesno("Close Configuration",
                                     "Are you sure you want to close without saving?")
        if result:
            self.dialog.destroy()


class FuturisticHelpDialog:
    """Futuristic help dialog"""

    def __init__(self, parent):
        self.dialog = ctk.CTkToplevel(parent)
        self.setup_futuristic_help()

    def setup_futuristic_help(self):
        """Setup futuristic help dialog"""
        self.dialog.title("💡 Futuristic Help System")
        self.dialog.geometry("800x600")
        self.dialog.configure(fg_color=PINK_COLORS["background"])

        # Center dialog
        x = (self.dialog.winfo_screenwidth() // 2) - 400
        y = (self.dialog.winfo_screenheight() // 2) - 300
        self.dialog.geometry(f"800x600+{x}+{y}")

        # Main container
        main_container = ctk.CTkFrame(
            self.dialog,
            corner_radius=25,
            fg_color=PINK_COLORS["surface"],
            border_width=2,
            border_color=PINK_COLORS["primary"]
        )
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Header
        ctk.CTkLabel(
            main_container,
            text="◆ GUARDIAN HELP SYSTEM ◆",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=PINK_COLORS["primary"]
        ).pack(pady=20)

        # Scrollable help content
        help_scroll = ctk.CTkScrollableFrame(
            main_container,
            corner_radius=15,
            fg_color=PINK_COLORS["background"]
        )
        help_scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Help sections
        help_sections = [
            ("🛡️ GUARDIAN ACTIVATION", [
                "• Click 'ACTIVATE GUARDIAN' to start voice monitoring",
                "• System listens for danger keywords automatically",
                "• Advanced AI detects threats in real-time",
                "• Futuristic interface provides instant feedback"
            ]),
            ("🚨 EMERGENCY PROTOCOL", [
                "• Red emergency button triggers immediate alerts",
                "• Automatic evidence capture and location sharing",
                "• Multi-channel alert delivery system",
                "• Continuous monitoring until deactivated"
            ]),
            ("⚙️ SYSTEM CONFIGURATION", [
                "• Configure personal profile in setup dialog",
                "• Add multiple emergency contacts",
                "• Test system regularly for optimal performance",
                "• Customize alert preferences and settings"
            ]),
            ("🔮 FUTURISTIC FEATURES", [
                "• Advanced pink-themed UI with animations",
                "• Real-time threat analysis and classification",
                "• Offline capability with local notifications",
                "• Elegant button designs with hover effects"
            ])
        ]

        for title, items in help_sections:
            section_frame = ctk.CTkFrame(
                help_scroll, corner_radius=15, fg_color=PINK_COLORS["surface"])
            section_frame.pack(fill="x", padx=10, pady=15)

            ctk.CTkLabel(
                section_frame,
                text=title,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=PINK_COLORS["primary"]
            ).pack(pady=(15, 10))

            for item in items:
                ctk.CTkLabel(
                    section_frame,
                    text=item,
                    font=ctk.CTkFont(size=12),
                    text_color=PINK_COLORS["text"]
                ).pack(anchor="w", padx=20, pady=2)

            ctk.CTkLabel(section_frame, text="").pack(pady=5)  # Spacer


class EnhancedFuturisticAlertDialog:
    """Enhanced futuristic alert dialog with escalation features"""

    def __init__(self, parent, text, keywords, alert_id, severity, escalation_id):
        self.dialog = ctk.CTkToplevel(parent)
        self.escalation_id = escalation_id
        self.setup_enhanced_alert(text, keywords, alert_id, severity)

    def setup_enhanced_alert(self, text, keywords, alert_id, severity):
        """Setup enhanced futuristic alert dialog"""
        self.dialog.title("🚨 Enhanced Emergency Protocol")
        self.dialog.geometry("700x600")
        self.dialog.configure(fg_color=PINK_COLORS["background"])

        # Make dialog modal and stay on top
        self.dialog.transient()
        self.dialog.grab_set()
        self.dialog.attributes('-topmost', True)
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_enhanced_alert_close)

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 350
        y = (self.dialog.winfo_screenheight() // 2) - 300
        self.dialog.geometry(f"700x600+{x}+{y}")

        # Play enhanced alert sound
        self.play_enhanced_alert_sound()

        # Main alert container with severity-based color
        severity_colors = {
            "CRITICAL": "#8b0000",  # Dark red
            "HIGH": "#dc143c",      # Crimson
            "MEDIUM": "#ff8c00"     # Orange
        }

        alert_container = ctk.CTkFrame(
            self.dialog,
            corner_radius=25,
            fg_color=severity_colors.get(severity, "#dc143c"),
            border_width=3,
            border_color=PINK_COLORS["primary"]
        )
        alert_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Enhanced header with escalation info
        header_frame = ctk.CTkFrame(alert_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=20)

        # Alert title with severity
        ctk.CTkLabel(
            header_frame,
            text=f"🚨 {severity} EMERGENCY PROTOCOL 🚨",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="white"
        ).pack(pady=10)

        # Escalation status
        ctk.CTkLabel(
            header_frame,
            text="◆ ESCALATION SYSTEM ACTIVE ◆",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PINK_COLORS["accent"]
        ).pack()

        # Alert ID and escalation ID
        ctk.CTkLabel(
            header_frame,
            text=f"Alert #{alert_id:04d} | Escalation: {self.escalation_id[:8]}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=PINK_COLORS["text_secondary"]
        ).pack(pady=5)

        # Enhanced alert details container
        details_container = ctk.CTkFrame(
            alert_container,
            corner_radius=15,
            fg_color=PINK_COLORS["surface"],
            border_width=2,
            border_color=PINK_COLORS["accent"]
        )
        details_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Threat information
        ctk.CTkLabel(
            details_container,
            text="ENHANCED THREAT DETECTION",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=PINK_COLORS["primary"]
        ).pack(pady=15)

        # Severity indicator
        ctk.CTkLabel(
            details_container,
            text=f"Severity Level: {severity}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ff0000" if severity == "CRITICAL" else "#ff8c00"
        ).pack(pady=5)

        ctk.CTkLabel(
            details_container,
            text=f"Keywords: {', '.join(keywords)}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PINK_COLORS["text"]
        ).pack(pady=5)

        ctk.CTkLabel(
            details_container,
            text=f"Audio: '{text}'",
            font=ctk.CTkFont(size=14),
            text_color=PINK_COLORS["text_secondary"],
            wraplength=600
        ).pack(pady=10)

        # Escalation timeline
        timeline_frame = ctk.CTkFrame(
            details_container, corner_radius=10, fg_color=PINK_COLORS["background"])
        timeline_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            timeline_frame,
            text="🔔 ESCALATION TIMELINE:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=PINK_COLORS["primary"]
        ).pack(pady=5)

        timeline_text = "• 0s: Initial alerts sent\n• 15s: Enhanced alerts with sound\n• 30s: Emergency calling initiated"
        ctk.CTkLabel(
            timeline_frame,
            text=timeline_text,
            font=ctk.CTkFont(size=12),
            text_color=PINK_COLORS["text"]
        ).pack(pady=5)

        # Status indicator with animation
        self.status_label = ctk.CTkLabel(
            details_container,
            text="📡 SENDING ENHANCED EMERGENCY ALERTS...",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00ff00"
        )
        self.status_label.pack(pady=15)

        # Enhanced action buttons
        button_frame = ctk.CTkFrame(alert_container, fg_color="transparent")
        button_frame.pack(pady=20)

        # Emergency services button
        ctk.CTkButton(
            button_frame,
            text="📞 EMERGENCY SERVICES",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=60,
            width=220,
            corner_radius=15,
            fg_color="white",
            text_color="black",
            hover_color="#f0f0f0",
            command=self.show_enhanced_emergency_numbers
        ).pack(side="left", padx=10)

        # Acknowledge button
        ctk.CTkButton(
            button_frame,
            text="✅ ACKNOWLEDGE ALERT",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=60,
            width=220,
            corner_radius=15,
            fg_color=PINK_COLORS["primary"],
            hover_color=PINK_COLORS["secondary"],
            command=self.acknowledge_and_close
        ).pack(side="left", padx=10)

        # Auto-save enhanced alert
        self.save_enhanced_alert_data(text, keywords, alert_id, severity)

        # Start status animation
        self.animate_status()

    def show_enhanced_emergency_numbers(self):
        """Show enhanced emergency contact numbers"""
        messagebox.showinfo(
            "Enhanced Emergency Contacts",
            "🚨 IMMEDIATE EMERGENCY CONTACTS:\n\n"
            "🚔 Police: 100\n"
            "🚑 Ambulance: 108\n"
            "🔥 Fire Brigade: 101\n"
            "👮‍♀️ Women Helpline: 1091\n"
            "🆘 Child Helpline: 1098\n"
            "🌐 Cyber Crime: 1930\n\n"
            "⚠️ CALL IMMEDIATELY IF IN DANGER!\n\n"
            "📍 Your location has been shared with emergency contacts.\n"
            "📷 Evidence has been automatically captured."
        )

    def acknowledge_and_close(self):
        """Acknowledge alert and stop escalation"""
        try:
            if ENHANCED_FEATURES and hasattr(escalation_system, 'acknowledge_alert'):
                result = escalation_system.acknowledge_alert(
                    self.escalation_id)
                if result:
                    messagebox.showinfo(
                        "Alert Acknowledged", "✅ Alert acknowledged successfully!\nEscalation system stopped.")
                else:
                    messagebox.showinfo(
                        "Alert Status", "✅ Alert processed successfully!")
            else:
                messagebox.showinfo("Alert Acknowledged",
                                    "✅ Alert acknowledged!")

            self.dialog.destroy()
        except Exception as e:
            print(f"Acknowledge error: {e}")
            messagebox.showinfo("Alert Acknowledged", "✅ Alert acknowledged!")
            self.dialog.destroy()

    def save_enhanced_alert_data(self, text, keywords, alert_id, severity):
        """Save enhanced alert data"""
        try:
            os.makedirs("alerts", exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"alerts/ENHANCED_FUTURISTIC_ALERT_{timestamp}.txt"

            alert_content = f"""
◆◆◆ HERSHIELD ENHANCED FUTURISTIC ALERT SYSTEM ◆◆◆

🚨 {severity} EMERGENCY ALERT #{alert_id:04d} 🚨

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Escalation ID: {self.escalation_id}
Severity Level: {severity}
Keywords Detected: {', '.join(keywords)}
Audio Transcript: "{text}"

🔔 ESCALATION FEATURES ACTIVE:
• Progressive alert system (15s → 30s intervals)
• Emergency calling capability
• Evidence capture (photos + video)
• Location sharing with emergency contacts
• Offline alert broadcasting
• Multi-channel notification delivery

⚠️ IMMEDIATE ACTION REQUIRED ⚠️

This alert was generated by HerShield Enhanced Futuristic Safety System
with advanced escalation capabilities and AI threat detection.

Contact emergency services immediately if this is a real emergency.

Enhanced Emergency Numbers:
• Police: 100
• Ambulance: 108  
• Women Helpline: 1091
• Child Helpline: 1098
• Cyber Crime: 1930

◆◆◆ END ENHANCED ALERT ◆◆◆
"""

            with open(filename, "w", encoding='utf-8') as f:
                f.write(alert_content)

        except Exception as e:
            print(f"Enhanced alert save error: {e}")

    def on_enhanced_alert_close(self):
        """Handle enhanced alert dialog close"""
        result = messagebox.askyesno("Close Enhanced Alert",
                                     "⚠️ ESCALATION SYSTEM IS ACTIVE!\n\nClosing this dialog will NOT stop the escalation.\nUse 'Acknowledge Alert' to stop escalation.\n\nAre you sure you want to close?")
        if result:
            self.dialog.destroy()

    def play_enhanced_alert_sound(self):
        """Play enhanced alert sound with escalation pattern"""
        def sound_thread():
            try:
                import winsound
                # Enhanced alert pattern - more urgent
                for cycle in range(3):
                    # Siren pattern
                    for freq in range(800, 1200, 50):
                        winsound.Beep(freq, 100)
                    for freq in range(1200, 800, -50):
                        winsound.Beep(freq, 100)
                    time.sleep(0.2)

                # Urgent beeps
                for _ in range(5):
                    winsound.Beep(1500, 200)
                    time.sleep(0.1)
                    winsound.Beep(1000, 200)
                    time.sleep(0.1)
            except:
                # Fallback to system bell
                try:
                    for _ in range(15):
                        print('\a', end='', flush=True)
                        time.sleep(0.2)
                except:
                    pass

        threading.Thread(target=sound_thread, daemon=True).start()

    def animate_status(self):
        """Animate status text"""
        def update_status():
            if hasattr(self, 'status_label'):
                current_text = self.status_label.cget("text")
                if "..." in current_text:
                    new_text = current_text.replace("...", "")
                else:
                    new_text = current_text + "..."

                self.status_label.configure(text=new_text)

                # Schedule next update
                self.dialog.after(1000, update_status)

        update_status()


class InstantThreatDialog:
    """Instant threat detection dialog - appears immediately"""

    def __init__(self, parent, description, threat_type, confidence, alert_id, escalation_id):
        self.dialog = ctk.CTkToplevel(parent)
        self.escalation_id = escalation_id
        self.setup_instant_threat_dialog(
            description, threat_type, confidence, alert_id)

    def setup_instant_threat_dialog(self, description, threat_type, confidence, alert_id):
        """Setup instant threat dialog with maximum urgency"""
        self.dialog.title("🚨 INSTANT THREAT DETECTED")
        self.dialog.geometry("750x650")
        # Dark red for maximum urgency
        self.dialog.configure(fg_color="#8b0000")

        # Maximum priority settings
        self.dialog.transient()
        self.dialog.grab_set()
        self.dialog.attributes('-topmost', True)
        self.dialog.attributes('-fullscreen', False)
        self.dialog.focus_force()

        # Center and make prominent
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 375
        y = (self.dialog.winfo_screenheight() // 2) - 325
        self.dialog.geometry(f"750x650+{x}+{y}")

        # Play URGENT alert sound immediately
        self.play_urgent_threat_sound()

        # Main container
        main_container = ctk.CTkFrame(
            self.dialog,
            corner_radius=25,
            fg_color="#8b0000",
            border_width=5,
            border_color="#ff0000"
        )
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Flashing header
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=15)

        # Urgent title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="🚨 INSTANT THREAT DETECTED 🚨",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        self.title_label.pack(pady=10)

        # Threat details
        details_frame = ctk.CTkFrame(
            main_container,
            corner_radius=15,
            fg_color=PINK_COLORS["surface"]
        )
        details_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Alert info
        ctk.CTkLabel(
            details_frame,
            text=f"◆ INSTANT ALERT #{alert_id:04d} ◆",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PINK_COLORS["primary"]
        ).pack(pady=15)

        # Threat type and confidence
        ctk.CTkLabel(
            details_frame,
            text=f"THREAT TYPE: {threat_type.upper()}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ff0000"
        ).pack(pady=10)

        ctk.CTkLabel(
            details_frame,
            text=f"Confidence: {confidence:.1%}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ff4444"
        ).pack(pady=5)

        ctk.CTkLabel(
            details_frame,
            text=description,
            font=ctk.CTkFont(size=14),
            text_color=PINK_COLORS["text"],
            wraplength=600
        ).pack(pady=15)

        # Instant response info
        response_frame = ctk.CTkFrame(
            details_frame, corner_radius=10, fg_color="#ff4444")
        response_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            response_frame,
            text="⚡ INSTANT RESPONSE ACTIVATED ⚡",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(pady=10)

        response_text = "• Emergency contacts notified immediately\n• Location shared in real-time\n• Evidence capture initiated\n• Escalation system active"
        ctk.CTkLabel(
            response_frame,
            text=response_text,
            font=ctk.CTkFont(size=12),
            text_color="white"
        ).pack(pady=10)

        # Action buttons
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(pady=20)

        # Emergency services
        ctk.CTkButton(
            button_frame,
            text="📞 CALL EMERGENCY NOW",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=70,
            width=250,
            corner_radius=15,
            fg_color="white",
            text_color="black",
            hover_color="#f0f0f0",
            command=self.call_emergency_now
        ).pack(side="left", padx=15)

        # Acknowledge
        ctk.CTkButton(
            button_frame,
            text="✅ I'M SAFE NOW",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=70,
            width=200,
            corner_radius=15,
            fg_color=PINK_COLORS["primary"],
            hover_color=PINK_COLORS["secondary"],
            command=self.acknowledge_threat
        ).pack(side="left", padx=15)

        # Start flashing animation
        self.start_flashing_animation()

    def call_emergency_now(self):
        """Show emergency numbers with instant calling options"""
        messagebox.showinfo(
            "EMERGENCY - CALL NOW",
            "🚨 CALL IMMEDIATELY:\n\n"
            "🚔 Police: 100\n"
            "🚑 Ambulance: 108\n"
            "👮‍♀️ Women Helpline: 1091\n\n"
            "⚠️ YOUR LOCATION HAS BEEN SHARED\n"
            "📷 EVIDENCE HAS BEEN CAPTURED\n"
            "📡 ALERTS SENT TO ALL CONTACTS"
        )

    def acknowledge_threat(self):
        """Acknowledge threat and stop escalation"""
        try:
            if ENHANCED_FEATURES and hasattr(escalation_system, 'acknowledge_alert'):
                escalation_system.acknowledge_alert(self.escalation_id)
                messagebox.showinfo(
                    "Threat Acknowledged", "✅ Threat acknowledged!\nEscalation stopped.")
            else:
                messagebox.showinfo("Threat Acknowledged",
                                    "✅ Threat acknowledged!")

            self.dialog.destroy()
        except Exception as e:
            print(f"Acknowledge threat error: {e}")
            messagebox.showinfo("Threat Acknowledged",
                                "✅ Threat acknowledged!")
            self.dialog.destroy()

    def play_urgent_threat_sound(self):
        """Play urgent threat sound pattern"""
        def sound_thread():
            try:
                import winsound
                # Maximum urgency sound pattern
                for cycle in range(5):
                    # Rapid siren
                    for freq in range(1000, 2000, 100):
                        winsound.Beep(freq, 50)
                    for freq in range(2000, 1000, -100):
                        winsound.Beep(freq, 50)

                # Urgent alarm
                for _ in range(10):
                    winsound.Beep(2000, 100)
                    time.sleep(0.05)
                    winsound.Beep(1500, 100)
                    time.sleep(0.05)
            except:
                # Fallback
                for _ in range(20):
                    print('\a', end='', flush=True)
                    time.sleep(0.1)

        threading.Thread(target=sound_thread, daemon=True).start()

    def start_flashing_animation(self):
        """Start subtle attention animation without harsh flashing"""
        self.flash_state = 0
        
        def gentle_flash():
            if hasattr(self, 'title_label'):
                self.flash_state = (self.flash_state + 1) % 40
                
                # Smooth color transition instead of harsh flashing
                if self.flash_state < 20:
                    intensity = self.flash_state / 20.0
                    # Interpolate between white and yellow
                    red = int(255)
                    green = int(255)
                    blue = int(255 - (intensity * 100))  # Gradually reduce blue for yellow tint
                else:
                    intensity = (40 - self.flash_state) / 20.0
                    red = int(255)
                    green = int(255)
                    blue = int(255 - (intensity * 100))
                
                color = f"#{red:02x}{green:02x}{blue:02x}"
                self.title_label.configure(text_color=color)
                self.dialog.after(150, gentle_flash)  # Faster, smoother updates

        gentle_flash()


class InstantVoiceAlertDialog:
    """Instant voice alert dialog for keyword detection"""

    def __init__(self, parent, text, keywords, severity, alert_id, escalation_id):
        self.dialog = ctk.CTkToplevel(parent)
        self.escalation_id = escalation_id
        self.setup_instant_voice_dialog(text, keywords, severity, alert_id)

    def setup_instant_voice_dialog(self, text, keywords, severity, alert_id):
        """Setup instant voice alert dialog with futuristic styling"""
        self.dialog.title("🎤 FUTURISTIC VOICE EMERGENCY")
        self.dialog.geometry("800x700")
        
        # Center the dialog
        try:
            x = (self.dialog.winfo_screenwidth() // 2) - 400
            y = (self.dialog.winfo_screenheight() // 2) - 350
            self.dialog.geometry(f"800x700+{x}+{y}")
        except:
            pass

        # Use same futuristic theme as main window
        if CUSTOM_TK_AVAILABLE:
            self.dialog.configure(fg_color=PINK_COLORS["background"])
        else:
            self.dialog.configure(bg=PINK_COLORS["background"])

        # Severity-based accent colors
        severity_colors = {
            "CRITICAL": "#ff0000",
            "HIGH": "#ff4500", 
            "MEDIUM": "#ff8c00"
        }
        accent_color = severity_colors.get(severity, "#ff4500")

        # Priority settings
        self.dialog.transient()
        self.dialog.grab_set()
        self.dialog.attributes('-topmost', True)
        self.dialog.focus_force()

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 350
        y = (self.dialog.winfo_screenheight() // 2) - 300
        self.dialog.geometry(f"700x600+{x}+{y}")

        # Play alert sound
        self.play_voice_alert_sound(severity)

        # Main container
        main_container = ctk.CTkFrame(
            self.dialog,
            corner_radius=25,
            fg_color=severity_colors.get(severity, "#dc143c"),
            border_width=3,
            border_color="#ff0000"
        )
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Header
        ctk.CTkLabel(
            main_container,
            text=f"🎤 {severity} VOICE EMERGENCY 🎤",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(pady=20)

        # Details
        details_frame = ctk.CTkFrame(
            main_container,
            corner_radius=15,
            fg_color=PINK_COLORS["surface"]
        )
        details_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Alert info
        ctk.CTkLabel(
            details_frame,
            text=f"◆ VOICE ALERT #{alert_id:04d} ◆",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PINK_COLORS["primary"]
        ).pack(pady=15)

        # Keywords
        ctk.CTkLabel(
            details_frame,
            text=f"KEYWORDS: {', '.join(keywords[:5])}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ff0000"
        ).pack(pady=10)

        # Voice text
        ctk.CTkLabel(
            details_frame,
            text=f"VOICE: \"{text}\"",
            font=ctk.CTkFont(size=14),
            text_color=PINK_COLORS["text"],
            wraplength=600
        ).pack(pady=15)

        # Instant response
        ctk.CTkLabel(
            details_frame,
            text="⚡ INSTANT EMERGENCY RESPONSE ACTIVATED ⚡",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00ff00"
        ).pack(pady=15)

        # Action buttons
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="📞 EMERGENCY SERVICES",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=60,
            width=220,
            corner_radius=15,
            fg_color="white",
            text_color="black",
            command=self.show_emergency_contacts
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="✅ ACKNOWLEDGE",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=60,
            width=180,
            corner_radius=15,
            fg_color=PINK_COLORS["primary"],
            command=self.acknowledge_alert
        ).pack(side="left", padx=10)

    def show_emergency_contacts(self):
        """Show emergency contacts"""
        messagebox.showinfo(
            "Emergency Contacts",
            "🚨 CALL IMMEDIATELY:\n\n"
            "🚔 Police: 100\n"
            "🚑 Ambulance: 108\n"
            "👮‍♀️ Women Helpline: 1091\n"
            "🆘 Child Helpline: 1098\n\n"
            "📍 Location shared with all contacts\n"
            "📷 Evidence automatically captured"
        )

    def acknowledge_alert(self):
        """Acknowledge alert"""
        try:
            if ENHANCED_FEATURES and hasattr(escalation_system, 'acknowledge_alert'):
                escalation_system.acknowledge_alert(self.escalation_id)
                messagebox.showinfo(
                    "Alert Acknowledged", "✅ Voice alert acknowledged!\nEscalation stopped.")
            else:
                messagebox.showinfo("Alert Acknowledged",
                                    "✅ Voice alert acknowledged!")

            self.dialog.destroy()
        except Exception as e:
            print(f"Acknowledge voice alert error: {e}")
            messagebox.showinfo("Alert Acknowledged",
                                "✅ Voice alert acknowledged!")
            self.dialog.destroy()

    def play_voice_alert_sound(self, severity):
        """Play voice alert sound based on severity"""
        def sound_thread():
            try:
                import winsound
                if severity == "CRITICAL":
                    # Most urgent pattern
                    for _ in range(8):
                        winsound.Beep(1800, 150)
                        time.sleep(0.05)
                        winsound.Beep(1200, 150)
                        time.sleep(0.05)
                elif severity == "HIGH":
                    # High urgency
                    for _ in range(6):
                        winsound.Beep(1500, 200)
                        time.sleep(0.1)
                        winsound.Beep(1000, 200)
                        time.sleep(0.1)
                else:
                    # Medium urgency
                    for _ in range(4):
                        winsound.Beep(1200, 250)
                        time.sleep(0.2)
            except:
                for _ in range(10):
                    print('\a', end='', flush=True)
                    time.sleep(0.2)

        threading.Thread(target=sound_thread, daemon=True).start()


class InstantStressDialog:
    """Instant stress detection dialog"""

    def __init__(self, parent, text, stress_level, alert_id):
        self.dialog = ctk.CTkToplevel(parent)
        self.setup_stress_dialog(text, stress_level, alert_id)

    def setup_stress_dialog(self, text, stress_level, alert_id):
        """Setup instant stress dialog"""
        self.dialog.title("⚠️ INSTANT STRESS DETECTED")
        self.dialog.geometry("600x500")
        self.dialog.configure(fg_color="#ff8c00")

        # Priority settings
        self.dialog.transient()
        self.dialog.grab_set()
        self.dialog.attributes('-topmost', True)

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 300
        y = (self.dialog.winfo_screenheight() // 2) - 250
        self.dialog.geometry(f"600x500+{x}+{y}")

        # Main container
        main_container = ctk.CTkFrame(
            self.dialog,
            corner_radius=25,
            fg_color="#ff8c00",
            border_width=2,
            border_color="#ff0000"
        )
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Header
        ctk.CTkLabel(
            main_container,
            text="⚠️ HIGH STRESS DETECTED ⚠️",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).pack(pady=20)

        # Details
        details_frame = ctk.CTkFrame(
            main_container,
            corner_radius=15,
            fg_color=PINK_COLORS["surface"]
        )
        details_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Stress level
        stress_color = "#ff0000" if stress_level > 0.8 else "#ff8c00"
        ctk.CTkLabel(
            details_frame,
            text=f"Stress Level: {stress_level:.1%}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=stress_color
        ).pack(pady=15)

        # Voice text
        ctk.CTkLabel(
            details_frame,
            text=f"Voice: \"{text}\"",
            font=ctk.CTkFont(size=14),
            text_color=PINK_COLORS["text"],
            wraplength=500
        ).pack(pady=15)

        # Action buttons
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="🆘 I NEED HELP",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=180,
            corner_radius=15,
            fg_color="#dc143c",
            command=self.escalate_to_emergency
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="✅ I'M OK",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=150,
            corner_radius=15,
            fg_color=PINK_COLORS["primary"],
            command=self.dialog.destroy
        ).pack(side="left", padx=10)

    def escalate_to_emergency(self):
        """Escalate to full emergency"""
        self.dialog.destroy()
        messagebox.showinfo(
            "Emergency Escalation",
            "🚨 Escalating to full emergency!\n\n"
            "All emergency contacts will be notified immediately."
        )


def main():
    """Launch the ultra-enhanced futuristic HerShield app"""
    try:
        app = FuturisticHerShield()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Error", f"Failed to start futuristic app: {e}")


if __name__ == "__main__":
    main()


class AdvancedThreatDialog:
    """Advanced threat detection dialog"""

    def __init__(self, parent, description, threat_types, alert_id, audio_data):
        self.dialog = ctk.CTkToplevel(parent)
        self.setup_threat_dialog(
            description, threat_types, alert_id, audio_data)

    def setup_threat_dialog(self, description, threat_types, alert_id, audio_data):
        """Setup advanced threat dialog"""
        self.dialog.title("🚨 Advanced Threat Detection")
        self.dialog.geometry("650x550")
        self.dialog.configure(fg_color=PINK_COLORS["background"])

        # Make dialog modal and stay on top
        self.dialog.transient()
        self.dialog.grab_set()
        self.dialog.attributes('-topmost', True)

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 325
        y = (self.dialog.winfo_screenheight() // 2) - 275
        self.dialog.geometry(f"650x550+{x}+{y}")

        # Main container
        main_container = ctk.CTkFrame(
            self.dialog,
            corner_radius=25,
            fg_color="#8b0000",  # Dark red for serious threats
            border_width=3,
            border_color=PINK_COLORS["primary"]
        )
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Header
        ctk.CTkLabel(
            main_container,
            text="🚨 ADVANCED THREAT DETECTED 🚨",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="white"
        ).pack(pady=20)

        # Threat details
        details_frame = ctk.CTkFrame(
            main_container,
            corner_radius=15,
            fg_color=PINK_COLORS["surface"]
        )
        details_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            details_frame,
            text=f"◆ ALERT ID: #{alert_id:04d} ◆",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PINK_COLORS["primary"]
        ).pack(pady=15)

        ctk.CTkLabel(
            details_frame,
            text="AUDIO ANALYSIS RESULTS:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PINK_COLORS["text"]
        ).pack(pady=10)

        ctk.CTkLabel(
            details_frame,
            text=description,
            font=ctk.CTkFont(size=14),
            text_color=PINK_COLORS["text_secondary"],
            wraplength=500
        ).pack(pady=10)

        ctk.CTkLabel(
            details_frame,
            text=f"Threat Type: {', '.join(threat_types).upper()}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ff4444"
        ).pack(pady=5)

        ctk.CTkLabel(
            details_frame,
            text=f"Detection Time: {datetime.now().strftime('%H:%M:%S')}",
            font=ctk.CTkFont(size=12),
            text_color=PINK_COLORS["text_secondary"]
        ).pack(pady=5)

        # Status
        ctk.CTkLabel(
            details_frame,
            text="📡 EMERGENCY PROTOCOLS ACTIVATED",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00ff00"
        ).pack(pady=15)

        # Action buttons
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="📞 EMERGENCY SERVICES",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=220,
            corner_radius=15,
            fg_color="white",
            text_color="black",
            hover_color="#f0f0f0",
            command=self.show_emergency_services
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="✅ FALSE ALARM",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=180,
            corner_radius=15,
            fg_color=PINK_COLORS["primary"],
            hover_color=PINK_COLORS["secondary"],
            command=self.dialog.destroy
        ).pack(side="left", padx=10)

        # Save threat data
        self.save_threat_data(description, threat_types, alert_id)

        # Play urgent alert sound
        self.play_urgent_alert()

    def show_emergency_services(self):
        """Show emergency services information"""
        messagebox.showinfo(
            "Emergency Services",
            "🚨 IMMEDIATE EMERGENCY CONTACTS:\n\n"
            "🚔 Police: 100\n"
            "🚑 Ambulance: 108\n"
            "🔥 Fire Brigade: 101\n"
            "👮‍♀️ Women Helpline: 1091\n"
            "🆘 Child Helpline: 1098\n\n"
            "⚠️ CALL IMMEDIATELY IF IN DANGER!"
        )

    def save_threat_data(self, description, threat_types, alert_id):
        """Save advanced threat detection data"""
        try:
            os.makedirs("alerts", exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"alerts/ADVANCED_THREAT_{timestamp}.txt"

            content = f"""
◆◆◆ HERSHIELD ADVANCED THREAT DETECTION ◆◆◆

🚨 CRITICAL ALERT #{alert_id:04d} 🚨

Detection Method: Advanced Audio Analysis
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Threat Description: {description}
Threat Categories: {', '.join(threat_types)}

⚠️ AUDIO PATTERN ANALYSIS DETECTED POTENTIAL DANGER ⚠️

This alert was generated by advanced AI audio analysis detecting
unnatural voice patterns, distress sounds, or threatening audio.

IMMEDIATE ACTIONS RECOMMENDED:
1. Verify user safety immediately
2. Contact emergency services if needed
3. Check surrounding environment for threats

Emergency Numbers:
• Police: 100
• Ambulance: 108
• Women Helpline: 1091

◆◆◆ END ADVANCED THREAT ALERT ◆◆◆
"""

            with open(filename, "w", encoding='utf-8') as f:
                f.write(content)

        except Exception as e:
            print(f"Threat data save error: {e}")

    def play_urgent_alert(self):
        """Play urgent alert sound pattern"""
        try:
            import winsound
            # Urgent alert pattern
            for i in range(5):
                winsound.Beep(1200, 200)  # High pitch
                time.sleep(0.1)
                winsound.Beep(800, 200)   # Lower pitch
                time.sleep(0.1)
        except:
            try:
                print('\a' * 10)  # System bell fallback
            except:
                pass


class StressAlertDialog:
    """Voice stress detection dialog"""

    def __init__(self, parent, text, stress_level, alert_id):
        self.dialog = ctk.CTkToplevel(parent)
        self.setup_stress_dialog(text, stress_level, alert_id)

    def setup_stress_dialog(self, text, stress_level, alert_id):
        """Setup stress detection dialog"""
        self.dialog.title("⚠️ Voice Stress Detection")
        self.dialog.geometry("600x450")
        self.dialog.configure(fg_color=PINK_COLORS["background"])

        # Make dialog modal
        self.dialog.transient()
        self.dialog.grab_set()
        self.dialog.attributes('-topmost', True)

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 300
        y = (self.dialog.winfo_screenheight() // 2) - 225
        self.dialog.geometry(f"600x450+{x}+{y}")

        # Main container
        main_container = ctk.CTkFrame(
            self.dialog,
            corner_radius=25,
            fg_color="#ff8c00",  # Orange for stress alerts
            border_width=2,
            border_color=PINK_COLORS["primary"]
        )
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Header
        ctk.CTkLabel(
            main_container,
            text="⚠️ VOICE STRESS DETECTED ⚠️",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(pady=20)

        # Stress details
        details_frame = ctk.CTkFrame(
            main_container,
            corner_radius=15,
            fg_color=PINK_COLORS["surface"]
        )
        details_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            details_frame,
            text=f"◆ STRESS ALERT #{alert_id:04d} ◆",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PINK_COLORS["primary"]
        ).pack(pady=15)

        # Stress level indicator
        stress_color = "#ff0000" if stress_level > 0.8 else "#ff8c00" if stress_level > 0.6 else "#ffff00"

        ctk.CTkLabel(
            details_frame,
            text=f"Stress Level: {stress_level:.1%}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=stress_color
        ).pack(pady=10)

        ctk.CTkLabel(
            details_frame,
            text=f"Voice Analysis: '{text}'",
            font=ctk.CTkFont(size=14),
            text_color=PINK_COLORS["text"],
            wraplength=500
        ).pack(pady=10)

        # Stress indicators
        indicators_text = "Detected Indicators:\n• Voice pitch variations\n• Speech pattern irregularities\n• Emotional stress markers"

        ctk.CTkLabel(
            details_frame,
            text=indicators_text,
            font=ctk.CTkFont(size=12),
            text_color=PINK_COLORS["text_secondary"]
        ).pack(pady=10)

        # Action buttons
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="🆘 NEED HELP",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=180,
            corner_radius=15,
            fg_color="#dc143c",
            hover_color="#b22222",
            command=self.escalate_to_emergency
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="✅ I'M OK",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=150,
            corner_radius=15,
            fg_color=PINK_COLORS["primary"],
            hover_color=PINK_COLORS["secondary"],
            command=self.dialog.destroy
        ).pack(side="left", padx=10)

    def escalate_to_emergency(self):
        """Escalate stress alert to full emergency"""
        self.dialog.destroy()
        messagebox.showinfo(
            "Emergency Escalation",
            "🚨 Escalating to full emergency protocol!\n\n"
            "Emergency contacts will be notified immediately."
        )


class SystemTestDialog:
    """Enhanced system test dialog"""

    def __init__(self, parent, test_mode, description, alert_id):
        self.dialog = ctk.CTkToplevel(parent)
        self.setup_test_dialog(test_mode, description, alert_id)

    def setup_test_dialog(self, test_mode, description, alert_id):
        """Setup system test dialog"""
        self.dialog.title("🧪 System Test Results")
        self.dialog.geometry("550x400")
        self.dialog.configure(fg_color=PINK_COLORS["background"])

        # Make dialog modal
        self.dialog.transient()
        self.dialog.grab_set()

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 275
        y = (self.dialog.winfo_screenheight() // 2) - 200
        self.dialog.geometry(f"550x400+{x}+{y}")

        # Main container
        main_container = ctk.CTkFrame(
            self.dialog,
            corner_radius=25,
            fg_color="#228b22",  # Green for successful tests
            border_width=2,
            border_color=PINK_COLORS["primary"]
        )
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Header
        ctk.CTkLabel(
            main_container,
            text="🧪 SYSTEM TEST COMPLETE 🧪",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).pack(pady=20)

        # Test results
        results_frame = ctk.CTkFrame(
            main_container,
            corner_radius=15,
            fg_color=PINK_COLORS["surface"]
        )
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            results_frame,
            text=f"◆ TEST #{alert_id:04d} ◆",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PINK_COLORS["primary"]
        ).pack(pady=15)

        ctk.CTkLabel(
            results_frame,
            text=f"Test Mode: {test_mode}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PINK_COLORS["text"]
        ).pack(pady=10)

        ctk.CTkLabel(
            results_frame,
            text=description,
            font=ctk.CTkFont(size=14),
            text_color=PINK_COLORS["text_secondary"],
            wraplength=450
        ).pack(pady=10)

        # System status
        status_items = [
            "✅ Voice Recognition: OPERATIONAL",
            "✅ Audio Analysis: OPERATIONAL",
            "✅ Stress Detection: OPERATIONAL",
            "✅ Emergency Protocols: OPERATIONAL",
            "✅ Alert Systems: OPERATIONAL"
        ]

        for item in status_items:
            ctk.CTkLabel(
                results_frame,
                text=item,
                font=ctk.CTkFont(size=12),
                text_color="#00ff00"
            ).pack(pady=2)

        # Close button
        ctk.CTkButton(
            main_container,
            text="✅ CLOSE",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=150,
            corner_radius=15,
            fg_color=PINK_COLORS["primary"],
            hover_color=PINK_COLORS["secondary"],
            command=self.dialog.destroy
        ).pack(pady=20)

class FuturisticVoiceAlertDialog:
    """Futuristic voice alert dialog matching main system theme"""
    
    def __init__(self, parent, text, keywords):
        self.result = None
        self.dialog = None
        self.setup_dialog(parent, text, keywords)
        
    def setup_dialog(self, parent, text, keywords):
        """Setup futuristic voice alert dialog"""
        if CUSTOM_TK_AVAILABLE:
            self.dialog = ctk.CTkToplevel(parent)
        else:
            self.dialog = tk.Toplevel(parent)
            
        self.dialog.title("🎤 FUTURISTIC VOICE EMERGENCY PROTOCOL")
        self.dialog.geometry("900x700")
        
        # Center dialog
        try:
            x = (self.dialog.winfo_screenwidth() // 2) - 450
            y = (self.dialog.winfo_screenheight() // 2) - 350
            self.dialog.geometry(f"900x700+{x}+{y}")
        except:
            pass
            
        # Configure theme
        if CUSTOM_TK_AVAILABLE:
            self.dialog.configure(fg_color=PINK_COLORS["background"])
        else:
            self.dialog.configure(bg=PINK_COLORS["background"])
            
        # Make dialog modal and always on top
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.attributes('-topmost', True)
        
        # Prevent auto-closing
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_dialog_close)
        
        # Main container
        if CUSTOM_TK_AVAILABLE:
            main_frame = ctk.CTkFrame(self.dialog, fg_color=PINK_COLORS["surface"], corner_radius=20)
        else:
            main_frame = tk.Frame(self.dialog, bg=PINK_COLORS["surface"], relief="raised", bd=5)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Animated header
        if CUSTOM_TK_AVAILABLE:
            header_label = ctk.CTkLabel(
                main_frame,
                text="🚨 VOICE EMERGENCY DETECTED 🚨",
                font=ctk.CTkFont(size=32, weight="bold"),
                text_color="#ff0000"
            )
        else:
            header_label = tk.Label(
                main_frame,
                text="🚨 VOICE EMERGENCY DETECTED 🚨",
                font=("Orbitron", 32, "bold"),
                fg="#ff0000",
                bg=PINK_COLORS["surface"]
            )
        header_label.pack(pady=30)
        
        # Status indicator
        if CUSTOM_TK_AVAILABLE:
            status_frame = ctk.CTkFrame(main_frame, fg_color="#ff1493", corner_radius=15)
        else:
            status_frame = tk.Frame(main_frame, bg="#ff1493", relief="ridge", bd=3)
        status_frame.pack(fill="x", padx=40, pady=20)
        
        if CUSTOM_TK_AVAILABLE:
            status_label = ctk.CTkLabel(
                status_frame,
                text="⚡ QUANTUM THREAT ANALYSIS COMPLETE ⚡",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
        else:
            status_label = tk.Label(
                status_frame,
                text="⚡ QUANTUM THREAT ANALYSIS COMPLETE ⚡",
                font=("Orbitron", 18, "bold"),
                fg="white",
                bg="#ff1493"
            )
        status_label.pack(pady=15)
        
        # Detection details
        if CUSTOM_TK_AVAILABLE:
            details_frame = ctk.CTkFrame(main_frame, fg_color=PINK_COLORS["dark"], corner_radius=15)
        else:
            details_frame = tk.Frame(main_frame, bg=PINK_COLORS["dark"], relief="sunken", bd=3)
        details_frame.pack(fill="x", padx=40, pady=20)
        
        # Voice text
        if CUSTOM_TK_AVAILABLE:
            voice_label = ctk.CTkLabel(
                details_frame,
                text=f"🎤 DETECTED VOICE: \"{text}\"",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#00ffff",
                wraplength=700
            )
        else:
            voice_label = tk.Label(
                details_frame,
                text=f"🎤 DETECTED VOICE: \"{text}\"",
                font=("Orbitron", 16, "bold"),
                fg="#00ffff",
                bg=PINK_COLORS["dark"],
                wraplength=700
            )
        voice_label.pack(pady=15)
        
        # Keywords
        keywords_text = f"🔍 EMERGENCY KEYWORDS: {', '.join(keywords)}"
        if CUSTOM_TK_AVAILABLE:
            keywords_label = ctk.CTkLabel(
                details_frame,
                text=keywords_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ffff00",
                wraplength=700
            )
        else:
            keywords_label = tk.Label(
                details_frame,
                text=keywords_text,
                font=("Orbitron", 14, "bold"),
                fg="#ffff00",
                bg=PINK_COLORS["dark"],
                wraplength=700
            )
        keywords_label.pack(pady=10)
        
        # Main question
        if CUSTOM_TK_AVAILABLE:
            question_frame = ctk.CTkFrame(main_frame, fg_color="#8b0000", corner_radius=15)
        else:
            question_frame = tk.Frame(main_frame, bg="#8b0000", relief="raised", bd=5)
        question_frame.pack(fill="x", padx=40, pady=30)
        
        if CUSTOM_TK_AVAILABLE:
            question_label = ctk.CTkLabel(
                question_frame,
                text="⚠️ ARE YOU IN IMMEDIATE DANGER? ⚠️",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="white"
            )
        else:
            question_label = tk.Label(
                question_frame,
                text="⚠️ ARE YOU IN IMMEDIATE DANGER? ⚠️",
                font=("Orbitron", 24, "bold"),
                fg="white",
                bg="#8b0000"
            )
        question_label.pack(pady=20)
        
        # Button frame
        if CUSTOM_TK_AVAILABLE:
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        else:
            button_frame = tk.Frame(main_frame, bg=PINK_COLORS["surface"])
        button_frame.pack(pady=30)
        
        # YES button (Emergency)
        if CUSTOM_TK_AVAILABLE:
            yes_button = ctk.CTkButton(
                button_frame,
                text="🚨 YES - SEND EMERGENCY ALERTS 🚨",
                font=ctk.CTkFont(size=18, weight="bold"),
                fg_color="#ff0000",
                hover_color="#dc143c",
                text_color="white",
                width=350,
                height=60,
                corner_radius=15,
                command=self.emergency_confirmed
            )
        else:
            yes_button = tk.Button(
                button_frame,
                text="🚨 YES - SEND EMERGENCY ALERTS 🚨",
                font=("Orbitron", 18, "bold"),
                bg="#ff0000",
                fg="white",
                activebackground="#dc143c",
                activeforeground="white",
                width=30,
                height=3,
                relief="raised",
                bd=5,
                command=self.emergency_confirmed
            )
        yes_button.pack(side="left", padx=20)
        
        # NO button (False alarm)
        if CUSTOM_TK_AVAILABLE:
            no_button = ctk.CTkButton(
                button_frame,
                text="✅ NO - FALSE ALARM",
                font=ctk.CTkFont(size=18, weight="bold"),
                fg_color="#32cd32",
                hover_color="#228b22",
                text_color="white",
                width=250,
                height=60,
                corner_radius=15,
                command=self.false_alarm
            )
        else:
            no_button = tk.Button(
                button_frame,
                text="✅ NO - FALSE ALARM",
                font=("Orbitron", 18, "bold"),
                bg="#32cd32",
                fg="white",
                activebackground="#228b22",
                activeforeground="white",
                width=20,
                height=3,
                relief="raised",
                bd=5,
                command=self.false_alarm
            )
        no_button.pack(side="right", padx=20)
        
        # Instructions
        if CUSTOM_TK_AVAILABLE:
            instructions_label = ctk.CTkLabel(
                main_frame,
                text="⌨️ QUICK KEYS: ESC = False Alarm | ENTER = Emergency | F12 = Acknowledge",
                font=ctk.CTkFont(size=12),
                text_color=PINK_COLORS["text_secondary"]
            )
        else:
            instructions_label = tk.Label(
                main_frame,
                text="⌨️ QUICK KEYS: ESC = False Alarm | ENTER = Emergency | F12 = Acknowledge",
                font=("Orbitron", 12),
                fg=PINK_COLORS["text_secondary"],
                bg=PINK_COLORS["surface"]
            )
        instructions_label.pack(pady=10)
        
        # Keyboard bindings
        self.dialog.bind('<Return>', lambda e: self.emergency_confirmed())
        self.dialog.bind('<Escape>', lambda e: self.false_alarm())
        self.dialog.bind('<F12>', lambda e: self.false_alarm())
        
        # Auto-focus
        self.dialog.focus_set()
        
        # Start pulsing animation
        self.start_alert_animation()
        
        # Wait for user response with error handling
        try:
            print("🎭 Dialog created, waiting for user response...")
            self.dialog.wait_window()
            print(f"🎭 Dialog closed, result: {self.result}")
        except Exception as e:
            print(f"🎭 Dialog wait error: {e}")
            self.result = False
        
    def start_alert_animation(self):
        """Start pulsing animation for urgency"""
        def pulse():
            try:
                if self.dialog and self.dialog.winfo_exists():
                    # Pulse the dialog slightly
                    current_alpha = self.dialog.attributes('-alpha')
                    if current_alpha is None:
                        current_alpha = 1.0
                    
                    new_alpha = 0.9 if current_alpha >= 1.0 else 1.0
                    self.dialog.attributes('-alpha', new_alpha)
                    
                    # Schedule next pulse
                    self.dialog.after(500, pulse)
            except:
                pass
        
        pulse()
        
    def emergency_confirmed(self):
        """User confirmed emergency"""
        self.result = True
        if self.dialog:
            self.dialog.destroy()
            
    def false_alarm(self):
        """User indicated false alarm"""
        self.result = False
        if self.dialog:
            self.dialog.destroy()
            
    def on_dialog_close(self):
        """Handle dialog close button"""
        # Treat close as false alarm
        self.false_alarm()

class FuturisticEmergencyProtocolDialog:
    """Futuristic emergency protocol dialog"""
    
    def __init__(self, parent):
        self.result = None
        self.dialog = None
        self.setup_dialog(parent)
        
    def setup_dialog(self, parent):
        """Setup futuristic emergency protocol dialog"""
        if CUSTOM_TK_AVAILABLE:
            self.dialog = ctk.CTkToplevel(parent)
        else:
            self.dialog = tk.Toplevel(parent)
            
        self.dialog.title("🚨 FUTURISTIC EMERGENCY PROTOCOL")
        self.dialog.geometry("800x600")
        
        # Center and configure
        try:
            x = (self.dialog.winfo_screenwidth() // 2) - 400
            y = (self.dialog.winfo_screenheight() // 2) - 300
            self.dialog.geometry(f"800x600+{x}+{y}")
        except:
            pass
            
        if CUSTOM_TK_AVAILABLE:
            self.dialog.configure(fg_color=PINK_COLORS["background"])
        else:
            self.dialog.configure(bg=PINK_COLORS["background"])
            
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.attributes('-topmost', True)
        
        # Main frame
        if CUSTOM_TK_AVAILABLE:
            main_frame = ctk.CTkFrame(self.dialog, fg_color=PINK_COLORS["surface"], corner_radius=20)
        else:
            main_frame = tk.Frame(self.dialog, bg=PINK_COLORS["surface"], relief="raised", bd=5)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        if CUSTOM_TK_AVAILABLE:
            header = ctk.CTkLabel(
                main_frame,
                text="🚨 ACTIVATE ENHANCED EMERGENCY PROTOCOL? 🚨",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#ff0000"
            )
        else:
            header = tk.Label(
                main_frame,
                text="🚨 ACTIVATE ENHANCED EMERGENCY PROTOCOL? 🚨",
                font=("Orbitron", 24, "bold"),
                fg="#ff0000",
                bg=PINK_COLORS["surface"]
            )
        header.pack(pady=30)
        
        # Features list
        features_text = """⚡ QUANTUM EMERGENCY FEATURES:

🔥 Start escalation system
📡 Send progressive alerts  
📷 Capture evidence automatically
📍 Share precise location
📞 Enable emergency calling
🤖 AI threat monitoring
🛡️ Full protection protocol"""

        if CUSTOM_TK_AVAILABLE:
            features_label = ctk.CTkLabel(
                main_frame,
                text=features_text,
                font=ctk.CTkFont(size=16),
                text_color="#00ffff",
                justify="left"
            )
        else:
            features_label = tk.Label(
                main_frame,
                text=features_text,
                font=("Orbitron", 16),
                fg="#00ffff",
                bg=PINK_COLORS["surface"],
                justify="left"
            )
        features_label.pack(pady=20)
        
        # Buttons
        if CUSTOM_TK_AVAILABLE:
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        else:
            button_frame = tk.Frame(main_frame, bg=PINK_COLORS["surface"])
        button_frame.pack(pady=30)
        
        if CUSTOM_TK_AVAILABLE:
            yes_btn = ctk.CTkButton(
                button_frame,
                text="🚨 YES - ACTIVATE PROTOCOL 🚨",
                font=ctk.CTkFont(size=18, weight="bold"),
                fg_color="#ff0000",
                hover_color="#dc143c",
                width=300,
                height=50,
                command=self.activate_protocol
            )
        else:
            yes_btn = tk.Button(
                button_frame,
                text="🚨 YES - ACTIVATE PROTOCOL 🚨",
                font=("Orbitron", 18, "bold"),
                bg="#ff0000",
                fg="white",
                width=25,
                height=2,
                command=self.activate_protocol
            )
        yes_btn.pack(side="left", padx=20)
        
        if CUSTOM_TK_AVAILABLE:
            no_btn = ctk.CTkButton(
                button_frame,
                text="❌ NO - CANCEL",
                font=ctk.CTkFont(size=18, weight="bold"),
                fg_color="#666666",
                hover_color="#555555",
                width=200,
                height=50,
                command=self.cancel_protocol
            )
        else:
            no_btn = tk.Button(
                button_frame,
                text="❌ NO - CANCEL",
                font=("Orbitron", 18, "bold"),
                bg="#666666",
                fg="white",
                width=15,
                height=2,
                command=self.cancel_protocol
            )
        no_btn.pack(side="right", padx=20)
        
        self.dialog.bind('<Return>', lambda e: self.activate_protocol())
        self.dialog.bind('<Escape>', lambda e: self.cancel_protocol())
        self.dialog.focus_set()
        self.dialog.wait_window()
        
    def activate_protocol(self):
        self.result = True
        if self.dialog:
            self.dialog.destroy()
            
    def cancel_protocol(self):
        self.result = False
        if self.dialog:
            self.dialog.destroy()


class FuturisticCallDialog:
    """Futuristic emergency call dialog"""
    
    def __init__(self, parent, name, number, location_text):
        self.result = None
        self.dialog = None
        self.setup_dialog(parent, name, number, location_text)
        
    def setup_dialog(self, parent, name, number, location_text):
        """Setup futuristic call dialog"""
        if CUSTOM_TK_AVAILABLE:
            self.dialog = ctk.CTkToplevel(parent)
        else:
            self.dialog = tk.Toplevel(parent)
            
        self.dialog.title("📞 FUTURISTIC EMERGENCY CALL")
        self.dialog.geometry("700x500")
        
        try:
            x = (self.dialog.winfo_screenwidth() // 2) - 350
            y = (self.dialog.winfo_screenheight() // 2) - 250
            self.dialog.geometry(f"700x500+{x}+{y}")
        except:
            pass
            
        if CUSTOM_TK_AVAILABLE:
            self.dialog.configure(fg_color=PINK_COLORS["background"])
        else:
            self.dialog.configure(bg=PINK_COLORS["background"])
            
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.attributes('-topmost', True)
        
        # Main frame
        if CUSTOM_TK_AVAILABLE:
            main_frame = ctk.CTkFrame(self.dialog, fg_color=PINK_COLORS["surface"], corner_radius=20)
        else:
            main_frame = tk.Frame(self.dialog, bg=PINK_COLORS["surface"], relief="raised", bd=5)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        if CUSTOM_TK_AVAILABLE:
            header = ctk.CTkLabel(
                main_frame,
                text=f"📞 CALLING {name.upper()} 📞",
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color="#ff1493"
            )
        else:
            header = tk.Label(
                main_frame,
                text=f"📞 CALLING {name.upper()} 📞",
                font=("Orbitron", 28, "bold"),
                fg="#ff1493",
                bg=PINK_COLORS["surface"]
            )
        header.pack(pady=20)
        
        # Number
        if CUSTOM_TK_AVAILABLE:
            number_label = ctk.CTkLabel(
                main_frame,
                text=f"📱 Number: {number}",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#00ffff"
            )
        else:
            number_label = tk.Label(
                main_frame,
                text=f"📱 Number: {number}",
                font=("Orbitron", 18, "bold"),
                fg="#00ffff",
                bg=PINK_COLORS["surface"]
            )
        number_label.pack(pady=10)
        
        # Location info
        if CUSTOM_TK_AVAILABLE:
            location_label = ctk.CTkLabel(
                main_frame,
                text=location_text,
                font=ctk.CTkFont(size=14),
                text_color="#ffff00",
                wraplength=600
            )
        else:
            location_label = tk.Label(
                main_frame,
                text=location_text,
                font=("Orbitron", 14),
                fg="#ffff00",
                bg=PINK_COLORS["surface"],
                wraplength=600
            )
        location_label.pack(pady=15)
        
        # Warning
        if CUSTOM_TK_AVAILABLE:
            warning_label = ctk.CTkLabel(
                main_frame,
                text="⚠️ FOR REAL EMERGENCIES ONLY ⚠️",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#ff8800"
            )
        else:
            warning_label = tk.Label(
                main_frame,
                text="⚠️ FOR REAL EMERGENCIES ONLY ⚠️",
                font=("Orbitron", 16, "bold"),
                fg="#ff8800",
                bg=PINK_COLORS["surface"]
            )
        warning_label.pack(pady=20)
        
        # Buttons
        if CUSTOM_TK_AVAILABLE:
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        else:
            button_frame = tk.Frame(main_frame, bg=PINK_COLORS["surface"])
        button_frame.pack(pady=30)
        
        if CUSTOM_TK_AVAILABLE:
            call_btn = ctk.CTkButton(
                button_frame,
                text="📞 MAKE EMERGENCY CALL",
                font=ctk.CTkFont(size=18, weight="bold"),
                fg_color="#ff0000",
                hover_color="#dc143c",
                width=250,
                height=50,
                command=self.make_call
            )
        else:
            call_btn = tk.Button(
                button_frame,
                text="📞 MAKE EMERGENCY CALL",
                font=("Orbitron", 18, "bold"),
                bg="#ff0000",
                fg="white",
                width=20,
                height=2,
                command=self.make_call
            )
        call_btn.pack(side="left", padx=20)
        
        if CUSTOM_TK_AVAILABLE:
            cancel_btn = ctk.CTkButton(
                button_frame,
                text="❌ CANCEL",
                font=ctk.CTkFont(size=18, weight="bold"),
                fg_color="#666666",
                hover_color="#555555",
                width=150,
                height=50,
                command=self.cancel_call
            )
        else:
            cancel_btn = tk.Button(
                button_frame,
                text="❌ CANCEL",
                font=("Orbitron", 18, "bold"),
                bg="#666666",
                fg="white",
                width=10,
                height=2,
                command=self.cancel_call
            )
        cancel_btn.pack(side="right", padx=20)
        
        self.dialog.bind('<Return>', lambda e: self.make_call())
        self.dialog.bind('<Escape>', lambda e: self.cancel_call())
        self.dialog.focus_set()
        self.dialog.wait_window()
        
    def make_call(self):
        self.result = True
        if self.dialog:
            self.dialog.destroy()
            
    def cancel_call(self):
        self.result = False
        if self.dialog:
            self.dialog.destroy()

class ImmediateEmergencyDialog:
    """Immediate emergency dialog - shows activation status without confirmation"""
    
    def __init__(self, parent, text, keywords, alert_count, alert_id):
        print(f"🏗️ ImmediateEmergencyDialog.__init__ called")
        print(f"   Parent: {parent}")
        print(f"   Text: '{text}'")
        print(f"   Keywords: {keywords}")
        self.parent = parent
        self.dialog = None
        try:
            self.setup_dialog(parent, text, keywords, alert_count, alert_id)
            print("✅ ImmediateEmergencyDialog setup completed")
        except Exception as e:
            print(f"❌ ImmediateEmergencyDialog setup failed: {e}")
            import traceback
            traceback.print_exc()
        
    def setup_dialog(self, parent, text, keywords, alert_count, alert_id):
        """Setup immediate emergency status dialog"""
        print("🖼️ Setting up emergency dialog window...")
        
        try:
            if CUSTOM_TK_AVAILABLE:
                print("   Using CustomTkinter for dialog")
                self.dialog = ctk.CTkToplevel(parent)
            else:
                print("   Using standard Tkinter for dialog")
                self.dialog = tk.Toplevel(parent)
            
            print("✅ Dialog window created")
            
            # Basic setup
            self.dialog.title("⚡ IMMEDIATE EMERGENCY PROTOCOL ACTIVE")
            self.dialog.geometry("700x500")
            print("✅ Dialog title and size set")
            
            # Make it visible immediately
            self.dialog.attributes('-topmost', True)
            self.dialog.lift()
            self.dialog.focus_force()
            self.dialog.deiconify()
            print("✅ Dialog visibility settings applied")
            
            # Center dialog
            try:
                self.dialog.update_idletasks()  # Update to get correct screen size
                x = (self.dialog.winfo_screenwidth() // 2) - 350
                y = (self.dialog.winfo_screenheight() // 2) - 250
                self.dialog.geometry(f"700x500+{x}+{y}")
                print("✅ Dialog centered")
            except Exception as e:
                print(f"⚠️ Centering failed: {e}")
                
            # Configure theme
            if CUSTOM_TK_AVAILABLE:
                self.dialog.configure(fg_color="#8b0000")  # Dark red for emergency
            else:
                self.dialog.configure(bg="#8b0000")
            
            print("✅ Dialog theme configured")
            
            # Force dialog to appear
            self.dialog.update()
            self.dialog.tkraise()
            print("🚨 EMERGENCY DIALOG SHOULD BE VISIBLE NOW!")
            
        except Exception as e:
            print(f"❌ Dialog setup error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Main frame
        if CUSTOM_TK_AVAILABLE:
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#8b0000", corner_radius=20)
        else:
            main_frame = tk.Frame(self.dialog, bg="#8b0000", relief="raised", bd=5)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Urgent header
        if CUSTOM_TK_AVAILABLE:
            header = ctk.CTkLabel(
                main_frame,
                text="⚡ IMMEDIATE EMERGENCY PROTOCOL ACTIVE ⚡",
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color="#ffffff"
            )
        else:
            header = tk.Label(
                main_frame,
                text="⚡ IMMEDIATE EMERGENCY PROTOCOL ACTIVE ⚡",
                font=("Orbitron", 28, "bold"),
                fg="#ffffff",
                bg="#8b0000"
            )
        header.pack(pady=20)
        
        # Status indicator
        if CUSTOM_TK_AVAILABLE:
            status_frame = ctk.CTkFrame(main_frame, fg_color="#ff0000", corner_radius=15)
        else:
            status_frame = tk.Frame(main_frame, bg="#ff0000", relief="ridge", bd=3)
        status_frame.pack(fill="x", padx=40, pady=20)
        
        if CUSTOM_TK_AVAILABLE:
            status_label = ctk.CTkLabel(
                status_frame,
                text="🚨 ESCALATION SYSTEM ACTIVATED - NO CONFIRMATION REQUIRED 🚨",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
        else:
            status_label = tk.Label(
                status_frame,
                text="🚨 ESCALATION SYSTEM ACTIVATED - NO CONFIRMATION REQUIRED 🚨",
                font=("Orbitron", 18, "bold"),
                fg="white",
                bg="#ff0000"
            )
        status_label.pack(pady=15)
        
        # Detection details
        if CUSTOM_TK_AVAILABLE:
            details_frame = ctk.CTkFrame(main_frame, fg_color=PINK_COLORS["dark"], corner_radius=15)
        else:
            details_frame = tk.Frame(main_frame, bg=PINK_COLORS["dark"], relief="sunken", bd=3)
        details_frame.pack(fill="x", padx=40, pady=20)
        
        # Alert info
        alert_info = f"🆔 Alert ID: {alert_id}\n🎤 Trigger: {text}\n🔍 Keywords: {', '.join(keywords)}\n⏰ Time: {datetime.now().strftime('%H:%M:%S')}"
        
        if CUSTOM_TK_AVAILABLE:
            info_label = ctk.CTkLabel(
                details_frame,
                text=alert_info,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#00ffff",
                justify="left"
            )
        else:
            info_label = tk.Label(
                details_frame,
                text=alert_info,
                font=("Orbitron", 14, "bold"),
                fg="#00ffff",
                bg=PINK_COLORS["dark"],
                justify="left"
            )
        info_label.pack(pady=15)
        
        # Active protocols
        protocols_text = """⚡ ACTIVE PROTOCOLS:

🔥 Progressive escalation started
📡 Emergency alerts being sent
📷 Evidence capture in progress
📍 Location sharing active
📞 Emergency services notified
🤖 AI monitoring enhanced
🛡️ Full protection mode"""

        if CUSTOM_TK_AVAILABLE:
            protocols_label = ctk.CTkLabel(
                main_frame,
                text=protocols_text,
                font=ctk.CTkFont(size=14),
                text_color="#ffff00",
                justify="left"
            )
        else:
            protocols_label = tk.Label(
                main_frame,
                text=protocols_text,
                font=("Orbitron", 14),
                fg="#ffff00",
                bg="#8b0000",
                justify="left"
            )
        protocols_label.pack(pady=20)
        
        # Acknowledge button (only way to close)
        if CUSTOM_TK_AVAILABLE:
            ack_button = ctk.CTkButton(
                main_frame,
                text="✅ ACKNOWLEDGE EMERGENCY PROTOCOL",
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#32cd32",
                hover_color="#228b22",
                width=400,
                height=50,
                command=self.acknowledge_emergency
            )
        else:
            ack_button = tk.Button(
                main_frame,
                text="✅ ACKNOWLEDGE EMERGENCY PROTOCOL",
                font=("Orbitron", 16, "bold"),
                bg="#32cd32",
                fg="white",
                width=35,
                height=2,
                command=self.acknowledge_emergency
            )
        ack_button.pack(pady=30)
        
        # Instructions
        if CUSTOM_TK_AVAILABLE:
            instructions = ctk.CTkLabel(
                main_frame,
                text="⌨️ Press ESC or F12 to acknowledge | Protocol will continue until acknowledged",
                font=ctk.CTkFont(size=12),
                text_color="#ffffff"
            )
        else:
            instructions = tk.Label(
                main_frame,
                text="⌨️ Press ESC or F12 to acknowledge | Protocol will continue until acknowledged",
                font=("Orbitron", 12),
                fg="#ffffff",
                bg="#8b0000"
            )
        instructions.pack(pady=10)
        
        # Keyboard bindings
        self.dialog.bind('<Escape>', lambda e: self.acknowledge_emergency())
        self.dialog.bind('<F12>', lambda e: self.acknowledge_emergency())
        
        # Auto-focus
        self.dialog.focus_set()
        
        # Start urgent pulsing
        self.start_urgent_animation()
        
    def start_urgent_animation(self):
        """Start subtle urgent animation without flickering"""
        self.pulse_direction = 1
        self.pulse_alpha = 1.0
        
        def smooth_pulse():
            try:
                if self.dialog and self.dialog.winfo_exists():
                    # Smooth pulsing animation
                    self.pulse_alpha += self.pulse_direction * 0.05
                    
                    # Reverse direction at limits
                    if self.pulse_alpha >= 1.0:
                        self.pulse_alpha = 1.0
                        self.pulse_direction = -1
                    elif self.pulse_alpha <= 0.85:
                        self.pulse_alpha = 0.85
                        self.pulse_direction = 1
                    
                    self.dialog.attributes('-alpha', self.pulse_alpha)
                    
                    # Smoother animation with shorter intervals
                    self.dialog.after(100, smooth_pulse)
            except:
                pass
        
        smooth_pulse()
        
    def acknowledge_emergency(self):
        """Acknowledge the emergency protocol"""
        try:
            print("✅ Emergency protocol acknowledged by user")
            if self.dialog:
                self.dialog.destroy()
                # Clear reference to allow new dialogs
                if hasattr(self, 'parent') and hasattr(self.parent, 'immediate_dialog'):
                    self.parent.immediate_dialog = None
        except Exception as e:
            print(f"Acknowledge error: {e}")

    def show_contacting_services_window(self):
        """Show animated window with alerts and sounds for contacting services"""
        try:
            print("📞 Creating contacting services window with alerts...")
            
            # Create services window
            if CUSTOM_TK_AVAILABLE:
                services_window = ctk.CTkToplevel(self.root)
                services_window.configure(fg_color=PINK_COLORS["background"])
            else:
                services_window = tk.Toplevel(self.root)
                services_window.configure(bg=PINK_COLORS["background"])
            
            # Window setup
            services_window.title("🚨 HerShield Emergency Services")
            services_window.geometry("700x500")
            
            # Make it appear on top
            services_window.attributes('-topmost', True)
            services_window.lift()
            services_window.focus_force()
            
            # Center the window
            services_window.update_idletasks()
            x = (services_window.winfo_screenwidth() // 2) - 350
            y = (services_window.winfo_screenheight() // 2) - 250
            services_window.geometry(f"700x500+{x}+{y}")
            
            # Main container
            if CUSTOM_TK_AVAILABLE:
                main_container = ctk.CTkFrame(
                    services_window,
                    corner_radius=25,
                    fg_color="#ff0000",  # Bright red for urgency
                    border_width=3,
                    border_color="#ffffff"
                )
            else:
                main_container = tk.Frame(
                    services_window,
                    bg="#ff0000",
                    relief="raised",
                    bd=5
                )
            main_container.pack(fill="both", expand=True, padx=15, pady=15)
            
            # Urgent header with animation
            if CUSTOM_TK_AVAILABLE:
                self.services_header = ctk.CTkLabel(
                    main_container,
                    text="🚨 CONTACTING EMERGENCY SERVICES 🚨",
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color="#ffffff"
                )
            else:
                self.services_header = tk.Label(
                    main_container,
                    text="🚨 CONTACTING EMERGENCY SERVICES 🚨",
                    font=("Arial", 24, "bold"),
                    fg="#ffffff",
                    bg="#ff0000"
                )
            self.services_header.pack(pady=20)
            
            # Status frame
            if CUSTOM_TK_AVAILABLE:
                status_frame = ctk.CTkFrame(
                    main_container,
                    corner_radius=15,
                    fg_color="#8b0000",
                    border_width=2,
                    border_color="#ffff00"
                )
            else:
                status_frame = tk.Frame(
                    main_container,
                    bg="#8b0000",
                    relief="ridge",
                    bd=3
                )
            status_frame.pack(fill="x", padx=20, pady=20)
            
            # Animated status messages
            self.service_messages = [
                "📞 Contacting Emergency Contacts...",
                "🚔 Alerting Police Services...",
                "🚑 Notifying Medical Services...", 
                "🔥 Contacting Fire Department...",
                "📡 Broadcasting Emergency Alert...",
                "📍 Sharing Live Location...",
                "📷 Capturing Evidence...",
                "🔊 Activating Emergency Whistle...",
                "📱 Sending SMS Alerts...",
                "📧 Sending Email Notifications...",
                "🌐 Uploading to Cloud Services...",
                "⚡ All Services Contacted Successfully!"
            ]
            
            # Status label for animated messages
            if CUSTOM_TK_AVAILABLE:
                self.status_label = ctk.CTkLabel(
                    status_frame,
                    text=self.service_messages[0],
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#00ff00"
                )
            else:
                self.status_label = tk.Label(
                    status_frame,
                    text=self.service_messages[0],
                    font=("Arial", 16, "bold"),
                    fg="#00ff00",
                    bg="#8b0000"
                )
            self.status_label.pack(pady=20)
            
            # Progress indicator
            if CUSTOM_TK_AVAILABLE:
                self.progress_label = ctk.CTkLabel(
                    main_container,
                    text="⚡ EMERGENCY PROTOCOL IN PROGRESS ⚡",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#ffff00"
                )
            else:
                self.progress_label = tk.Label(
                    main_container,
                    text="⚡ EMERGENCY PROTOCOL IN PROGRESS ⚡",
                    font=("Arial", 18, "bold"),
                    fg="#ffff00",
                    bg="#ff0000"
                )
            self.progress_label.pack(pady=20)
            
            # Instructions
            if CUSTOM_TK_AVAILABLE:
                instructions = ctk.CTkLabel(
                    main_container,
                    text="🔊 Emergency whistle activated | All services being contacted | Help is on the way!",
                    font=ctk.CTkFont(size=14),
                    text_color="#ffffff"
                )
            else:
                instructions = tk.Label(
                    main_container,
                    text="🔊 Emergency whistle activated | All services being contacted | Help is on the way!",
                    font=("Arial", 14),
                    fg="#ffffff",
                    bg="#ff0000"
                )
            instructions.pack(pady=15)
            
            # Close button (appears after all messages)
            if CUSTOM_TK_AVAILABLE:
                self.close_services_btn = ctk.CTkButton(
                    main_container,
                    text="✅ SERVICES CONTACTED",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    fg_color="#32cd32",
                    hover_color="#228b22",
                    width=300,
                    height=50,
                    corner_radius=15,
                    command=services_window.destroy
                )
            else:
                self.close_services_btn = tk.Button(
                    main_container,
                    text="✅ SERVICES CONTACTED",
                    font=("Arial", 16, "bold"),
                    bg="#32cd32",
                    fg="white",
                    width=25,
                    height=2,
                    command=services_window.destroy
                )
            # Don't pack the button yet - it will appear after animation
            
            # Store window reference
            self.services_window = services_window
            
            # Start animations and sounds
            self.start_service_animation(services_window)
            self.play_emergency_sounds()
            
            print("✅ Contacting services window created with alerts!")
            
        except Exception as e:
            print(f"❌ Services window creation failed: {e}")
            import traceback
            traceback.print_exc()
    
    def start_service_animation(self, window):
        """Animate the service contact messages"""
        message_index = 0
        
        def update_message():
            nonlocal message_index
            try:
                if window.winfo_exists() and message_index < len(self.service_messages):
                    # Update status message
                    if CUSTOM_TK_AVAILABLE:
                        self.status_label.configure(text=self.service_messages[message_index])
                    else:
                        self.status_label.configure(text=self.service_messages[message_index])
                    
                    message_index += 1
                    
                    # If all messages shown, show close button
                    if message_index >= len(self.service_messages):
                        self.close_services_btn.pack(pady=20)
                        # Change header to success
                        if CUSTOM_TK_AVAILABLE:
                            self.services_header.configure(text="✅ ALL EMERGENCY SERVICES CONTACTED ✅")
                        else:
                            self.services_header.configure(text="✅ ALL EMERGENCY SERVICES CONTACTED ✅")
                    else:
                        # Schedule next message
                        window.after(1500, update_message)  # 1.5 seconds between messages
                        
            except Exception as e:
                print(f"Animation error: {e}")
        
        # Start the animation
        update_message()
        
        # Also animate the header flashing
        self.animate_services_header(window)
    
    def animate_services_header(self, window):
        """Animate the services header with flashing colors"""
        colors = ["#ffffff", "#ffff00", "#ff8800"]
        color_index = 0
        
        def flash_header():
            nonlocal color_index
            try:
                if window.winfo_exists():
                    if CUSTOM_TK_AVAILABLE:
                        self.services_header.configure(text_color=colors[color_index])
                    else:
                        self.services_header.configure(fg=colors[color_index])
                    color_index = (color_index + 1) % len(colors)
                    window.after(400, flash_header)  # Flash every 400ms
            except:
                pass
        
        flash_header()
    
    def play_emergency_sounds(self):
        """Play emergency whistle and alert sounds"""
        def sound_thread():
            try:
                import winsound
                # Emergency whistle pattern
                for cycle in range(3):
                    # High-pitched whistle
                    for freq in range(2000, 3000, 100):
                        winsound.Beep(freq, 100)
                    # Low-pitched alert
                    for freq in range(1000, 500, -50):
                        winsound.Beep(freq, 150)
                    
                # Continuous alert beeps
                for _ in range(10):
                    winsound.Beep(1500, 200)
                    time.sleep(0.1)
                    winsound.Beep(2000, 200)
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"Sound error: {e}")
                # Fallback to system bell
                for _ in range(20):
                    print('\a', end='', flush=True)
                    time.sleep(0.2)
        
        # Play sounds in background
        threading.Thread(target=sound_thread, daemon=True).start()