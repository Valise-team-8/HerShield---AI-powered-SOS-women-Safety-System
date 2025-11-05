#!/usr/bin/env python3
"""
HerShield Setup - Quick Configuration
"""

import json
import os
import getpass
import smtplib

def test_email(smtp_server, username, password):
    """Test email credentials"""
    try:
        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()
        server.login(username, password)
        server.quit()
        return True, "✅ Email working"
    except Exception as e:
        return False, f"❌ Email failed: {str(e)[:50]}"

def setup():
    """Quick setup"""
    print("🛡️ HerShield Setup")
    print("=" * 25)
    
    # User info
    name = input("Name: ").strip() or "User"
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()
    
    # Emergency contacts
    print("\nEmergency Contacts:")
    contacts = []
    for i in range(3):
        contact = input(f"Contact {i+1}: ").strip()
        if contact:
            contacts.append(contact)
    
    if not contacts:
        contacts = ["+1234567890", "+0987654321"]
        print("Using default test contacts")
    
    # Email setup
    print("\nEmail Setup:")
    provider = input("Provider (gmail/outlook): ").strip().lower()
    
    if provider == "gmail":
        smtp_server = "smtp.gmail.com"
        print("📝 For Gmail: Use App Password (not regular password)")
        print("   Settings → Security → 2-Step Verification → App passwords")
    elif provider == "outlook":
        smtp_server = "smtp-mail.outlook.com"
    else:
        smtp_server = input("SMTP server: ").strip() or "smtp.gmail.com"
    
    username = input(f"Username ({email}): ").strip() or email
    password = getpass.getpass("Password: ")
    
    # Test email
    print("\n🧪 Testing email...")
    success, message = test_email(smtp_server, username, password)
    print(message)
    
    if not success:
        if input("Continue anyway? (y/n): ").lower() != 'y':
            return False
    
    # Save config
    os.makedirs("data", exist_ok=True)
    
    keywords = [
        "help", "save me", "emergency", "police", "fire", "ambulance",
        "attack", "assault", "violence", "danger", "gun", "knife", 
        "hurt", "scared", "trapped", "bleeding", "stop hitting",
        "rape", "kidnap", "abuse", "threat", "weapon", "pain"
    ]
    
    config = {
        "user": {
            "name": name,
            "email": email,
            "phone": phone,
            "contacts": contacts
        },
        "email": {
            "smtp_server": smtp_server,
            "username": username,
            "password": password
        },
        "keywords": keywords
    }
    
    with open("data/config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Setup complete!")
    print("🚀 Run: python hershield.py")
    return True

if __name__ == "__main__":
    setup()