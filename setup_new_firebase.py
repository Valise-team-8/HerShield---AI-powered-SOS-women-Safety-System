#!/usr/bin/env python3
"""
Firebase Setup Helper Script
"""

import os
import json
import webbrowser

def setup_firebase():
    print("🔥 Firebase Setup Helper")
    print("=" * 50)
    
    # Check current status
    if os.path.exists("serviceAccountKey.json"):
        try:
            with open("serviceAccountKey.json", 'r') as f:
                data = json.load(f)
            project_id = data.get('project_id', 'unknown')
            print(f"📋 Current key file: {project_id}")
            
            # Test current key
            print("🧪 Testing current Firebase key...")
            try:
                import firebase_admin
                from firebase_admin import credentials
                
                # Clear existing apps
                try:
                    firebase_admin.delete_app(firebase_admin.get_app())
                except:
                    pass
                
                cred = credentials.Certificate(data)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': f'https://{project_id}-default-rtdb.firebaseio.com/'
                })
                print("✅ Current Firebase key is working!")
                
                choice = input("\\n🤔 Current key works. Do you want to create a new one anyway? (y/N): ")
                if choice.lower() != 'y':
                    print("✅ Using existing Firebase key.")
                    return
                    
            except Exception as e:
                print(f"❌ Current key not working: {str(e)[:100]}...")
                print("📝 You need to create a new Firebase service account key.")
                
        except Exception as e:
            print(f"❌ Error reading current key: {e}")
    else:
        print("📝 No Firebase key found. You need to create one.")
    
    print("\\n🚀 Opening Firebase Console...")
    print("\\n📋 Follow these steps:")
    print("1. Sign in to Firebase Console")
    print("2. Select or create project 'hershield-8eef0' (or your own)")
    print("3. Go to Project Settings (gear icon)")
    print("4. Click 'Service accounts' tab")
    print("5. Click 'Generate new private key'")
    print("6. Download the JSON file")
    print("7. Rename it to 'serviceAccountKey.json'")
    print("8. Replace the file in this folder")
    
    # Open Firebase Console
    try:
        webbrowser.open("https://console.firebase.google.com/")
        print("\\n🌐 Firebase Console opened in your browser!")
    except:
        print("\\n🌐 Please manually go to: https://console.firebase.google.com/")
    
    print("\\n⏳ After downloading the new key file:")
    print("1. Replace serviceAccountKey.json in this folder")
    print("2. Run: python test_firebase_simple.py")
    print("3. Run: python futuristic_hershield.py")
    
    # Wait for user to complete setup
    input("\\n📥 Press Enter after you've downloaded and replaced the key file...")
    
    # Test new key
    if os.path.exists("serviceAccountKey.json"):
        print("\\n🧪 Testing new Firebase key...")
        try:
            with open("serviceAccountKey.json", 'r') as f:
                data = json.load(f)
            
            project_id = data.get('project_id', 'unknown')
            print(f"📋 New project ID: {project_id}")
            
            # Test the new key
            import firebase_admin
            from firebase_admin import credentials, db
            
            # Clear existing apps
            try:
                firebase_admin.delete_app(firebase_admin.get_app())
            except:
                pass
            
            cred = credentials.Certificate(data)
            firebase_admin.initialize_app(cred, {
                'databaseURL': f'https://{project_id}-default-rtdb.firebaseio.com/'
            })
            
            # Test database write
            ref = db.reference('/')
            ref.child('setup_test').set({
                'timestamp': firebase_admin.db.ServerValue.TIMESTAMP,
                'status': 'success'
            })
            ref.child('setup_test').delete()
            
            print("✅ New Firebase key is working perfectly!")
            print("🎉 Firebase setup complete!")
            
            # Update database URL in firebase_service.py if needed
            if project_id != 'hershield-8eef0':
                print(f"\\n📝 Note: Update database URL in core/firebase_service.py")
                print(f"Change to: https://{project_id}-default-rtdb.firebaseio.com/")
            
        except Exception as e:
            print(f"❌ New key test failed: {e}")
            print("\\n🔧 Troubleshooting:")
            print("1. Make sure you downloaded the correct JSON file")
            print("2. Make sure it's named exactly 'serviceAccountKey.json'")
            print("3. Make sure Realtime Database is enabled in Firebase Console")
            print("4. Try creating a new Firebase project")
    else:
        print("❌ Key file not found. Please download and place it in this folder.")

if __name__ == "__main__":
    setup_firebase()