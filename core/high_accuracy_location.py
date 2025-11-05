#!/usr/bin/env python3
"""
High Accuracy Location Service for HerShield
Implements multiple location detection methods for maximum accuracy
"""

import json
import os
import time
import threading
import requests
import subprocess
import platform
import logging
from datetime import datetime
import socket
import re

class HighAccuracyLocationService:
    """High accuracy location service with multiple detection methods"""
    
    def __init__(self):
        self.last_location = None
        self.location_cache = {}
        self.location_file = "data/high_accuracy_location.json"
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load cached location data
        self.load_location_cache()

    def load_location_cache(self):
        """Load cached location data"""
        try:
            if os.path.exists(self.location_file):
                with open(self.location_file, 'r') as f:
                    data = json.load(f)
                    self.last_location = data.get('last_location')
                    self.location_cache = data.get('cache', {})
        except Exception as e:
            self.logger.error(f"Error loading location cache: {e}")

    def save_location_cache(self):
        """Save location data to cache"""
        try:
            data = {
                'last_location': self.last_location,
                'cache': self.location_cache,
                'last_updated': time.time()
            }
            with open(self.location_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving location cache: {e}")

    def get_windows_wifi_location(self):
        """Get location using Windows WiFi networks (Windows 10/11)"""
        try:
            if platform.system() != "Windows":
                return None
            
            # Get WiFi networks using netsh
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'profiles'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            # Parse WiFi networks
            networks = []
            for line in result.stdout.split('\n'):
                if 'All User Profile' in line:
                    profile_name = line.split(':')[1].strip()
                    networks.append(profile_name)
            
            if not networks:
                return None
            
            # Get detailed info for each network
            wifi_data = []
            for network in networks[:5]:  # Limit to 5 networks
                try:
                    detail_result = subprocess.run(
                        ['netsh', 'wlan', 'show', 'profile', f'name="{network}"', 'key=clear'],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    if detail_result.returncode == 0:
                        # Extract BSSID/MAC if available
                        for line in detail_result.stdout.split('\n'):
                            if 'SSID name' in line:
                                ssid = line.split(':')[1].strip().strip('"')
                                wifi_data.append({'ssid': ssid, 'network': network})
                                break
                except:
                    continue
            
            if wifi_data:
                # Use Google Geolocation API (requires API key)
                return self.query_google_geolocation(wifi_data)
            
        except Exception as e:
            self.logger.error(f"Windows WiFi location error: {e}")
        
        return None

    def get_browser_location(self):
        """Get location using browser geolocation (requires user permission)"""
        try:
            # Create a simple HTML file for geolocation
            html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>HerShield Location</title>
</head>
<body>
    <script>
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const location = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: Date.now()
                };
                
                // Save to file
                fetch('data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(location)))
                    .then(() => {
                        document.body.innerHTML = '<h2>Location obtained: ' + 
                            location.latitude + ', ' + location.longitude + 
                            ' (±' + Math.round(location.accuracy) + 'm)</h2>';
                    });
            },
            function(error) {
                document.body.innerHTML = '<h2>Location access denied or unavailable</h2>';
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            }
        );
    } else {
        document.body.innerHTML = '<h2>Geolocation not supported</h2>';
    }
    </script>
</body>
</html>
            '''
            
            # Save HTML file
            html_file = "data/location_request.html"
            with open(html_file, 'w') as f:
                f.write(html_content)
            
            self.logger.info("Browser location request created. Open data/location_request.html in browser.")
            return None
            
        except Exception as e:
            self.logger.error(f"Browser location error: {e}")
        
        return None

    def get_enhanced_ip_location(self):
        """Get enhanced IP-based location using multiple services"""
        services = [
            {
                'name': 'ipapi',
                'url': 'http://ip-api.com/json/',
                'parser': self.parse_ipapi_response
            },
            {
                'name': 'ipinfo',
                'url': 'https://ipinfo.io/json',
                'parser': self.parse_ipinfo_response
            },
            {
                'name': 'ipgeolocation',
                'url': 'https://api.ipgeolocation.io/ipgeo?apiKey=free',
                'parser': self.parse_ipgeolocation_response
            }
        ]
        
        for service in services:
            try:
                response = requests.get(service['url'], timeout=5)
                if response.status_code == 200:
                    location = service['parser'](response.json())
                    if location:
                        location['method'] = f"enhanced_ip_{service['name']}"
                        return location
            except Exception as e:
                self.logger.debug(f"Service {service['name']} failed: {e}")
        
        return None

    def parse_ipapi_response(self, data):
        """Parse ip-api.com response"""
        if data.get('status') == 'success':
            return {
                'latitude': float(data.get('lat', 0)),
                'longitude': float(data.get('lon', 0)),
                'accuracy': 5000,  # IP accuracy is typically city-level
                'address': f"{data.get('city', '')}, {data.get('regionName', '')}, {data.get('country', '')}",
                'city': data.get('city', ''),
                'region': data.get('regionName', ''),
                'country': data.get('country', ''),
                'isp': data.get('isp', ''),
                'timestamp': time.time()
            }
        return None

    def parse_ipinfo_response(self, data):
        """Parse ipinfo.io response"""
        if 'loc' in data:
            lat, lon = data['loc'].split(',')
            return {
                'latitude': float(lat),
                'longitude': float(lon),
                'accuracy': 5000,
                'address': f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}",
                'city': data.get('city', ''),
                'region': data.get('region', ''),
                'country': data.get('country', ''),
                'org': data.get('org', ''),
                'timestamp': time.time()
            }
        return None

    def parse_ipgeolocation_response(self, data):
        """Parse ipgeolocation.io response"""
        if 'latitude' in data and 'longitude' in data:
            return {
                'latitude': float(data.get('latitude', 0)),
                'longitude': float(data.get('longitude', 0)),
                'accuracy': 3000,  # Slightly better accuracy
                'address': f"{data.get('city', '')}, {data.get('state_prov', '')}, {data.get('country_name', '')}",
                'city': data.get('city', ''),
                'region': data.get('state_prov', ''),
                'country': data.get('country_name', ''),
                'isp': data.get('isp', ''),
                'timestamp': time.time()
            }
        return None

    def get_cell_tower_location(self):
        """Get location using cell tower information (requires special APIs)"""
        try:
            # This would require access to cell tower APIs
            # For now, return None as it needs special permissions
            self.logger.info("Cell tower location requires special API access")
            return None
        except Exception as e:
            self.logger.error(f"Cell tower location error: {e}")
        return None

    def get_manual_precise_location(self):
        """Allow user to input precise coordinates manually"""
        try:
            print("\n🎯 Manual Precise Location Entry")
            print("=" * 40)
            print("Enter your precise coordinates:")
            
            lat_input = input("Latitude (e.g., 12.9716): ").strip()
            lon_input = input("Longitude (e.g., 77.5946): ").strip()
            description = input("Location description (optional): ").strip()
            
            if lat_input and lon_input:
                latitude = float(lat_input)
                longitude = float(lon_input)
                
                # Validate coordinates
                if -90 <= latitude <= 90 and -180 <= longitude <= 180:
                    return {
                        'latitude': latitude,
                        'longitude': longitude,
                        'accuracy': 10,  # Very high accuracy for manual entry
                        'address': description or f"Manual: {latitude}, {longitude}",
                        'method': 'manual_precise',
                        'timestamp': time.time()
                    }
                else:
                    print("❌ Invalid coordinates. Please check your input.")
            
        except ValueError:
            print("❌ Invalid coordinate format. Please enter numbers only.")
        except Exception as e:
            self.logger.error(f"Manual location error: {e}")
        
        return None

    def get_best_available_location(self):
        """Get the best available location using all methods"""
        methods = [
            ('Manual Precise', self.get_manual_precise_location),
            ('Windows WiFi', self.get_windows_wifi_location),
            ('Enhanced IP', self.get_enhanced_ip_location),
            ('Cell Tower', self.get_cell_tower_location),
        ]
        
        best_location = None
        best_accuracy = float('inf')
        
        for method_name, method_func in methods:
            try:
                self.logger.info(f"Trying {method_name} location...")
                location = method_func()
                
                if location:
                    accuracy = location.get('accuracy', float('inf'))
                    if accuracy < best_accuracy:
                        best_location = location
                        best_accuracy = accuracy
                        self.logger.info(f"✅ {method_name}: ±{accuracy}m accuracy")
                    else:
                        self.logger.info(f"✅ {method_name}: ±{accuracy}m (not best)")
                else:
                    self.logger.info(f"❌ {method_name}: Not available")
                    
            except Exception as e:
                self.logger.error(f"❌ {method_name} error: {e}")
        
        if best_location:
            self.last_location = best_location
            self.save_location_cache()
            
        return best_location

    def get_location_accuracy_report(self):
        """Generate a detailed accuracy report"""
        location = self.get_best_available_location()
        
        if not location:
            return "❌ No location data available"
        
        accuracy = location.get('accuracy', 0)
        method = location.get('method', 'unknown')
        
        # Accuracy categories
        if accuracy <= 10:
            accuracy_level = "🎯 EXCELLENT (GPS-level)"
        elif accuracy <= 100:
            accuracy_level = "✅ VERY GOOD (Street-level)"
        elif accuracy <= 1000:
            accuracy_level = "🟡 GOOD (Neighborhood-level)"
        elif accuracy <= 5000:
            accuracy_level = "🟠 MODERATE (City-level)"
        else:
            accuracy_level = "🔴 LOW (Regional-level)"
        
        report = f"""
🎯 LOCATION ACCURACY REPORT
{'=' * 40}
📍 Coordinates: {location['latitude']:.6f}, {location['longitude']:.6f}
🎯 Accuracy: ±{accuracy}m ({accuracy_level})
🔧 Method: {method}
📍 Address: {location.get('address', 'Unknown')}
⏰ Updated: {datetime.fromtimestamp(location.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}

🔗 Google Maps: https://maps.google.com/?q={location['latitude']},{location['longitude']}
"""
        
        return report

def test_location_accuracy():
    """Test all location methods and show accuracy comparison"""
    print("🎯 HerShield High Accuracy Location Test")
    print("=" * 50)
    
    service = HighAccuracyLocationService()
    
    # Test all methods
    methods = [
        ('Enhanced IP Location', service.get_enhanced_ip_location),
        ('Windows WiFi Location', service.get_windows_wifi_location),
    ]
    
    results = []
    
    for method_name, method_func in methods:
        print(f"\n🔍 Testing {method_name}...")
        try:
            location = method_func()
            if location:
                accuracy = location.get('accuracy', 0)
                print(f"✅ Success: ±{accuracy}m accuracy")
                results.append((method_name, location))
            else:
                print(f"❌ Not available")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Show comparison
    if results:
        print(f"\n📊 ACCURACY COMPARISON")
        print("=" * 30)
        results.sort(key=lambda x: x[1].get('accuracy', float('inf')))
        
        for i, (method, location) in enumerate(results, 1):
            accuracy = location.get('accuracy', 0)
            print(f"{i}. {method}: ±{accuracy}m")
        
        # Show best result
        best_method, best_location = results[0]
        print(f"\n🏆 BEST METHOD: {best_method}")
        print(service.get_location_accuracy_report())
    else:
        print("\n❌ No location methods available")

if __name__ == "__main__":
    test_location_accuracy()