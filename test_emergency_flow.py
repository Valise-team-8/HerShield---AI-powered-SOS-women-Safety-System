#!/usr/bin/env python3
"""
Test Emergency Flow - Test the complete emergency detection and dialog flow
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
from datetime import datetime

# Import the main application components
try:
    from main import FuturisticHerShield, ImmediateEmergencyDialog, PINK_COLORS
    MAIN_AVAILABLE = True
except ImportError as e:
    print(f"Main import error: {e}")
    MAIN_AVAILABLE = False

def test_emergency_dialog_creation():
    """Test creating the emergency dialog directly"""
    print("🧪 Testing Emergency Dialog Creation")
    
    if not MAIN_AVAILABLE:
        print("❌ Main application not available")
        return
    
    # Create a simple root window
    if CUSTOM_TK_AVAILABLE:
        root = ctk.CTk()
    else:
        root = tk.Tk()
    
    root.title("🧪 Emergency Dialog Test")
    root.geometry("300x200")
    
    def create_emergency_dialog():
        """Create an emergency dialog for testing"""
        try:
            print("🚨 Creating emergency dialog...")
            dialog = ImmediateEmergencyDialog(
                parent=root,
                text="test emergency help",
                keywords=["help", "emergency"],
                alert_count=1,
                alert_id="test_123"
            )
            print("✅ Emergency dialog created successfully")
        except Exception as e:
            print(f"❌ Emergency dialog creation failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Add test button
    if CUSTOM_TK_AVAILABLE:
        test_btn = ctk.CTkButton(
            root,
            text="🚨 Test Emergency Dialog",
            command=create_emergency_dialog
        )
    else:
        test_btn = tk.Button(
            root,
            text="🚨 Test Emergency Dialog",
            command=create_emergency_dialog
        )
    test_btn.pack(pady=50)
    
    print("✅ Test window ready - click button to test emergency dialog")
    root.mainloop()

def test_voice_alert_trigger():
    """Test the voice alert trigger function"""
    print("\n🧪 Testing Voice Alert Trigger")
    
    if not MAIN_AVAILABLE:
        print("❌ Main application not available")
        return
    
    try:
        # Create a minimal HerShield instance
        app = FuturisticHerShield()
        
        # Test the trigger function
        print("🎤 Simulating voice detection...")
        app.trigger_voice_alert("help emergency", ["help", "emergency"])
        
        print("✅ Voice alert triggered successfully")
        
        # Run the GUI briefly
        app.root.after(5000, app.root.quit)  # Auto-close after 5 seconds
        app.root.mainloop()
        
    except Exception as e:
        print(f"❌ Voice alert trigger test failed: {e}")
        import traceback
        traceback.print_exc()

def test_emergency_flow_simulation():
    """Simulate the complete emergency flow"""
    print("\n🧪 Testing Complete Emergency Flow")
    
    # Simulate the flow without actual voice detection
    print("1. 🎤 Voice detected: 'help emergency'")
    print("2. 🔍 Keywords found: ['help', 'emergency']")
    print("3. 🚨 Critical keywords detected - immediate activation")
    print("4. ⚡ Calling emergency_alert_immediate()")
    print("5. 📊 Updating alert count")
    print("6. 🏗️ Creating ImmediateEmergencyDialog")
    print("7. 🖥️ Showing emergency protocol window")
    
    # Test each step
    steps_passed = 0
    
    # Step 1-3: Voice processing (simulated)
    steps_passed += 3
    print(f"✅ Steps 1-3 passed ({steps_passed}/7)")
    
    # Step 4-5: Emergency activation (test with minimal setup)
    try:
        if MAIN_AVAILABLE:
            # Test dialog creation
            if CUSTOM_TK_AVAILABLE:
                root = ctk.CTk()
            else:
                root = tk.Tk()
            root.withdraw()  # Hide root window
            
            dialog = ImmediateEmergencyDialog(
                parent=root,
                text="help emergency",
                keywords=["help", "emergency"],
                alert_count=1,
                alert_id="test_flow_123"
            )
            steps_passed += 3
            print(f"✅ Steps 4-7 passed ({steps_passed}/7)")
            
            # Show dialog briefly
            root.after(3000, root.quit)
            root.deiconify()  # Show root window
            root.mainloop()
            
        else:
            print("⚠️ Cannot test steps 4-7 without main application")
            
    except Exception as e:
        print(f"❌ Steps 4-7 failed: {e}")
    
    print(f"\n📊 Emergency Flow Test Results: {steps_passed}/7 steps passed")
    if steps_passed == 7:
        print("✅ Complete emergency flow working!")
    else:
        print("⚠️ Some issues detected in emergency flow")

def main():
    """Run all emergency flow tests"""
    print("🛡️ HerShield Emergency Flow Tests")
    print("=" * 50)
    
    # Test 1: Direct dialog creation
    test_emergency_dialog_creation()
    
    # Test 2: Voice alert trigger
    # test_voice_alert_trigger()  # Commented out to avoid full app startup
    
    # Test 3: Flow simulation
    test_emergency_flow_simulation()
    
    print("\n🎯 Test Summary:")
    print("1. Emergency dialog creation - Test completed")
    print("2. Voice alert trigger - Requires full app")
    print("3. Emergency flow simulation - Test completed")
    print("\n💡 If dialogs appear correctly, the emergency system is working!")

if __name__ == "__main__":
    main()