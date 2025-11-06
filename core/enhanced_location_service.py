#!/usr/bin/env python3
"""
Enhanced Location Service
Provides multiple methods for location detection including offline capabilities
Supports GPS, WiFi triangulation, IP-based location, and manual location sharing
"""

import json
import os
import time
import threading
import requests
from geopy.geocoders import Nominatim
import socket
import subprocess
import platform
import logging
from datetime import datetime, timedelta

class EnhancedLocationService:
    """Enhanced location service with multiple detection methods"""
    
    def __init__(self):
        self.last_location = None
        self.location_history = []
        self.location_file = "data/location_data.json"
        self.is_monitoring = False
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Initialize geocoder for reverse geocoding
        self.geocoder = Nominatim(user_agent="HerShield-Safety-System")
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load previous location data
        self.load_location_data()

    def load_location_data(self):
        """Load previous location data"""
        try:
            if os.path.exists(self.location_file):
                with open(self.location_file, 'r') as f:
                    data = json.load(f)
                    self.last_location = data.get('last_location')
                    self.location_history = data.get('history', [])
        except Exception as e:
            self.logger.error(f"Error loading location data: {e}")

    def save_location_data(self):
        """Save location data to file"""
        try:
            data = {
                'last_location': self.last_location,
                'history': self.location_history[-50:],  # Keep last 50 locations
                'last_updated': datetime.now().isoformat()
            }
            with open(self.location_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving location data: {e}")

    def get_ip_location(self):
        """Get location based on IP address with enhanced address resolution"""
        try:
            # Try multiple IP geolocation services
            services = [
                "http://ip-api.com/json/",
                "https://ipapi.co/json/",
                "https://ipinfo.io/json"
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=3)  # Faster timeout
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Parse different response formats
                        if 'lat' in data and 'lon' in data:
                            lat, lon = data['lat'], data['lon']
                        elif 'latitude' in data and 'longitude' in data:
                            lat, lon = data['latitude'], data['longitude']
                        else:
                            continue
                        
                        # Build comprehensive address
                        address_parts = []
                        if data.get('city'):
                            address_parts.append(data['city'])
                        if data.get('region', data.get('regionName')):
                            address_parts.append(data.get('region', data.get('regionName')))
                        if data.get('country'):
                            address_parts.append(data['country'])
                        
                        # Build basic address first
                        basic_address = ', '.join(address_parts) if address_parts else 'Location detected'
                        
                        # Try to get detailed address using reverse geocoding (non-blocking)
                        detailed_address = None
                        try:
                            detailed_address = self._get_detailed_address(lat, lon)
                        except:
                            pass
                        
                        location_info = {
                            'latitude': lat,
                            'longitude': lon,
                            'method': 'ip_geolocation',
                            'accuracy': 'city_level',
                            'timestamp': datetime.now().isoformat(),
                            'city': data.get('city', 'Unknown City'),
                            'region': data.get('region', data.get('regionName', 'Unknown Region')),
                            'country': data.get('country', data.get('countryCode', 'Unknown Country')),
                            'isp': data.get('isp', data.get('org', 'Unknown ISP')),
                            'address': detailed_address or basic_address
                        }
                        
                        self.logger.info(f"IP location: {lat}, {lon} ({location_info['city']})")
                        return location_info
                        
                except Exception as e:
                    self.logger.warning(f"IP service {service} failed: {e}")
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"IP location error: {e}")
            return None

    def _get_detailed_address(self, lat, lon):
        """Get detailed address from coordinates using reverse geocoding"""
        try:
            location = self.geocoder.reverse(f"{lat}, {lon}", timeout=2)
            if location and location.address:
                return location.address
        except Exception as e:
            self.logger.debug(f"Reverse geocoding failed: {e}")
        return None

    def get_wifi_location(self):
        """Get location based on WiFi networks (requires external service)"""
        try:
            # Get available WiFi networks
            wifi_networks = self._scan_wifi_networks()
            
            if not wifi_networks:
                return None
            
            # Use Google Geolocation API (requires API key)
            # For now, return None as this requires API setup
            self.logger.info("WiFi location scanning available but requires API key setup")
            return None
            
        except Exception as e:
            self.logger.error(f"WiFi location error: {e}")
            return None

    def _scan_wifi_networks(self):
        """Scan for available WiFi networks"""
        try:
            system = platform.system().lower()
            networks = []
            
            if system == "windows":
                # Windows WiFi scan
                result = subprocess.run(
                    ["netsh", "wlan", "show", "profiles"], 
                    capture_output=True, text=True, timeout=10
                )
                # Parse Windows WiFi output
                # This is a simplified version
                
            elif system == "linux":
                # Linux WiFi scan
                result = subprocess.run(
                    ["iwlist", "scan"], 
                    capture_output=True, text=True, timeout=10
                )
                # Parse Linux WiFi output
                
            elif system == "darwin":  # macOS
                # macOS WiFi scan
                result = subprocess.run(
                    ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"], 
                    capture_output=True, text=True, timeout=10
                )
                # Parse macOS WiFi output
            
            return networks
            
        except Exception as e:
            self.logger.error(f"WiFi scan error: {e}")
            return []

    def get_gps_location(self):
        """Get GPS location (placeholder for actual GPS implementation)"""
        # This would require platform-specific GPS access
        # For mobile devices, you'd use platform APIs
        # For computers with GPS, you'd use appropriate libraries
        
        self.logger.info("GPS location requires platform-specific implementation")
        return None

    def get_manual_location(self, lat, lon, description="Manual location"):
        """Set location manually"""
        try:
            location_info = {
                'latitude': float(lat),
                'longitude': float(lon),
                'method': 'manual',
                'accuracy': 'user_provided',
                'timestamp': datetime.now().isoformat(),
                'description': description
            }
            
            # Try to get address from coordinates
            try:
                location = self.geocoder.reverse(f"{lat}, {lon}")
                if location:
                    location_info['address'] = location.address
            except:
                pass
            
            return location_info
            
        except Exception as e:
            self.logger.error(f"Manual location error: {e}")
            return None

    def get_best_location(self):
        """Get the best available location using multiple methods"""
        location_methods = [
            ('google_maps', self.get_google_maps_location),
            ('gps', self.get_gps_location),
            ('wifi', self.get_wifi_location),
            ('ip', self.get_ip_location)
        ]
        
        for method_name, method_func in location_methods:
            try:
                location = method_func()
                if location:
                    self.update_location(location)
                    return location
            except Exception as e:
                self.logger.warning(f"Location method {method_name} failed: {e}")
        
        # Return last known location if no new location available
        if self.last_location:
            self.logger.info("Using last known location")
            return self.last_location
        
        return None

    def get_google_maps_location(self):
        """Get location using Google Maps API (high accuracy)"""
        try:
            from core.google_maps_location import GoogleMapsLocationService
            
            google_service = GoogleMapsLocationService()
            if google_service.api_key:
                location = google_service.get_high_accuracy_location()
                if location:
                    # Convert to our format
                    return {
                        'latitude': location['latitude'],
                        'longitude': location['longitude'],
                        'accuracy': location.get('accuracy', 100),
                        'address': location.get('address', ''),
                        'method': 'google_maps_api',
                        'timestamp': location.get('timestamp', time.time()),
                        'data_sources': location.get('data_sources', [])
                    }
            else:
                self.logger.debug("Google Maps API key not configured")
        except ImportError:
            self.logger.debug("Google Maps location service not available")
        except Exception as e:
            self.logger.error(f"Google Maps location error: {e}")
        
        return None

    def update_location(self, location_info):
        """Update current location"""
        if location_info:
            self.last_location = location_info
            self.location_history.append(location_info)
            self.save_location_data()
            
            self.logger.info(f"Location updated: {location_info['latitude']}, {location_info['longitude']} via {location_info['method']}")

    def get_location_url(self, location_info=None):
        """Get Google Maps URL for location"""
        if not location_info:
            location_info = self.last_location
        
        if not location_info:
            return "Location not available"
        
        lat = location_info['latitude']
        lon = location_info['longitude']
        return f"https://maps.google.com/?q={lat},{lon}"

    def get_location_description(self, location_info=None):
        """Get human-readable location description"""
        if not location_info:
            location_info = self.last_location
        
        if not location_info:
            return "Location not available"
        
        description_parts = []
        
        # Add coordinates
        lat = location_info['latitude']
        lon = location_info['longitude']
        description_parts.append(f"Coordinates: {lat:.6f}, {lon:.6f}")
        
        # Add address if available
        if 'address' in location_info:
            description_parts.append(f"Address: {location_info['address']}")
        elif 'city' in location_info:
            city_info = []
            if location_info.get('city'):
                city_info.append(location_info['city'])
            if location_info.get('region'):
                city_info.append(location_info['region'])
            if location_info.get('country'):
                city_info.append(location_info['country'])
            if city_info:
                description_parts.append(f"Location: {', '.join(city_info)}")
        
        # Add method and accuracy
        method = location_info.get('method', 'unknown')
        accuracy = location_info.get('accuracy', 'unknown')
        description_parts.append(f"Method: {method} ({accuracy})")
        
        # Add timestamp
        if 'timestamp' in location_info:
            try:
                timestamp = datetime.fromisoformat(location_info['timestamp'].replace('Z', '+00:00'))
                time_ago = datetime.now() - timestamp.replace(tzinfo=None)
                if time_ago.total_seconds() < 60:
                    time_str = "just now"
                elif time_ago.total_seconds() < 3600:
                    time_str = f"{int(time_ago.total_seconds() / 60)} minutes ago"
                else:
                    time_str = f"{int(time_ago.total_seconds() / 3600)} hours ago"
                description_parts.append(f"Updated: {time_str}")
            except:
                pass
        
        return "\n".join(description_parts)

    def start_location_monitoring(self, interval=300):  # 5 minutes
        """Start continuous location monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(interval,), 
            daemon=True
        )
        self.monitoring_thread.start()
        self.logger.info(f"Location monitoring started (interval: {interval}s)")

    def stop_location_monitoring(self):
        """Stop location monitoring"""
        self.is_monitoring = False
        if hasattr(self, 'monitoring_thread'):
            self.monitoring_thread.join(timeout=2)
        self.logger.info("Location monitoring stopped")

    def _monitoring_loop(self, interval):
        """Location monitoring loop"""
        while self.is_monitoring:
            try:
                location = self.get_best_location()
                if location:
                    self.logger.info(f"Location updated: {location['method']}")
                else:
                    self.logger.warning("No location available")
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Location monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute on error

    def get_emergency_location_info(self):
        """Get comprehensive location info for emergency alerts"""
        location = self.get_best_location()
        
        if not location:
            return {
                'status': 'unavailable',
                'message': 'Location services unavailable',
                'url': None,
                'description': 'Location not available'
            }
        
        return {
            'status': 'available',
            'coordinates': {
                'latitude': location['latitude'],
                'longitude': location['longitude']
            },
            'url': self.get_location_url(location),
            'description': self.get_location_description(location),
            'method': location.get('method', 'unknown'),
            'accuracy': location.get('accuracy', 'unknown'),
            'timestamp': location.get('timestamp', datetime.now().isoformat())
        }

# Backward compatibility function
def get_location():
    """Get location coordinates (backward compatibility)"""
    service = EnhancedLocationService()
    location = service.get_best_location()
    
    if location:
        return location['latitude'], location['longitude']
    else:
        # Return default coordinates if no location available
        return 0.0, 0.0

# Example usage
if __name__ == "__main__":
    service = EnhancedLocationService()
    
    print("Testing location services...")
    
    # Test IP-based location
    location = service.get_best_location()
    if location:
        print(f"Location found: {location}")
        print(f"Maps URL: {service.get_location_url()}")
        print(f"Description:\n{service.get_location_description()}")
    else:
        print("No location available")
    
    # Test manual location
    manual_loc = service.get_manual_location(28.6139, 77.2090, "New Delhi, India")
    if manual_loc:
        service.update_location(manual_loc)
        print(f"Manual location set: {service.get_location_url()}")
    
    # Test emergency location info
    emergency_info = service.get_emergency_location_info()
    print(f"Emergency location info: {emergency_info}")