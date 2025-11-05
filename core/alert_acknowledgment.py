#!/usr/bin/env python3
"""
Alert Acknowledgment System for HerShield
Provides keyboard shortcuts and GUI for acknowledging alerts
"""

import threading
import time
import logging
from pathlib import Path

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

from .escalation_system import escalation_system

logger = logging.getLogger(__name__)


class AlertAcknowledgmentSystem:
    """System for acknowledging active alerts"""
    
    def __init__(self):
        self.monitoring = False
        self.acknowledgment_window = None
        self.keyboard_thread = None
        
        logger.info("Alert acknowledgment system initialized")
    
    def start_monitoring(self):
        """Start monitoring for acknowledgment inputs"""
        if self.monitoring:
            return
        
        self.monitoring = True
        
        # Start keyboard monitoring if available
        if KEYBOARD_AVAILABLE:
            self.keyboard_thread = threading.Thread(
                target=self._keyboard_monitor,
                daemon=True
            )
            self.keyboard_thread.start()
            logger.info("Keyboard acknowledgment monitoring started")
        
        # Start GUI monitoring
        if TKINTER_AVAILABLE:
            self._check_for_alerts_periodically()
            logger.info("GUI acknowledgment monitoring started")
        
        print("[ACKNOWLEDGMENT] Press 'ESC' key or click GUI button to acknowledge alerts")
    
    def stop_monitoring(self):
        """Stop acknowledgment monitoring"""
        self.monitoring = False
        
        if self.acknowledgment_window:
            try:
                self.acknowledgment_window.destroy()
            except:
                pass
        
        logger.info("Alert acknowledgment monitoring stopped")
    
    def _keyboard_monitor(self):
        """Monitor keyboard for acknowledgment keys"""
        try:
            # Set up hotkeys
            keyboard.add_hotkey('esc', self._acknowledge_all_alerts)
            keyboard.add_hotkey('ctrl+shift+a', self._acknowledge_all_alerts)
            keyboard.add_hotkey('f12', self._acknowledge_all_alerts)
            
            # Keep monitoring
            while self.monitoring:
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Keyboard monitoring error: {e}")
    
    def _acknowledge_all_alerts(self):
        """Acknowledge all active alerts"""
        try:
            active_alerts = escalation_system.get_active_alerts()
            if active_alerts:
                count = escalation_system.acknowledge_all_alerts()
                print(f"[ACKNOWLEDGED] {count} alert(s) acknowledged by user")
                logger.info(f"User acknowledged {count} alerts")
                
                # Show confirmation
                if TKINTER_AVAILABLE:
                    self._show_acknowledgment_confirmation(count)
            else:
                print("[INFO] No active alerts to acknowledge")
        except Exception as e:
            logger.error(f"Failed to acknowledge alerts: {e}")
    
    def _check_for_alerts_periodically(self):
        """Periodically check for active alerts and show GUI"""
        if not self.monitoring:
            return
        
        try:
            active_alerts = escalation_system.get_active_alerts()
            
            if active_alerts and not self.acknowledgment_window:
                self._show_acknowledgment_gui(active_alerts)
            elif not active_alerts and self.acknowledgment_window:
                self._hide_acknowledgment_gui()
        
        except Exception as e:
            logger.error(f"Alert checking error: {e}")
        
        # Schedule next check
        if self.monitoring:
            threading.Timer(2.0, self._check_for_alerts_periodically).start()
    
    def _show_acknowledgment_gui(self, active_alerts):
        """Show GUI for acknowledging alerts"""
        try:
            if self.acknowledgment_window:
                return
            
            # Create acknowledgment window
            self.acknowledgment_window = tk.Toplevel()
            self.acknowledgment_window.title("🚨 EMERGENCY ALERT ACTIVE")
            self.acknowledgment_window.geometry("500x300")
            self.acknowledgment_window.configure(bg='#ff4444')
            
            # Make window stay on top
            self.acknowledgment_window.attributes('-topmost', True)
            self.acknowledgment_window.attributes('-toolwindow', True)
            
            # Center the window
            self.acknowledgment_window.update_idletasks()
            x = (self.acknowledgment_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (self.acknowledgment_window.winfo_screenheight() // 2) - (300 // 2)
            self.acknowledgment_window.geometry(f"500x300+{x}+{y}")
            
            # Alert message
            alert_label = tk.Label(
                self.acknowledgment_window,
                text="🚨 EMERGENCY ALERT ACTIVE 🚨",
                font=('Arial', 16, 'bold'),
                fg='white',
                bg='#ff4444'
            )
            alert_label.pack(pady=20)
            
            # Alert count
            count_label = tk.Label(
                self.acknowledgment_window,
                text=f"{len(active_alerts)} active alert(s)",
                font=('Arial', 12),
                fg='white',
                bg='#ff4444'
            )
            count_label.pack(pady=5)
            
            # Instructions
            instruction_label = tk.Label(
                self.acknowledgment_window,
                text="Click button below or press ESC to acknowledge",
                font=('Arial', 10),
                fg='white',
                bg='#ff4444'
            )
            instruction_label.pack(pady=10)
            
            # Acknowledge button
            acknowledge_btn = tk.Button(
                self.acknowledgment_window,
                text="ACKNOWLEDGE ALERTS",
                font=('Arial', 14, 'bold'),
                fg='white',
                bg='#cc0000',
                activebackground='#990000',
                activeforeground='white',
                command=self._acknowledge_all_alerts,
                width=20,
                height=2
            )
            acknowledge_btn.pack(pady=20)
            
            # Keyboard shortcuts info
            shortcuts_label = tk.Label(
                self.acknowledgment_window,
                text="Keyboard shortcuts: ESC, Ctrl+Shift+A, F12",
                font=('Arial', 8),
                fg='white',
                bg='#ff4444'
            )
            shortcuts_label.pack(pady=5)
            
            # Handle window close
            self.acknowledgment_window.protocol("WM_DELETE_WINDOW", self._acknowledge_all_alerts)
            
            # Bind keyboard shortcuts
            self.acknowledgment_window.bind('<Escape>', lambda e: self._acknowledge_all_alerts())
            self.acknowledgment_window.bind('<F12>', lambda e: self._acknowledge_all_alerts())
            
            # Focus the window
            self.acknowledgment_window.focus_force()
            
            logger.info("Acknowledgment GUI displayed")
            
        except Exception as e:
            logger.error(f"Failed to show acknowledgment GUI: {e}")
    
    def _hide_acknowledgment_gui(self):
        """Hide acknowledgment GUI"""
        try:
            if self.acknowledgment_window:
                self.acknowledgment_window.destroy()
                self.acknowledgment_window = None
                logger.info("Acknowledgment GUI hidden")
        except Exception as e:
            logger.error(f"Failed to hide acknowledgment GUI: {e}")
    
    def _show_acknowledgment_confirmation(self, count):
        """Show confirmation that alerts were acknowledged"""
        try:
            # Create temporary confirmation window
            confirmation = tk.Toplevel()
            confirmation.title("Alerts Acknowledged")
            confirmation.geometry("300x150")
            confirmation.configure(bg='#00aa00')
            
            # Center the window
            confirmation.update_idletasks()
            x = (confirmation.winfo_screenwidth() // 2) - (300 // 2)
            y = (confirmation.winfo_screenheight() // 2) - (150 // 2)
            confirmation.geometry(f"300x150+{x}+{y}")
            
            # Confirmation message
            msg_label = tk.Label(
                confirmation,
                text=f"✅ {count} Alert(s) Acknowledged",
                font=('Arial', 12, 'bold'),
                fg='white',
                bg='#00aa00'
            )
            msg_label.pack(pady=30)
            
            # Auto-close after 3 seconds
            confirmation.after(3000, confirmation.destroy)
            
        except Exception as e:
            logger.error(f"Failed to show confirmation: {e}")


# Global acknowledgment system instance
acknowledgment_system = AlertAcknowledgmentSystem()