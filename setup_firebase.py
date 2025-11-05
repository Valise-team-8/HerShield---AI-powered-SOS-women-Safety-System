#!/usr/bin/env python3
"""
Firebase Setup Helper for HerShield
Helps you connect your Firebase account to the project
"""

import os
import json
import sys
from pathlib import Path

def check_firebase_file():
    """Check if Firebase service account key exists"""
    if os.path.exists("serviceAccountKey.json"):
        print("✅ Found serviceAccountKey.json")
        return True
    else:
        print("❌ serviceAccountKey.json not found")
        return False

def validate_firebase_file():
    """Validate Firebase service account key format"""
    try:
        with open("serviceAccountKey.json", 'r') as f:
            data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"❌ Invalid Firebase key file. Missing fields: {missing_fields}")
            return False, None
        
        print("✅ Firebase key file is valid")
        return True, data
    except json.JSONDecodeError:
        print("❌ Firebase key file is not valid JSON")
        return False, None
    except Exception as e:
        print(f"❌ Error reading Firebase key file: {e}")
        return False, None

def get_database_url():
    """Get database URL from user or detect from project ID"""
    try:
        with open("serviceAccountKey.json", 'r') as f:
            data = json.load(f)
        
        project_id = data.get('project_id', '')
        if project_id:
            # Generate likely database URL
            suggested_url = f"https://{project_id}-default-rtdb.firebaseio.com/"
            print(f"\n🔥 Detected project ID: {project_id}")
            print(f"📍 Suggested database URL: {suggested_url}")
            
            use_suggested = input("\nUse this database URL? (y/n): ").lower().startswith('y')
            if use_suggested:
                return suggested_url
        
        print("\n📝 Please enter your Firebase Realtime Database URL:")
        print("   Format: https://your-project-default-rtdb.firebaseio.com/")
        print("   (Find this in Firebase Console → Realtime Database)")
        
        url = input("Database URL: ").strip()
        if not url.startswith('https://') or not url.endswith('/'):
            print("⚠️ URL should start with https:// and end with /")
            if not url.endswith('/'):
                url += '/'
        
        return url
    except Exception as e:
        print(f"Error getting database URL: {e}")
        return None

def update_firebase_service(database_url):
    """Update the Firebase service file with the correct database URL"""
    try:
        firebase_service_path = Path("core/firebase_service.py")
        
        if not firebase_service_path.exists():
            print("❌ core/firebase_service.py not found")
            return False
        
        # Read current content
        with open(firebase_service_path, 'r') as f:
            content = f.read()
        
        # Replace the database URL
        old_url_line = "'databaseURL': 'https://your-project-default-rtdb.firebaseio.com/'"
        new_url_line = f"'databaseURL': '{database_url}'"
        
        if old_url_line in content:
            content = content.replace(old_url_line, new_url_line)
            
            # Write updated content
            with open(firebase_service_path, 'w') as f:
                f.write(content)
            
            print("✅ Updated Firebase service with your database URL")
            return True
        else:
            print("⚠️ Could not find database URL line to replace")
            print("Please manually update core/firebase_service.py")
            print(f"Replace the databaseURL with: {database_url}")
            return False
    
    except Exception as e:
        print(f"❌ Error updating Firebase service: {e}")
        return False

def test_firebase_connection():
    """Test Firebase connection"""
    try:
        print("\n🧪 Testing Firebase connection...")
        
        # Import and test
        from core.firebase_service import initialize_firebase
        result = initialize_firebase()
        
        if result:
            print("✅ Firebase connection successful!")
            return True
        else:
            print("❌ Firebase connection failed")
            return False
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed: pip install firebase-admin")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main setup process"""
    print("🔥 Firebase Setup Helper for HerShield")
    print("=" * 50)
    
    # Step 1: Check for service account key
    print("\n📋 Step 1: Checking Firebase service account key...")
    if not check_firebase_file():
        print("\n📥 To get your Firebase service account key:")
        print("1. Go to https://console.firebase.google.com/")
        print("2. Select your project")
        print("3. Go to Project Settings (gear icon)")
        print("4. Click 'Service accounts' tab")
        print("5. Click 'Generate new private key'")
        print("6. Save the file as 'serviceAccountKey.json' in this folder")
        print("\nRun this script again after adding the file.")
        return False
    
    # Step 2: Validate the key file
    print("\n🔍 Step 2: Validating Firebase key file...")
    valid, data = validate_firebase_file()
    if not valid:
        print("\nPlease check your serviceAccountKey.json file and try again.")
        return False
    
    # Step 3: Get database URL
    print("\n🌐 Step 3: Setting up database URL...")
    database_url = get_database_url()
    if not database_url:
        print("❌ Database URL is required")
        return False
    
    # Step 4: Update Firebase service
    print("\n⚙️ Step 4: Updating Firebase service configuration...")
    if not update_firebase_service(database_url):
        print("⚠️ Manual configuration may be required")
    
    # Step 5: Test connection
    print("\n🧪 Step 5: Testing Firebase connection...")
    if test_firebase_connection():
        print("\n🎉 Firebase setup complete!")
        print("\n✅ Your HerShield project is now connected to Firebase!")
        print("\n🚀 Next steps:")
        print("1. Run: python futuristic_hershield.py")
        print("2. Complete user setup (name, email, contacts)")
        print("3. Test the system with 'TEST SYSTEM' button")
        print("4. Check Firebase console to see your data")
        return True
    else:
        print("\n❌ Setup incomplete. Please check the errors above.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🔥 Firebase connection successful! 💜")
        else:
            print("\n⚠️ Setup needs attention. Check the messages above.")
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        print("Please check the Firebase Setup Guide for manual configuration.")