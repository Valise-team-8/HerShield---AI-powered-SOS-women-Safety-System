#!/usr/bin/env python3
"""
HerShield User Interface for setup and configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from pathlib import Path
from core.user_config import user_config, setup_new_user
from core.email_alert import test_email_config
from core.telegram_alert import TelegramAlert

class HerShieldUI:
    """Main UI class for HerShield setup and configuration"""

    def __init__(self, root):
        self.root = root
        self.root.title("HerShield - Personal Safety System")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Load current config
        self.config = user_config.config

        self.create_widgets()
        self.load_current_config()

    def create_widgets(self):
        """Create the main UI widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Profile Setup Tab
        self.profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.profile_frame, text="User Profile")
        self.create_profile_tab()

        # Messaging Setup Tab
        self.messaging_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.messaging_frame, text="Alert Services")
        self.create_messaging_tab()

        # Settings Tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        self.create_settings_tab()

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(fill='x', side='bottom')

    def create_profile_tab(self):
        """Create the user profile setup tab"""
        # Title
        title_label = ttk.Label(self.profile_frame, text="User Profile Setup",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Create scrollable frame
        canvas = tk.Canvas(self.profile_frame)
        scrollbar = ttk.Scrollbar(self.profile_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Basic Information Section
        basic_frame = ttk.LabelFrame(scrollable_frame, text="Basic Information", padding=10)
        basic_frame.pack(fill='x', pady=5, padx=10)

        # Name
        ttk.Label(basic_frame, text="Full Name:").grid(row=0, column=0, sticky='w', pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=2, padx=(10,0))

        # Email
        ttk.Label(basic_frame, text="Email:").grid(row=1, column=0, sticky='w', pady=2)
        self.email_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.email_var, width=40).grid(row=1, column=1, pady=2, padx=(10,0))

        # Phone
        ttk.Label(basic_frame, text="Phone:").grid(row=2, column=0, sticky='w', pady=2)
        self.phone_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.phone_var, width=40).grid(row=2, column=1, pady=2, padx=(10,0))

        # Emergency Contacts Section
        contacts_frame = ttk.LabelFrame(scrollable_frame, text="Emergency Contacts", padding=10)
        contacts_frame.pack(fill='x', pady=5, padx=10)

        ttk.Label(contacts_frame, text="Add contacts in format: Name: +1234567890").pack(anchor='w')
        self.contacts_text = scrolledtext.ScrolledText(contacts_frame, height=6, width=60)
        self.contacts_text.pack(pady=5)

        # Medical Information Section
        medical_frame = ttk.LabelFrame(scrollable_frame, text="Medical Information (Optional)", padding=10)
        medical_frame.pack(fill='x', pady=5, padx=10)

        # Blood type
        ttk.Label(medical_frame, text="Blood Type:").grid(row=0, column=0, sticky='w', pady=2)
        self.blood_var = tk.StringVar()
        ttk.Entry(medical_frame, textvariable=self.blood_var).grid(row=0, column=1, pady=2, padx=(10,0))

        # Allergies
        ttk.Label(medical_frame, text="Allergies:").grid(row=1, column=0, sticky='w', pady=2)
        self.allergies_var = tk.StringVar()
        ttk.Entry(medical_frame, textvariable=self.allergies_var).grid(row=1, column=1, pady=2, padx=(10,0))

        # Medications
        ttk.Label(medical_frame, text="Medications:").grid(row=2, column=0, sticky='w', pady=2)
        self.medications_var = tk.StringVar()
        ttk.Entry(medical_frame, textvariable=self.medications_var).grid(row=2, column=1, pady=2, padx=(10,0))

        # Conditions
        ttk.Label(medical_frame, text="Medical Conditions:").grid(row=3, column=0, sticky='w', pady=2)
        self.conditions_var = tk.StringVar()
        ttk.Entry(medical_frame, textvariable=self.conditions_var).grid(row=3, column=1, pady=2, padx=(10,0))

        # Save Button
        save_btn = ttk.Button(scrollable_frame, text="Save Profile", command=self.save_profile)
        save_btn.pack(pady=20)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_messaging_tab(self):
        """Create the messaging services setup tab"""
        title_label = ttk.Label(self.messaging_frame, text="Alert Services Setup",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Service selection
        service_frame = ttk.LabelFrame(self.messaging_frame, text="Select Alert Services", padding=10)
        service_frame.pack(fill='x', pady=5, padx=10)

        self.service_vars = {}
        services = ['twilio', 'email', 'telegram']

        for service in services:
            var = tk.BooleanVar()
            self.service_vars[service] = var
            ttk.Checkbutton(service_frame, text=service.title(),
                           variable=var, command=self.update_service_config).pack(anchor='w', pady=2)

        # Configuration frames for each service
        self.twilio_frame = self.create_twilio_config()
        self.email_frame = self.create_email_config()
        self.telegram_frame = self.create_telegram_config()

        # Test buttons
        test_frame = ttk.Frame(self.messaging_frame)
        test_frame.pack(fill='x', pady=10, padx=10)

        ttk.Button(test_frame, text="Test Email", command=self.test_email).pack(side='left', padx=5)
        ttk.Button(test_frame, text="Test Telegram", command=self.test_telegram).pack(side='left', padx=5)
        ttk.Button(test_frame, text="Save Settings", command=self.save_messaging_config).pack(side='right', padx=5)

    def create_twilio_config(self):
        """Create Twilio configuration frame"""
        frame = ttk.LabelFrame(self.messaging_frame, text="Twilio SMS Configuration", padding=10)

        ttk.Label(frame, text="Account SID:").grid(row=0, column=0, sticky='w', pady=2)
        self.twilio_sid_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.twilio_sid_var, width=50).grid(row=0, column=1, pady=2, padx=(10,0))

        ttk.Label(frame, text="Auth Token:").grid(row=1, column=0, sticky='w', pady=2)
        self.twilio_auth_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.twilio_auth_var, width=50, show="*").grid(row=1, column=1, pady=2, padx=(10,0))

        ttk.Label(frame, text="Phone Number:").grid(row=2, column=0, sticky='w', pady=2)
        self.twilio_phone_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.twilio_phone_var, width=50).grid(row=2, column=1, pady=2, padx=(10,0))

        ttk.Label(frame, text="Messaging Service SID:").grid(row=3, column=0, sticky='w', pady=2)
        self.twilio_msg_sid_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.twilio_msg_sid_var, width=50).grid(row=3, column=1, pady=2, padx=(10,0))

        return frame

    def create_email_config(self):
        """Create email configuration frame"""
        frame = ttk.LabelFrame(self.messaging_frame, text="Email Configuration", padding=10)

        ttk.Label(frame, text="SMTP Server:").grid(row=0, column=0, sticky='w', pady=2)
        self.email_server_var = tk.StringVar(value="smtp.gmail.com")
        ttk.Entry(frame, textvariable=self.email_server_var, width=40).grid(row=0, column=1, pady=2, padx=(10,0))

        ttk.Label(frame, text="SMTP Port:").grid(row=1, column=0, sticky='w', pady=2)
        self.email_port_var = tk.StringVar(value="587")
        ttk.Entry(frame, textvariable=self.email_port_var, width=10).grid(row=1, column=1, sticky='w', pady=2, padx=(10,0))

        ttk.Label(frame, text="Email Address:").grid(row=2, column=0, sticky='w', pady=2)
        self.email_user_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.email_user_var, width=40).grid(row=2, column=1, pady=2, padx=(10,0))

        ttk.Label(frame, text="App Password:").grid(row=3, column=0, sticky='w', pady=2)
        self.email_pass_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.email_pass_var, width=40, show="*").grid(row=3, column=1, pady=2, padx=(10,0))

        return frame

    def create_telegram_config(self):
        """Create Telegram configuration frame"""
        frame = ttk.LabelFrame(self.messaging_frame, text="Telegram Bot Configuration", padding=10)

        ttk.Label(frame, text="Bot Token:").grid(row=0, column=0, sticky='w', pady=2)
        self.telegram_token_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.telegram_token_var, width=50).grid(row=0, column=1, pady=2, padx=(10,0))

        ttk.Label(frame, text="Chat IDs:").grid(row=1, column=0, sticky='w', pady=2)
        self.telegram_chats_text = scrolledtext.ScrolledText(frame, height=3, width=50)
        self.telegram_chats_text.grid(row=1, column=1, pady=2, padx=(10,0))

        ttk.Button(frame, text="Get Chat IDs", command=self.get_telegram_chats).grid(row=2, column=1, pady=5, sticky='e')

        return frame

    def create_settings_tab(self):
        """Create the settings tab"""
        title_label = ttk.Label(self.settings_frame, text="System Settings",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Voice settings
        voice_frame = ttk.LabelFrame(self.settings_frame, text="Voice Recognition", padding=10)
        voice_frame.pack(fill='x', pady=5, padx=10)

        ttk.Label(voice_frame, text="Keywords (comma-separated):").grid(row=0, column=0, sticky='w', pady=2)
        self.keywords_var = tk.StringVar(value="help,save me,emergency")
        ttk.Entry(voice_frame, textvariable=self.keywords_var).grid(row=0, column=1, pady=2, padx=(10,0))

        # Location settings
        location_frame = ttk.LabelFrame(self.settings_frame, text="Location Services", padding=10)
        location_frame.pack(fill='x', pady=5, padx=10)

        self.gps_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(location_frame, text="Enable GPS location sharing", variable=self.gps_var).pack(anchor='w')

        # Save settings button
        ttk.Button(self.settings_frame, text="Save Settings", command=self.save_settings).pack(pady=20)

    def load_current_config(self):
        """Load current configuration into UI"""
        # Profile
        user_info = self.config["user_info"]
        self.name_var.set(user_info["name"])
        self.email_var.set(user_info["email"])
        self.phone_var.set(user_info["phone"])

        # Emergency contacts
        contacts_text = "\n".join(user_info["emergency_contacts"])
        self.contacts_text.insert('1.0', contacts_text)

        # Medical info
        medical = user_info["medical_info"]
        self.blood_var.set(medical["blood_type"])
        self.allergies_var.set(", ".join(medical["allergies"]))
        self.medications_var.set(", ".join(medical["medications"]))
        self.conditions_var.set(", ".join(medical["conditions"]))

        # Messaging services
        messaging = self.config["alert_settings"]
        service = messaging["messaging_service"]

        if service:
            services = service.split(',') if ',' in service else [service]
            for svc in services:
                if svc in self.service_vars:
                    self.service_vars[svc].set(True)

        # Twilio config
        twilio = messaging["twilio_config"]
        self.twilio_sid_var.set(twilio["sid"])
        self.twilio_auth_var.set(twilio["auth_token"])
        self.twilio_phone_var.set(twilio["phone_number"])
        self.twilio_msg_sid_var.set(twilio["messaging_service_sid"])

        # Email config
        email = messaging["email_config"]
        self.email_server_var.set(email["smtp_server"])
        self.email_port_var.set(str(email["smtp_port"]))
        self.email_user_var.set(email["username"])
        self.email_pass_var.set(email["password"])

        # Telegram config
        telegram = messaging["telegram_config"]
        self.telegram_token_var.set(telegram["bot_token"])
        chats_text = "\n".join(str(chat_id) for chat_id in telegram.get("chat_ids", []))
        self.telegram_chats_text.insert('1.0', chats_text)

        # Settings
        voice_settings = self.config["voice_settings"]
        self.keywords_var.set(", ".join(voice_settings["keywords"]))

        location_settings = self.config["location_settings"]
        self.gps_var.set(location_settings["enable_gps"])

        self.update_service_config()

    def update_service_config(self):
        """Show/hide service configuration frames based on selection"""
        # Clear existing frames
        for frame in [self.twilio_frame, self.email_frame, self.telegram_frame]:
            frame.pack_forget()

        # Show selected frames
        if self.service_vars['twilio'].get():
            self.twilio_frame.pack(fill='x', pady=5, padx=10)
        if self.service_vars['email'].get():
            self.email_frame.pack(fill='x', pady=5, padx=10)
        if self.service_vars['telegram'].get():
            self.telegram_frame.pack(fill='x', pady=5, padx=10)

    def save_profile(self):
        """Save user profile"""
        try:
            # Update config
            self.config["user_info"]["name"] = self.name_var.get()
            self.config["user_info"]["email"] = self.email_var.get()
            self.config["user_info"]["phone"] = self.phone_var.get()

            # Emergency contacts
            contacts_text = self.contacts_text.get('1.0', tk.END).strip()
            contacts = [c.strip() for c in contacts_text.split('\n') if c.strip()]
            self.config["user_info"]["emergency_contacts"] = contacts

            # Medical info
            self.config["user_info"]["medical_info"]["blood_type"] = self.blood_var.get()
            self.config["user_info"]["medical_info"]["allergies"] = [a.strip() for a in self.allergies_var.get().split(',') if a.strip()]
            self.config["user_info"]["medical_info"]["medications"] = [m.strip() for m in self.medications_var.get().split(',') if m.strip()]
            self.config["user_info"]["medical_info"]["conditions"] = [c.strip() for c in self.conditions_var.get().split(',') if c.strip()]

            user_config.save_config()
            self.status_var.set("Profile saved successfully!")
            messagebox.showinfo("Success", "User profile saved!")

        except Exception as e:
            self.status_var.set(f"Error saving profile: {e}")
            messagebox.showerror("Error", f"Failed to save profile: {e}")

    def save_messaging_config(self):
        """Save messaging configuration"""
        try:
            # Update selected services
            selected_services = [svc for svc, var in self.service_vars.items() if var.get()]
            self.config["alert_settings"]["messaging_service"] = ','.join(selected_services)

            # Twilio config
            self.config["alert_settings"]["twilio_config"]["sid"] = self.twilio_sid_var.get()
            self.config["alert_settings"]["twilio_config"]["auth_token"] = self.twilio_auth_var.get()
            self.config["alert_settings"]["twilio_config"]["phone_number"] = self.twilio_phone_var.get()
            self.config["alert_settings"]["twilio_config"]["messaging_service_sid"] = self.twilio_msg_sid_var.get()

            # Email config
            self.config["alert_settings"]["email_config"]["smtp_server"] = self.email_server_var.get()
            self.config["alert_settings"]["email_config"]["smtp_port"] = int(self.email_port_var.get())
            self.config["alert_settings"]["email_config"]["username"] = self.email_user_var.get()
            self.config["alert_settings"]["email_config"]["password"] = self.email_pass_var.get()

            # Telegram config
            self.config["alert_settings"]["telegram_config"]["bot_token"] = self.telegram_token_var.get()
            chats_text = self.telegram_chats_text.get('1.0', tk.END).strip()
            chat_ids = [int(chat_id.strip()) for chat_id in chats_text.split('\n') if chat_id.strip()]
            self.config["alert_settings"]["telegram_config"]["chat_ids"] = chat_ids

            user_config.save_config()
            self.status_var.set("Messaging configuration saved!")
            messagebox.showinfo("Success", "Messaging configuration saved!")

        except Exception as e:
            self.status_var.set(f"Error saving messaging config: {e}")
            messagebox.showerror("Error", f"Failed to save messaging config: {e}")

    def save_settings(self):
        """Save system settings"""
        try:
            # Voice settings
            keywords = [k.strip() for k in self.keywords_var.get().split(',') if k.strip()]
            self.config["voice_settings"]["keywords"] = keywords

            # Location settings
            self.config["location_settings"]["enable_gps"] = self.gps_var.get()

            user_config.save_config()
            self.status_var.set("Settings saved successfully!")
            messagebox.showinfo("Success", "Settings saved!")

        except Exception as e:
            self.status_var.set(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def test_email(self):
        """Test email configuration"""
        if test_email_config():
            messagebox.showinfo("Success", "Email configuration is working!")
        else:
            messagebox.showerror("Error", "Email configuration test failed. Check your settings.")

    def test_telegram(self):
        """Test Telegram configuration"""
        alert = TelegramAlert()
        if alert.config["bot_token"]:
            messagebox.showinfo("Info", "Telegram bot configured. Send a test message to check chat IDs.")
        else:
            messagebox.showerror("Error", "Telegram bot token not configured.")

    def get_telegram_chats(self):
        """Get Telegram chat IDs"""
        from core.telegram_alert import get_chat_updates
        try:
            get_chat_updates()
            messagebox.showinfo("Info", "Check console output for chat IDs, then update the Chat IDs field.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get chat updates: {e}")

def main():
    """Main function to run the UI"""
    root = tk.Tk()
    app = HerShieldUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()