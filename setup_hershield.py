#!/usr/bin/env python3
"""
HerShield Setup Script - Install all dependencies
Run this on a new laptop to set up HerShield
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    print("🛡️ HerShield Setup - Installing Dependencies...")
    print("=" * 50)
    
    # Essential packages for HerShield
    packages = [
        "pygame>=2.5.0",
        "speechrecognition>=3.10.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "customtkinter==5.2.2",  # Specific version to avoid issues
        "pillow>=10.0.0",
        "pyttsx3>=2.90",
        "plyer>=2.1.0",
        "requests>=2.31.0",
        "geocoder>=1.38.1",
        "python-dotenv>=1.0.0",
        "cryptography>=41.0.0"
    ]
    
    # Optional packages (won't fail if they don't install)
    optional_packages = [
        "pyaudio>=0.2.11",  # Might need system dependencies
        "firebase-admin>=6.2.0",
        "google-cloud-firestore>=2.11.0",
        "sounddevice>=0.4.6",
        "librosa>=0.10.0",
        "folium>=0.14.0"
    ]
    
    print("Installing essential packages...")
    failed_essential = []
    for package in packages:
        if not install_package(package):
            failed_essential.append(package)
    
    print("\nInstalling optional packages...")
    failed_optional = []
    for package in optional_packages:
        if not install_package(package):
            failed_optional.append(package)
    
    print("\n" + "=" * 50)
    print("🛡️ HerShield Setup Complete!")
    
    if not failed_essential:
        print("✅ All essential packages installed successfully!")
        print("🚀 You can now run: python main.py")
    else:
        print("❌ Some essential packages failed to install:")
        for pkg in failed_essential:
            print(f"   - {pkg}")
        print("\nTry installing them manually:")
        for pkg in failed_essential:
            print(f"   pip install {pkg}")
    
    if failed_optional:
        print("\n⚠️ Optional packages that failed (HerShield will still work):")
        for pkg in failed_optional:
            print(f"   - {pkg}")
    
    print("\n🔧 If you get 'CTkFrame' errors, run:")
    print("   pip uninstall customtkinter")
    print("   pip install customtkinter==5.2.2")

if __name__ == "__main__":
    main()