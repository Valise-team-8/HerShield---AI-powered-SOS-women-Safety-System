import firebase_admin
from firebase_admin import credentials, db
import os

# Initialize Firebase only if service account key exists
def initialize_firebase():
    """Initialize Firebase with demo or real credentials"""
    if not firebase_admin._apps:
        try:
            # Try real service account key first
            if os.path.exists("serviceAccountKey.json"):
                try:
                    # Load and fix the key format
                    import json
                    with open("serviceAccountKey.json", 'r') as f:
                        key_data = json.load(f)
                    
                    # Fix the private key format if needed
                    if "private_key" in key_data:
                        private_key = key_data["private_key"]
                        # Replace escaped newlines with actual newlines
                        if "\\n" in private_key:
                            key_data["private_key"] = private_key.replace("\\n", "\n")
                    
                    cred = credentials.Certificate(key_data)
                    firebase_admin.initialize_app(cred, {
                        'databaseURL': 'https://hershield-8eef0-default-rtdb.firebaseio.com/'
                    })
                    print("✅ Firebase initialized with real credentials")
                    return True
                except Exception as key_error:
                    print(f"⚠️ Firebase key error: {str(key_error)[:100]}...")
                    print("💡 Tip: Generate a new service account key from Firebase Console")
                    print("📋 Using local storage mode instead")
                    return False
            elif os.path.exists("serviceAccountKey_DEMO.json"):
                print("⚠️  Using demo Firebase credentials - replace with real ones")
                # Don't actually initialize with demo credentials
                return False
            else:
                print("❌ No Firebase credentials found")
                return False
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            return False
    return True

# Initialize on import - but handle failures gracefully
try:
    firebase_available = initialize_firebase()
except Exception as e:
    print(f"⚠️  Firebase unavailable: {e}")
    firebase_available = False

def get_user_contacts(email):
    """Get user contacts from Firebase (if available)"""
    if not firebase_available:
        print("[INFO] Firebase not available, using local contacts")
        return []
    
    try:
        ref = db.reference('/users')
        key = email.replace('.', '_').replace('@', '_')
        data = ref.child(key).get()
        
        if data and "contacts" in data:
            return data["contacts"]
        return []
    except Exception as e:
        print(f"[ERROR] Firebase error: {e}")
        return []

def save_user_data(email, user_data):
    """Save user data to Firebase"""
    if not firebase_available:
        print("[INFO] Firebase not available, data saved locally only")
        return False
    
    try:
        ref = db.reference('/users')
        key = email.replace('.', '_').replace('@', '_')
        
        # Prepare data for Firebase
        firebase_data = {
            'name': user_data.get('name', ''),
            'email': email,
            'phone': user_data.get('phone', ''),
            'contacts': user_data.get('emergency_contacts', []),
            'last_updated': int(__import__('time').time() * 1000),  # Current timestamp
            'app_version': '3.0'
        }
        
        ref.child(key).set(firebase_data)
        print(f"✅ User data saved to Firebase for {email}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Firebase save error: {e}")
        return False

def get_user_profile(email):
    """Get complete user profile from Firebase"""
    if not firebase_available:
        return None
    
    try:
        ref = db.reference('/users')
        key = email.replace('.', '_').replace('@', '_')
        data = ref.child(key).get()
        
        if data:
            return {
                'name': data.get('name', ''),
                'email': data.get('email', email),
                'phone': data.get('phone', ''),
                'emergency_contacts': data.get('contacts', []),
                'last_updated': data.get('last_updated'),
                'data_source': 'firebase'
            }
        return None
        
    except Exception as e:
        print(f"[ERROR] Firebase profile error: {e}")
        return None

def log_emergency_alert(email, alert_data):
    """Log emergency alert to Firebase"""
    if not firebase_available:
        return False
    
    try:
        ref = db.reference('/emergency_logs')
        key = email.replace('.', '_').replace('@', '_')
        
        alert_log = {
            'user_email': email,
            'alert_type': alert_data.get('type', 'unknown'),
            'keywords': alert_data.get('keywords', []),
            'location': alert_data.get('location', {}),
            'timestamp': int(__import__('time').time() * 1000),  # Current timestamp
            'severity': alert_data.get('severity', 'medium'),
            'acknowledged': False
        }
        
        ref.child(key).push(alert_log)
        print(f"✅ Emergency alert logged to Firebase")
        return True
        
    except Exception as e:
        print(f"[ERROR] Firebase alert log error: {e}")
        return False

def update_user_location(email, location_data):
    """Update user's last known location in Firebase"""
    if not firebase_available:
        return False
    
    try:
        ref = db.reference('/users')
        key = email.replace('.', '_').replace('@', '_')
        
        location_update = {
            'last_location': {
                'latitude': location_data.get('latitude'),
                'longitude': location_data.get('longitude'),
                'address': location_data.get('address', ''),
                'accuracy': location_data.get('accuracy', 0),
                'timestamp': int(__import__('time').time() * 1000)  # Current timestamp
            }
        }
        
        ref.child(key).update(location_update)
        return True
        
    except Exception as e:
        print(f"[ERROR] Firebase location update error: {e}")
        return False
