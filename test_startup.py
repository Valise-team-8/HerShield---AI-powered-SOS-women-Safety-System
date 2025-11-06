#!/usr/bin/env python3
"""
Quick startup test for HerShield
"""

print("🔍 Testing HerShield startup...")

try:
    print("1. Testing basic imports...")
    import tkinter as tk
    print("   ✅ tkinter OK")
    
    import customtkinter as ctk
    print("   ✅ customtkinter OK")
    
    import pygame
    print("   ✅ pygame OK")
    
    print("2. Testing core modules...")
    from core.firebase_service import initialize_firebase
    print("   ✅ firebase_service OK")
    
    from core.user_config import user_config
    print("   ✅ user_config OK")
    
    from core.escalation_system import escalation_system
    print("   ✅ escalation_system OK")
    
    print("3. Testing Firebase initialization...")
    firebase_result = initialize_firebase()
    if firebase_result:
        print("   ✅ Firebase connected")
    else:
        print("   ⚠️ Firebase using local mode")
    
    print("4. Testing main app import...")
    # Don't actually run the GUI, just test if it imports
    import futuristic_hershield
    print("   ✅ Main app imports OK")
    
    print("\n🎉 All tests passed! HerShield should start properly.")
    print("Run: python futuristic_hershield.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()