#!/usr/bin/env python3
"""
Simple Firebase test
"""

import json
import os

def test_firebase():
    print("🔥 Testing Firebase connection...")
    
    try:
        import firebase_admin
        from firebase_admin import credentials, db
        print("✅ Firebase Admin SDK imported")
        
        # Clear existing apps
        try:
            firebase_admin.delete_app(firebase_admin.get_app())
        except:
            pass
        
        # Test key loading
        if os.path.exists("serviceAccountKey.json"):
            with open("serviceAccountKey.json", 'r') as f:
                key_data = json.load(f)
            print(f"✅ Key file loaded: {key_data.get('project_id')}")
            
            # Test credential creation
            cred = credentials.Certificate(key_data)
            print("✅ Credentials created")
            
            # Test Firebase initialization
            app = firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://hershield-8eef0-default-rtdb.firebaseio.com/'
            })
            print("✅ Firebase initialized")
            
            # Test database connection
            import time
            ref = db.reference('/')
            ref.child('test_connection').set({
                'timestamp': int(time.time() * 1000),
                'status': 'success'
            })
            print("✅ Database write successful")
            
            # Clean up
            ref.child('test_connection').delete()
            print("✅ Test cleanup complete")
            
            print("🎉 Firebase connection working perfectly!")
            return True
            
        else:
            print("❌ serviceAccountKey.json not found")
            return False
            
    except Exception as e:
        print(f"❌ Firebase test failed: {e}")
        return False

if __name__ == "__main__":
    test_firebase()