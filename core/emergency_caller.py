#!/usr/bin/env python3
"""
Emergency Caller Service
Automatically calls police, ambulance, and emergency contacts
"""

import subprocess
import platform
import webbrowser

class EmergencyCaller:
    """
    Handles emergency calls to police, ambulance, and contacts
    """
    
    def __init__(self):
        self.system = platform.system()
        
        # Emergency numbers by country (India by default)
        self.emergency_numbers = {
            'police': '100',
            'ambulance': '108',
            'women_helpline': '1091',
            'fire': '101',
            'disaster': '108'
        }
    
    def call_police(self, location=None):
        """Call police with location"""
        print("📞 CALLING POLICE (100)...")
        return self._make_call(
            self.emergency_numbers['police'],
            f"Emergency at {location}" if location else "Emergency"
        )
    
    def call_ambulance(self, location=None):
        """Call ambulance with location"""
        print("🚑 CALLING AMBULANCE (108)...")
        return self._make_call(
            self.emergency_numbers['ambulance'],
            f"Medical emergency at {location}" if location else "Medical emergency"
        )
    
    def call_women_helpline(self, location=None):
        """Call women helpline"""
        print("👮‍♀️ CALLING WOMEN HELPLINE (1091)...")
        return self._make_call(
            self.emergency_numbers['women_helpline'],
            f"Women in distress at {location}" if location else "Women in distress"
        )
    
    def call_contact(self, phone_number, name="Emergency Contact"):
        """Call emergency contact"""
        print(f"📞 CALLING {name} ({phone_number})...")
        return self._make_call(phone_number, f"Emergency call to {name}")
    
    def _make_call(self, number, message):
        """
        Make actual phone call
        Platform-specific implementation
        """
        try:
            if self.system == "Windows":
                # Windows: Use tel: protocol (requires phone link app)
                webbrowser.open(f"tel:{number}")
                print(f"✅ Call initiated to {number}")
                return {'success': True, 'number': number, 'message': message}
            
            elif self.system == "Linux":
                # Linux: Try various methods
                try:
                    # Method 1: Using gnome-phone-manager
                    subprocess.run(['gnome-phone-manager', '--dial', number], check=True)
                except:
                    try:
                        # Method 2: Using xdg-open
                        subprocess.run(['xdg-open', f'tel:{number}'], check=True)
                    except:
                        # Method 3: Using tel: protocol
                        webbrowser.open(f"tel:{number}")
                
                print(f"✅ Call initiated to {number}")
                return {'success': True, 'number': number, 'message': message}
            
            elif self.system == "Darwin":  # macOS
                # macOS: Use tel: protocol
                webbrowser.open(f"tel:{number}")
                print(f"✅ Call initiated to {number}")
                return {'success': True, 'number': number, 'message': message}
            
            else:
                print(f"⚠️ Calling not supported on {self.system}")
                return {'success': False, 'error': 'Platform not supported'}
        
        except Exception as e:
            print(f"❌ Call error: {e}")
            return {'success': False, 'error': str(e)}
    
    def call_all_emergency_services(self, location=None):
        """Call all emergency services"""
        results = {
            'police': self.call_police(location),
            'ambulance': self.call_ambulance(location),
            'women_helpline': self.call_women_helpline(location)
        }
        return results
    
    def call_all_contacts(self, contacts):
        """
        Call all emergency contacts
        
        Args:
            contacts: List of dicts with 'name' and 'phone' keys
        """
        results = []
        for contact in contacts:
            result = self.call_contact(
                contact.get('phone', ''),
                contact.get('name', 'Emergency Contact')
            )
            results.append(result)
        return results


# Global instance
emergency_caller = EmergencyCaller()
