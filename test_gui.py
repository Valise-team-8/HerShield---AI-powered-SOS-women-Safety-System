#!/usr/bin/env python3
"""
Test GUI - Check if the main window appears
"""

import tkinter as tk
try:
    import customtkinter as ctk
    CUSTOM_TK_AVAILABLE = True
    ctk.set_appearance_mode("dark")
except ImportError:
    ctk = tk
    CUSTOM_TK_AVAILABLE = False

def test_gui():
    """Test basic GUI functionality"""
    print("🖥️ Testing GUI...")
    
    if CUSTOM_TK_AVAILABLE:
        root = ctk.CTk()
        print("✅ CustomTkinter window created")
    else:
        root = tk.Tk()
        print("✅ Tkinter window created")
    
    root.title("🛡️ HerShield Test")
    root.geometry("600x400")
    
    # Center window
    try:
        x = (root.winfo_screenwidth() // 2) - 300
        y = (root.winfo_screenheight() // 2) - 200
        root.geometry(f"600x400+{x}+{y}")
        print("✅ Window centered")
    except Exception as e:
        print(f"⚠️ Centering failed: {e}")
    
    # Add test content
    if CUSTOM_TK_AVAILABLE:
        label = ctk.CTkLabel(root, text="🛡️ HerShield GUI Test", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=50)
        
        button = ctk.CTkButton(root, text="✅ GUI Working!", font=ctk.CTkFont(size=16), 
                              command=lambda: print("Button clicked!"))
        button.pack(pady=20)
    else:
        label = tk.Label(root, text="🛡️ HerShield GUI Test", font=("Arial", 24, "bold"))
        label.pack(pady=50)
        
        button = tk.Button(root, text="✅ GUI Working!", font=("Arial", 16), 
                          command=lambda: print("Button clicked!"))
        button.pack(pady=20)
    
    print("🖥️ Starting GUI mainloop...")
    root.mainloop()
    print("🛑 GUI closed")

if __name__ == "__main__":
    test_gui()