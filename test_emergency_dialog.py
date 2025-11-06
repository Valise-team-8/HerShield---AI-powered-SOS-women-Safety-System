#!/usr/bin/env python3
"""
Test Emergency Dialog - Check if the dialog appears without flickering
"""

import tkinter as tk
try:
    import customtkinter as ctk
    CUSTOM_TK_AVAILABLE = True
    ctk.set_appearance_mode("dark")
except ImportError:
    ctk = tk
    CUSTOM_TK_AVAILABLE = False

from datetime import datetime

# Pink color palette
PINK_COLORS = {
    "primary": "#ff1493",
    "secondary": "#ff69b4", 
    "accent": "#ffc0cb",
    "dark": "#8b008b",
    "background": "#1a0d1a",
    "surface": "#2d1b2d",
    "text": "#ffffff",
    "text_secondary": "#ffb3d9"
}

class TestEmergencyDialog:
    """Test emergency dialog without flickering"""
    
    def __init__(self, parent):
        self.dialog = None
        self.setup_dialog(parent)
        
    def setup_dialog(self, parent):
        """Setup smooth emergency dialog"""
        if CUSTOM_TK_AVAILABLE:
            self.dialog = ctk.CTkToplevel(parent)
        else:
            self.dialog = tk.Toplevel(parent)
            
        self.dialog.title("⚡ EMERGENCY PROTOCOL TEST")
        self.dialog.geometry("700x500")
        
        # Center dialog
        try:
            x = (self.dialog.winfo_screenwidth() // 2) - 350
            y = (self.dialog.winfo_screenheight() // 2) - 250
            self.dialog.geometry(f"700x500+{x}+{y}")
        except:
            pass
            
        # Configure theme
        if CUSTOM_TK_AVAILABLE:
            self.dialog.configure(fg_color=PINK_COLORS["background"])
        else:
            self.dialog.configure(bg=PINK_COLORS["background"])
            
        # Make dialog always on top
        self.dialog.attributes('-topmost', True)
        
        # Main frame
        if CUSTOM_TK_AVAILABLE:
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#8b0000", corner_radius=20)
        else:
            main_frame = tk.Frame(self.dialog, bg="#8b0000", relief="raised", bd=5)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        if CUSTOM_TK_AVAILABLE:
            self.header = ctk.CTkLabel(
                main_frame,
                text="⚡ EMERGENCY PROTOCOL ACTIVE ⚡",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#ffffff"
            )
        else:
            self.header = tk.Label(
                main_frame,
                text="⚡ EMERGENCY PROTOCOL ACTIVE ⚡",
                font=("Arial", 24, "bold"),
                fg="#ffffff",
                bg="#8b0000"
            )
        self.header.pack(pady=20)
        
        # Status
        if CUSTOM_TK_AVAILABLE:
            status_frame = ctk.CTkFrame(main_frame, fg_color="#ff0000", corner_radius=15)
        else:
            status_frame = tk.Frame(main_frame, bg="#ff0000", relief="ridge", bd=3)
        status_frame.pack(fill="x", padx=40, pady=20)
        
        if CUSTOM_TK_AVAILABLE:
            status_label = ctk.CTkLabel(
                status_frame,
                text="🚨 SMOOTH ANIMATION TEST - NO FLICKERING 🚨",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white"
            )
        else:
            status_label = tk.Label(
                status_frame,
                text="🚨 SMOOTH ANIMATION TEST - NO FLICKERING 🚨",
                font=("Arial", 16, "bold"),
                fg="white",
                bg="#ff0000"
            )
        status_label.pack(pady=15)
        
        # Test info
        test_info = f"""🧪 TEST DETAILS:
        
Time: {datetime.now().strftime('%H:%M:%S')}
Animation: Smooth pulsing (no harsh flashing)
Alpha: Gradual transition from 0.85 to 1.0
Update Rate: Every 100ms for smoothness

This dialog should pulse gently without flickering."""

        if CUSTOM_TK_AVAILABLE:
            info_label = ctk.CTkLabel(
                main_frame,
                text=test_info,
                font=ctk.CTkFont(size=12),
                text_color="#ffff00",
                justify="left"
            )
        else:
            info_label = tk.Label(
                main_frame,
                text=test_info,
                font=("Arial", 12),
                fg="#ffff00",
                bg="#8b0000",
                justify="left"
            )
        info_label.pack(pady=20)
        
        # Close button
        if CUSTOM_TK_AVAILABLE:
            close_button = ctk.CTkButton(
                main_frame,
                text="✅ CLOSE TEST",
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#32cd32",
                hover_color="#228b22",
                width=200,
                height=50,
                command=self.close_dialog
            )
        else:
            close_button = tk.Button(
                main_frame,
                text="✅ CLOSE TEST",
                font=("Arial", 16, "bold"),
                bg="#32cd32",
                fg="white",
                width=15,
                height=2,
                command=self.close_dialog
            )
        close_button.pack(pady=30)
        
        # Start smooth animation
        self.start_smooth_animation()
        
    def start_smooth_animation(self):
        """Start smooth pulsing animation"""
        self.pulse_direction = 1
        self.pulse_alpha = 1.0
        
        def smooth_pulse():
            try:
                if self.dialog and self.dialog.winfo_exists():
                    # Very smooth pulsing
                    self.pulse_alpha += self.pulse_direction * 0.02  # Smaller steps
                    
                    # Reverse direction at limits
                    if self.pulse_alpha >= 1.0:
                        self.pulse_alpha = 1.0
                        self.pulse_direction = -1
                    elif self.pulse_alpha <= 0.9:  # Less dramatic range
                        self.pulse_alpha = 0.9
                        self.pulse_direction = 1
                    
                    self.dialog.attributes('-alpha', self.pulse_alpha)
                    
                    # Smooth 60fps-like animation
                    self.dialog.after(50, smooth_pulse)
            except:
                pass
        
        smooth_pulse()
        
    def close_dialog(self):
        """Close the test dialog"""
        try:
            if self.dialog:
                self.dialog.destroy()
        except Exception as e:
            print(f"Close error: {e}")

def test_emergency_dialog():
    """Test the emergency dialog"""
    print("🧪 Testing Emergency Dialog Animation")
    
    if CUSTOM_TK_AVAILABLE:
        root = ctk.CTk()
    else:
        root = tk.Tk()
    
    root.title("🛡️ Emergency Dialog Test")
    root.geometry("400x200")
    
    # Center main window
    try:
        x = (root.winfo_screenwidth() // 2) - 200
        y = (root.winfo_screenheight() // 2) - 100
        root.geometry(f"400x200+{x}+{y}")
    except:
        pass
    
    if CUSTOM_TK_AVAILABLE:
        root.configure(fg_color=PINK_COLORS["background"])
        
        title = ctk.CTkLabel(root, text="🛡️ HerShield Dialog Test", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=30)
        
        test_btn = ctk.CTkButton(root, text="🧪 Test Emergency Dialog", 
                                font=ctk.CTkFont(size=14),
                                command=lambda: TestEmergencyDialog(root))
        test_btn.pack(pady=20)
    else:
        root.configure(bg=PINK_COLORS["background"])
        
        title = tk.Label(root, text="🛡️ HerShield Dialog Test", 
                        font=("Arial", 20, "bold"), fg="white", bg=PINK_COLORS["background"])
        title.pack(pady=30)
        
        test_btn = tk.Button(root, text="🧪 Test Emergency Dialog", 
                            font=("Arial", 14),
                            command=lambda: TestEmergencyDialog(root))
        test_btn.pack(pady=20)
    
    print("✅ Test window ready - click button to test emergency dialog")
    root.mainloop()

if __name__ == "__main__":
    test_emergency_dialog()