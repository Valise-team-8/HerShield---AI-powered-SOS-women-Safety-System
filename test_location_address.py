#!/usr/bin/env python3
"""
Test location address resolution
"""

def test_location_address():
    print("🌍 Testing location address resolution...")
    
    try:
        from core.enhanced_location_service import EnhancedLocationService
        
        location_service = EnhancedLocationService()
        
        # Test IP location
        print("📍 Getting IP-based location...")
        ip_location = location_service.get_ip_location()
        
        if ip_location:
            print(f"✅ Location found:")
            print(f"   📍 Address: {ip_location.get('address', 'Not resolved')}")
            print(f"   🌐 Coordinates: {ip_location.get('latitude')}, {ip_location.get('longitude')}")
            print(f"   🏙️ City: {ip_location.get('city')}")
            print(f"   🗺️ Region: {ip_location.get('region')}")
            print(f"   🌏 Country: {ip_location.get('country')}")
            print(f"   📡 ISP: {ip_location.get('isp')}")
            print(f"   🎯 Method: {ip_location.get('method')}")
            
            # Test if address contains "not available"
            address = ip_location.get('address', '')
            if 'not available' in address.lower() or 'address not' in address.lower():
                print("⚠️ Address still showing as not available")
                return False
            else:
                print("✅ Address resolution working!")
                return True
        else:
            print("❌ No location data received")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_location_address()
    if success:
        print("\n🎉 Location address resolution is working!")
    else:
        print("\n⚠️ Location address needs attention.")