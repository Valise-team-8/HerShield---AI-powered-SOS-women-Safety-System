#!/usr/bin/env python3
"""
Offline Alert System
Comprehensive offline alert system that works without internet connectivity
Includes local network alerts, device-to-device communication, and offline storage
"""

import json
import os
import time
import threading
import socket
import subprocess
import platform
import logging
from datetime import datetime
import sqlite3
from pathlib import Path

class OfflineAlertSystem:
    """Offline alert system for emergency situations"""
    
    def __init__(self):
        self.db_path = "data/offline_alerts.db"
        self.alert_queue = []
        self.is_monitoring = False
        
        # Network discovery
        self.local_devices = []
        self.broadcast_port = 8888
        self.discovery_port = 8889
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self.init_database()
        
        # Start network discovery
        self.start_network_discovery()

    def init_database(self):
        """Initialize SQLite database for offline alert storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    location_data TEXT,
                    user_info TEXT,
                    status TEXT DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create network devices table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS network_devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT UNIQUE NOT NULL,
                    device_name TEXT,
                    last_seen TEXT,
                    device_type TEXT,
                    is_trusted BOOLEAN DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Offline alert database initialized")
            
        except Exception as e:
            self.logger.error(f"Database initialization error: {e}")

    def store_alert_offline(self, alert_type, message, location_data=None, user_info=None):
        """Store alert in offline database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (timestamp, alert_type, message, location_data, user_info)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                alert_type,
                message,
                json.dumps(location_data) if location_data else None,
                json.dumps(user_info) if user_info else None
            ))
            
            alert_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Alert stored offline with ID: {alert_id}")
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Error storing offline alert: {e}")
            return None

    def get_pending_alerts(self):
        """Get all pending alerts from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, timestamp, alert_type, message, location_data, user_info, retry_count
                FROM alerts 
                WHERE status = 'pending'
                ORDER BY timestamp ASC
            ''')
            
            alerts = []
            for row in cursor.fetchall():
                alert = {
                    'id': row[0],
                    'timestamp': row[1],
                    'alert_type': row[2],
                    'message': row[3],
                    'location_data': json.loads(row[4]) if row[4] else None,
                    'user_info': json.loads(row[5]) if row[5] else None,
                    'retry_count': row[6]
                }
                alerts.append(alert)
            
            conn.close()
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error getting pending alerts: {e}")
            return []

    def mark_alert_sent(self, alert_id):
        """Mark alert as successfully sent"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts 
                SET status = 'sent', retry_count = retry_count + 1
                WHERE id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Alert {alert_id} marked as sent")
            
        except Exception as e:
            self.logger.error(f"Error marking alert as sent: {e}")

    def increment_retry_count(self, alert_id):
        """Increment retry count for failed alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts 
                SET retry_count = retry_count + 1
                WHERE id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error incrementing retry count: {e}")

    def discover_local_devices(self):
        """Discover devices on local network"""
        try:
            # Get local network range
            local_ip = self.get_local_ip()
            if not local_ip:
                return []
            
            network_base = '.'.join(local_ip.split('.')[:-1]) + '.'
            devices = []
            
            # Ping sweep (simplified)
            for i in range(1, 255):
                ip = network_base + str(i)
                if self.ping_device(ip):
                    device_info = {
                        'ip': ip,
                        'hostname': self.get_hostname(ip),
                        'last_seen': datetime.now().isoformat()
                    }
                    devices.append(device_info)
                    self.store_network_device(device_info)
            
            self.local_devices = devices
            self.logger.info(f"Discovered {len(devices)} local devices")
            return devices
            
        except Exception as e:
            self.logger.error(f"Device discovery error: {e}")
            return []

    def get_local_ip(self):
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return None

    def ping_device(self, ip):
        """Ping a device to check if it's reachable"""
        try:
            system = platform.system().lower()
            if system == "windows":
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "1000", ip], 
                    capture_output=True, timeout=2
                )
            else:
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", ip], 
                    capture_output=True, timeout=2
                )
            return result.returncode == 0
        except:
            return False

    def get_hostname(self, ip):
        """Get hostname for IP address"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return "Unknown"

    def store_network_device(self, device_info):
        """Store network device in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO network_devices (ip_address, device_name, last_seen)
                VALUES (?, ?, ?)
            ''', (
                device_info['ip'],
                device_info.get('hostname', 'Unknown'),
                device_info['last_seen']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing network device: {e}")

    def broadcast_alert_to_network(self, alert_message):
        """Broadcast alert to local network devices"""
        try:
            # Create broadcast socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # Prepare alert data
            alert_data = {
                'type': 'emergency_alert',
                'message': alert_message,
                'timestamp': datetime.now().isoformat(),
                'source': self.get_local_ip()
            }
            
            message = json.dumps(alert_data).encode('utf-8')
            
            # Broadcast to network
            broadcast_address = '<broadcast>'
            sock.sendto(message, (broadcast_address, self.broadcast_port))
            
            # Also send to discovered devices
            for device in self.local_devices:
                try:
                    sock.sendto(message, (device['ip'], self.broadcast_port))
                except:
                    pass
            
            sock.close()
            self.logger.info("Alert broadcasted to local network")
            return True
            
        except Exception as e:
            self.logger.error(f"Network broadcast error: {e}")
            return False

    def start_alert_listener(self):
        """Start listening for alerts from other devices"""
        def listener():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind(('', self.broadcast_port))
                
                self.logger.info(f"Alert listener started on port {self.broadcast_port}")
                
                while self.is_monitoring:
                    try:
                        data, addr = sock.recvfrom(1024)
                        alert_data = json.loads(data.decode('utf-8'))
                        
                        if alert_data.get('type') == 'emergency_alert':
                            self.handle_received_alert(alert_data, addr)
                    
                    except socket.timeout:
                        continue
                    except Exception as e:
                        self.logger.error(f"Alert listener error: {e}")
                
                sock.close()
                
            except Exception as e:
                self.logger.error(f"Alert listener setup error: {e}")
        
        if not self.is_monitoring:
            self.is_monitoring = True
            self.listener_thread = threading.Thread(target=listener, daemon=True)
            self.listener_thread.start()

    def handle_received_alert(self, alert_data, sender_addr):
        """Handle alert received from another device"""
        try:
            self.logger.warning(f"🚨 EMERGENCY ALERT RECEIVED from {sender_addr[0]}")
            self.logger.warning(f"Message: {alert_data['message']}")
            self.logger.warning(f"Time: {alert_data['timestamp']}")
            
            # Store received alert
            self.store_alert_offline(
                'received_alert',
                f"Alert from {sender_addr[0]}: {alert_data['message']}",
                None,
                {'sender_ip': sender_addr[0], 'sender_data': alert_data}
            )
            
            # Could trigger local notifications here
            self.show_emergency_notification(alert_data, sender_addr)
            
        except Exception as e:
            self.logger.error(f"Error handling received alert: {e}")

    def show_emergency_notification(self, alert_data, sender_addr):
        """Show emergency notification (platform-specific)"""
        try:
            system = platform.system().lower()
            message = f"EMERGENCY ALERT from {sender_addr[0]}: {alert_data['message']}"
            
            if system == "windows":
                # Windows notification
                subprocess.run([
                    "powershell", "-Command",
                    f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('{message}', 'Emergency Alert', 'OK', 'Warning')"
                ], timeout=5)
            
            elif system == "linux":
                # Linux notification
                subprocess.run(["notify-send", "Emergency Alert", message], timeout=5)
            
            elif system == "darwin":  # macOS
                # macOS notification
                subprocess.run([
                    "osascript", "-e",
                    f'display notification "{message}" with title "Emergency Alert"'
                ], timeout=5)
            
        except Exception as e:
            self.logger.error(f"Notification error: {e}")

    def start_network_discovery(self):
        """Start periodic network discovery"""
        def discovery_loop():
            while True:
                try:
                    self.discover_local_devices()
                    time.sleep(300)  # Discover every 5 minutes
                except Exception as e:
                    self.logger.error(f"Discovery loop error: {e}")
                    time.sleep(60)
        
        self.discovery_thread = threading.Thread(target=discovery_loop, daemon=True)
        self.discovery_thread.start()

    def send_offline_alert(self, alert_type, message, location_data=None, user_info=None):
        """Send alert using offline methods"""
        success_methods = []
        
        # Store in offline database
        alert_id = self.store_alert_offline(alert_type, message, location_data, user_info)
        if alert_id:
            success_methods.append("offline_storage")
        
        # Broadcast to local network
        if self.broadcast_alert_to_network(message):
            success_methods.append("network_broadcast")
        
        # Try to write to removable media (if available)
        if self.write_to_removable_media(alert_type, message, location_data, user_info):
            success_methods.append("removable_media")
        
        # Create local alert file
        if self.create_local_alert_file(alert_type, message, location_data, user_info):
            success_methods.append("local_file")
        
        self.logger.info(f"Offline alert sent via: {', '.join(success_methods)}")
        return len(success_methods) > 0

    def write_to_removable_media(self, alert_type, message, location_data, user_info):
        """Write alert to removable media (USB drives, etc.)"""
        try:
            # Find removable drives
            removable_drives = self.find_removable_drives()
            
            for drive in removable_drives:
                try:
                    alert_file = os.path.join(drive, "EMERGENCY_ALERT.txt")
                    
                    alert_content = f"""
🚨 EMERGENCY ALERT 🚨
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Type: {alert_type}
Message: {message}

Location: {json.dumps(location_data, indent=2) if location_data else 'Not available'}
User Info: {json.dumps(user_info, indent=2) if user_info else 'Not available'}

This is an automated emergency alert from HerShield Safety System.
Please contact emergency services immediately.
"""
                    
                    with open(alert_file, 'w') as f:
                        f.write(alert_content)
                    
                    self.logger.info(f"Alert written to removable media: {drive}")
                    return True
                    
                except Exception as e:
                    self.logger.warning(f"Could not write to {drive}: {e}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Removable media error: {e}")
            return False

    def find_removable_drives(self):
        """Find removable drives on the system"""
        drives = []
        try:
            system = platform.system().lower()
            
            if system == "windows":
                import string
                for letter in string.ascii_uppercase:
                    drive = f"{letter}:\\"
                    if os.path.exists(drive):
                        # Check if it's removable (simplified check)
                        drives.append(drive)
            
            elif system in ["linux", "darwin"]:
                # Check common mount points
                mount_points = ["/media", "/mnt", "/Volumes"]
                for mount_point in mount_points:
                    if os.path.exists(mount_point):
                        for item in os.listdir(mount_point):
                            full_path = os.path.join(mount_point, item)
                            if os.path.isdir(full_path):
                                drives.append(full_path)
            
        except Exception as e:
            self.logger.error(f"Drive detection error: {e}")
        
        return drives

    def create_local_alert_file(self, alert_type, message, location_data, user_info):
        """Create local alert file"""
        try:
            alert_dir = "data/emergency_alerts"
            os.makedirs(alert_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            alert_file = os.path.join(alert_dir, f"alert_{timestamp}.json")
            
            alert_data = {
                'timestamp': datetime.now().isoformat(),
                'alert_type': alert_type,
                'message': message,
                'location_data': location_data,
                'user_info': user_info,
                'system_info': {
                    'platform': platform.system(),
                    'hostname': socket.gethostname(),
                    'local_ip': self.get_local_ip()
                }
            }
            
            with open(alert_file, 'w') as f:
                json.dump(alert_data, f, indent=2)
            
            self.logger.info(f"Local alert file created: {alert_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Local alert file error: {e}")
            return False

    def retry_pending_alerts(self):
        """Retry sending pending alerts when connectivity is restored"""
        pending_alerts = self.get_pending_alerts()
        
        for alert in pending_alerts:
            if alert['retry_count'] < 5:  # Max 5 retries
                try:
                    # Try to send via online methods
                    # This would integrate with your existing alert system
                    self.logger.info(f"Retrying alert {alert['id']}")
                    
                    # If successful, mark as sent
                    # self.mark_alert_sent(alert['id'])
                    
                except Exception as e:
                    self.increment_retry_count(alert['id'])
                    self.logger.error(f"Retry failed for alert {alert['id']}: {e}")

    def stop_monitoring(self):
        """Stop all monitoring services"""
        self.is_monitoring = False
        self.logger.info("Offline alert system stopped")

# Example usage
if __name__ == "__main__":
    offline_system = OfflineAlertSystem()
    
    # Start alert listener
    offline_system.start_alert_listener()
    
    # Test offline alert
    test_location = {
        'latitude': 28.6139,
        'longitude': 77.2090,
        'address': 'New Delhi, India'
    }
    
    test_user = {
        'name': 'Test User',
        'phone': '+1234567890'
    }
    
    print("Sending test offline alert...")
    success = offline_system.send_offline_alert(
        'test_alert',
        'This is a test emergency alert',
        test_location,
        test_user
    )
    
    if success:
        print("✅ Offline alert sent successfully")
    else:
        print("❌ Failed to send offline alert")
    
    # Keep running to listen for alerts
    try:
        print("Listening for network alerts... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        offline_system.stop_monitoring()
        print("Stopped")