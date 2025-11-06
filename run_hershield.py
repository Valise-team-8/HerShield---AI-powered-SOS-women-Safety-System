#!/usr/bin/env python3
"""
HerShield Enhanced Launcher
Launch the futuristic women safety application with all enhanced features
"""

import sys
import os
from pathlib import Path

def main():
    """Launch HerShield Enhanced"""
    print("🛡️ Starting HerShield Enhanced - AI-Powered Women Safety System")
    print("=" * 60)
    print("🎀 Futuristic Pink Theme")
    print("🤖 AI Threat Detection") 
    print("🔔 Progressive Escalation System")
    print("📡 Offline Alert Broadcasting")
    print("📷 Automatic Evidence Capture")
    print("⌨️  Quick Acknowledge (ESC, Ctrl+Shift+A, F12)")
    print("=" * 60)
    
    try:
        # Import and run the futuristic application
        from main import main as futuristic_main
        futuristic_main()
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Application Error: {e}")
        print("Please check the system requirements and try again.")

if __name__ == "__main__":
    main()