#!/usr/bin/env python3
"""
Simple dialog test to see if emergency dialogs work
"""

import tkinter as tk
try:
    import customtkinter as ctk
    CUSTOM_TK_AVAILABLE = True
    ctk.set_appearance_mode("dark")
except ImportError:
    ctk = tk
    CUSTOM_TK_AVAILABLE = False

def test_emergency_dialog():
    """Test emergency dialog creation"""
    print("🧪 Testing Emergency Dialog Creation")
    
    if CUSTOM_TK_AVAILABLE:
        root = ctk.CTk()
        print("✅ CustomTkinter root created")
    else:
        root = tk.Tk()
        print("✅ Tkinter root created")
    
    root.title("Test Root")
    root.geometry("300x200")
    
    def create_dialog():
        print("🚨 Creating emergency dialog...")
        try:
            if CUSTOM_TK_AVAILABLE:
                dialog = ctk.CTkToplevel(root)
                print("✅ CTkToplevel created")
            else:
                dialog = tk.Toplevel(root)
                print("✅ Toplevel created")
            
            dialog.title("⚡ EMERGENCY PROTOCOL ACTIVE")
            dialog.geometry("600x400")
            print("✅ Dialog configured")
            
            # Make it visible
            dialog.attributes('-topmost', True)
            dialog.lift()
            dialog.focus_force()
            dialog.deiconify()
            print("✅ Dialog visibility set")
            
            # Add content
            if CUSTOM_TK_AVAILABLE:
                label = ctk.CTkLabel(dialog, text="🚨 EMERGENCY DIALOG TEST", 
                                   font=ctk.CTkFont(size=20, weight="bold"))
                label.pack(pady=50)
                
                button = ctk.CTkButton(dialog, text="✅ CLOSE", 
                                     command=dialog.destroy)
                button.pack(pady=20)
            else:
                label = tk.Label(dialog, text="🚨 EMERGENCY DIALOG TEST", 
                               font=("Arial", 20, "bold"))
                label.pack(pady=50)
                
                button = tk.Button(dialog, text="✅ CLOSE", 
                                 command=dialog.destroy)
                button.pack(pady=20)
            
            print("✅ Dialog content added")
            print("🖥️ Dialog should be visible now!")
            
        except Exception as e:
            print(f"❌ Dialog creation failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Add test button
    if CUSTOM_TK_AVAILABLE:
        test_btn = ctk.CTkButton(root, text="🚨 Create Emergency Dialog", 
                               command=create_dialog)
    else:
        test_btn = tk.Button(root, text="🚨 Create Emergency Dialog", 
                           command=create_dialog)
    test_btn.pack(pady=50)
    
    print("🖥️ Test window ready - click button to test dialog")
    root.mainloop()

if __name__ == "__main__":
    test_emergency_dialog()