#!/usr/bin/env python3
"""
Google Maps API Enhanced Location Service
Provides high-accuracy location using Google's geolocation services
"""

import json
import os
import time
import requests
import subprocess
import platform
import logging
from datetime import datetime
import re

class GoogleMapsLocationService:
    """Enhanced location service using Google Maps APIs"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or self.load_api_key()
        self.location_cache = {}
        self.cache_file = "data/google_location_cache.json"
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load cached data
        self.load_cache()

    def load_api_key(self):
        """Load Google Maps API key from config file"""
        config_files = [
            "data/google_maps_config.json",
            "config/google_maps.json",
            ".env"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    if config_file.endswith('.json'):
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                            return config.get('google_maps_api_key')
                    elif config_file.endswith('.env'):
                        with open(config_file, 'r') as f:
                            for line in f:
                                if line.startswith('GOOGLE_MAPS_API_KEY='):
                                    return line.split('=', 1)[1].strip()
                except Exception as e:
                    self.logger.error(f"Error loading API key from {config_file}: {e}")
        
        return None

    def save_api_key(self, api_key):
        """Save Google Maps API key to config file"""
        try:
            config = {
                'google_maps_api_key': api_key,
                'created': datetime.now().isoformat(),
                'service': 'HerShield Location Service'
            }
            
            with open("data/google_maps_config.json", 'w') as f:
                json.dump(config, f, indent=2)
            
            self.api_key = api_key
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving API key: {e}")
            return False

    def load_cache(self):
        """Load cached location data"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.location_cache = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading cache: {e}")

    def save_cache(self):
        """Save location data to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.location_cache, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving cache: {e}")

    def get_wifi_networks_windows(self):
        """Get WiFi networks on Windows for geolocation"""
        try:
            if platform.system() != "Windows":
                return []
            
            # Get WiFi networks using netsh
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'profiles'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            networks = []
            for line in result.stdout.split('\n'):
                if 'All User Profile' in line:
                    profile_name = line.split(':')[1].strip()
                    
                    # Get detailed info for each network
                    try:
                        detail_result = subprocess.run(
                            ['netsh', 'wlan', 'show', 'profile', f'name="{profile_name}"', 'key=clear'],
                            capture_output=True, text=True, timeout=5
                        )
                        
                        if detail_result.returncode == 0:
                            # Extract BSSID/MAC and signal strength if available
                            bssid = None
                            signal_strength = None
                            
                            for detail_line in detail_result.stdout.split('\n'):
                                if 'SSID name' in detail_line:
                                    ssid = detail_line.split(':')[1].strip().strip('"')
                                elif 'BSSID' in detail_line:
                                    bssid = detail_line.split(':')[1].strip()
                                elif 'Signal' in detail_line:
                                    signal_match = re.search(r'(\d+)%', detail_line)
                                    if signal_match:
                                        signal_strength = int(signal_match.group(1))
                            
                            network_info = {
                                'macAddress': bssid or f"unknown_{len(networks)}",
                                'signalStrength': signal_strength or -50,
                                'age': 0,
                                'channel': 11,  # Default channel
                                'signalToNoiseRatio': 0
                            }
                            
                            networks.append(network_info)
                            
                            if len(networks) >= 5:  # Limit to 5 networks
                                break
                                
                    except Exception as e:
                        self.logger.debug(f"Error getting network details: {e}")
                        continue
            
            return networks
            
        except Exception as e:
            self.logger.error(f"Error getting WiFi networks: {e}")
            return []

    def get_cell_towers_info(self):
        """Get cell tower information (placeholder - requires special APIs)"""
        # This would require access to cellular APIs or special permissions
        # For demo purposes, return empty list
        return []

    def google_geolocation_api(self, wifi_networks=None, cell_towers=None):
        """Use Google Geolocation API for high-accuracy location"""
        if not self.api_key:
            self.logger.error("Google Maps API key not configured")
            return None
        
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={self.api_key}"
        
        # Prepare request data
        request_data = {
            "considerIp": True,
            "wifiAccessPoints": wifi_networks or [],
            "cellTowers": cell_towers or []
        }
        
        try:
            response = requests.post(url, json=request_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'location' in data:
                    location = {
                        'latitude': data['location']['lat'],
                        'longitude': data['location']['lng'],
                        'accuracy': data.get('accuracy', 100),
                        'method': 'google_geolocation_api',
                        'timestamp': time.time(),
                        'data_sources': []
                    }
                    
                    # Add data source information
                    if wifi_networks:
                        location['data_sources'].append(f"wifi_networks_{len(wifi_networks)}")
                    if cell_towers:
                        location['data_sources'].append(f"cell_towers_{len(cell_towers)}")
                    if not wifi_networks and not cell_towers:
                        location['data_sources'].append("ip_only")
                    
                    return location
                    
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                self.logger.error(f"Google Geolocation API error: {error_message}")
                
        except Exception as e:
            self.logger.error(f"Google Geolocation API request failed: {e}")
        
        return None

    def google_geocoding_api(self, address):
        """Use Google Geocoding API to convert address to coordinates"""
        if not self.api_key:
            self.logger.error("Google Maps API key not configured")
            return None
        
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'OK' and data['results']:
                    result = data['results'][0]
                    geometry = result['geometry']
                    
                    location = {
                        'latitude': geometry['location']['lat'],
                        'longitude': geometry['location']['lng'],
                        'accuracy': 50,  # Geocoding is usually quite accurate
                        'method': 'google_geocoding_api',
                        'address': result['formatted_address'],
                        'place_id': result.get('place_id'),
                        'location_type': geometry.get('location_type'),
                        'timestamp': time.time()
                    }
                    
                    # Add viewport bounds if available
                    if 'viewport' in geometry:
                        location['viewport'] = geometry['viewport']
                    
                    return location
                    
            else:
                self.logger.error(f"Google Geocoding API error: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Google Geocoding API request failed: {e}")
        
        return None

    def google_places_nearby_search(self, latitude, longitude, radius=1000):
        """Use Google Places API to find nearby places for location verification"""
        if not self.api_key:
            return []
        
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': f"{latitude},{longitude}",
            'radius': radius,
            'key': self.api_key,
            'type': 'establishment'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'OK':
                    places = []
                    for place in data.get('results', [])[:5]:  # Limit to 5 places
                        places.append({
                            'name': place.get('name'),
                            'types': place.get('types', []),
                            'rating': place.get('rating'),
                            'vicinity': place.get('vicinity'),
                            'place_id': place.get('place_id')
                        })
                    
                    return places
                    
        except Exception as e:
            self.logger.error(f"Google Places API request failed: {e}")
        
        return []

    def get_high_accuracy_location(self):
        """Get high-accuracy location using all available Google APIs"""
        if not self.api_key:
            self.logger.error("Google Maps API key required for high accuracy location")
            return None
        
        # Method 1: Try WiFi + Cell Tower geolocation
        wifi_networks = self.get_wifi_networks_windows()
        cell_towers = self.get_cell_towers_info()
        
        if wifi_networks or cell_towers:
            self.logger.info(f"Using Google Geolocation API with {len(wifi_networks)} WiFi networks")
            location = self.google_geolocation_api(wifi_networks, cell_towers)
            
            if location:
                # Enhance with nearby places for verification
                places = self.google_places_nearby_search(
                    location['latitude'], 
                    location['longitude']
                )
                location['nearby_places'] = places
                
                # Get formatted address
                reverse_geocode = self.reverse_geocode(
                    location['latitude'], 
                    location['longitude']
                )
                if reverse_geocode:
                    location['address'] = reverse_geocode.get('address', '')
                
                return location
        
        # Method 2: IP-only geolocation as fallback
        self.logger.info("Using Google Geolocation API with IP only")
        location = self.google_geolocation_api()
        
        if location:
            # Enhance with address and nearby places
            reverse_geocode = self.reverse_geocode(
                location['latitude'], 
                location['longitude']
            )
            if reverse_geocode:
                location['address'] = reverse_geocode.get('address', '')
            
            places = self.google_places_nearby_search(
                location['latitude'], 
                location['longitude']
            )
            location['nearby_places'] = places
        
        return location

    def reverse_geocode(self, latitude, longitude):
        """Convert coordinates to address using Google Geocoding API"""
        if not self.api_key:
            return None
        
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'latlng': f"{latitude},{longitude}",
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'OK' and data['results']:
                    result = data['results'][0]
                    
                    return {
                        'address': result['formatted_address'],
                        'place_id': result.get('place_id'),
                        'address_components': result.get('address_components', []),
                        'location_type': result['geometry'].get('location_type')
                    }
                    
        except Exception as e:
            self.logger.error(f"Reverse geocoding failed: {e}")
        
        return None

    def geocode_address(self, address):
        """Convert address to coordinates"""
        return self.google_geocoding_api(address)

    def get_location_from_address(self, address):
        """Get location from user-provided address"""
        print(f"🔍 Geocoding address: {address}")
        location = self.geocode_address(address)
        
        if location:
            print(f"✅ Address found!")
            print(f"📍 Coordinates: {location['latitude']:.6f}, {location['longitude']:.6f}")
            print(f"🎯 Accuracy: ±{location['accuracy']}m")
            print(f"📍 Full Address: {location['address']}")
            
            return location
        else:
            print("❌ Address not found")
            return None

def setup_google_maps_api():
    """Setup Google Maps API key"""
    print("🗺️  GOOGLE MAPS API SETUP")
    print("=" * 30)
    print("To use high-accuracy location services, you need a Google Maps API key.")
    print("\n📋 Steps to get API key:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable these APIs:")
    print("   • Geolocation API")
    print("   • Geocoding API") 
    print("   • Places API (optional)")
    print("4. Create credentials (API Key)")
    print("5. Restrict the key to your IP address for security")
    
    print("\n🎁 FREE TIER (as of 2024):")
    print("• $200 FREE credit per month (never expires)")
    print("• Geolocation API: 40,000 FREE requests/month")
    print("• Geocoding API: 40,000 FREE requests/month")
    print("• Places API: 11,764 FREE requests/month")
    print("• Maps JavaScript API: 28,500 FREE map loads/month")
    
    print("\n💰 After free tier:")
    print("• Geolocation API: $5 per 1,000 requests")
    print("• Geocoding API: $5 per 1,000 requests")
    print("• Places API: $17 per 1,000 requests")
    
    api_key = input("\nEnter your Google Maps API key (or press Enter to skip): ").strip()
    
    if api_key:
        service = GoogleMapsLocationService()
        if service.save_api_key(api_key):
            print("✅ API key saved successfully!")
            
            # Test the API key
            print("\n🧪 Testing API key...")
            test_location = service.get_high_accuracy_location()
            
            if test_location:
                print("✅ API key is working!")
                print(f"📍 Test location: {test_location['latitude']:.6f}, {test_location['longitude']:.6f}")
                print(f"🎯 Accuracy: ±{test_location['accuracy']}m")
                return True
            else:
                print("❌ API key test failed. Please check your key and API settings.")
                return False
        else:
            print("❌ Failed to save API key")
            return False
    else:
        print("⏭️  Skipped API key setup")
        return False

def test_google_maps_location():
    """Test Google Maps location services"""
    print("🧪 TESTING GOOGLE MAPS LOCATION SERVICES")
    print("=" * 45)
    
    service = GoogleMapsLocationService()
    
    if not service.api_key:
        print("❌ Google Maps API key not configured")
        print("Run setup first: python -c \"from core.google_maps_location import setup_google_maps_api; setup_google_maps_api()\"")
        return
    
    print("🔍 Testing high-accuracy location...")
    location = service.get_high_accuracy_location()
    
    if location:
        print(f"\n✅ SUCCESS!")
        print(f"📍 Coordinates: {location['latitude']:.6f}, {location['longitude']:.6f}")
        print(f"🎯 Accuracy: ±{location['accuracy']}m")
        print(f"🔧 Method: {location['method']}")
        print(f"📊 Data Sources: {', '.join(location.get('data_sources', []))}")
        
        if 'address' in location:
            print(f"📍 Address: {location['address']}")
        
        if 'nearby_places' in location and location['nearby_places']:
            print(f"\n🏢 Nearby Places:")
            for place in location['nearby_places'][:3]:
                print(f"   • {place['name']} ({place.get('vicinity', 'Unknown area')})")
        
        print(f"\n🔗 Google Maps: https://maps.google.com/?q={location['latitude']},{location['longitude']}")
        
        # Compare with IP-only location
        print(f"\n📊 ACCURACY COMPARISON:")
        ip_location = service.google_geolocation_api()  # IP-only
        if ip_location:
            print(f"IP-only accuracy: ±{ip_location['accuracy']}m")
            print(f"WiFi+IP accuracy: ±{location['accuracy']}m")
            improvement = ip_location['accuracy'] - location['accuracy']
            if improvement > 0:
                print(f"🎯 Improvement: {improvement}m better accuracy!")
        
    else:
        print("❌ Failed to get location")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_google_maps_api()
    else:
        test_google_maps_location()