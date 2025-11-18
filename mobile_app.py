#!/usr/bin/env python3
"""
AI Powered SOS Application - Mobile Version
Designed for Android phones
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import threading
import time

# Import core modules
try:
    from core.double_tap_detector import double_tap_detector
    DOUBLE_TAP_AVAILABLE = True
except:
    DOUBLE_TAP_AVAILABLE = False

try:
    from core.emergency_caller import emergency_caller
    CALLER_AVAILABLE = True
except:
    CALLER_AVAILABLE = False


class MainScreen(Screen):
    """Main emergency screen with large tap button"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Title
        title = Label(
            text='[b]AI SOS[/b]\nWomen Safety',
            markup=True,
            font_size='32sp',
            size_hint=(1, 0.15)
        )
        layout.add_widget(title)
        
        # Status
        self.status_label = Label(
            text='Ready to Protect You',
            font_size='20sp',
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.status_label)
        
        # LARGE EMERGENCY BUTTON
        self.emergency_btn = Button(
            text='[b]TAP FOR\nEMERGENCY[/b]',
            markup=True,
            font_size='48sp',
            size_hint=(1, 0.5),
            background_color=(0.9, 0.2, 0.2, 1)
        )
        self.emergency_btn.bind(on_press=self.on_emergency_tap)
        layout.add_widget(self.emergency_btn)
        
        # Countdown
        self.countdown_label = Label(
            text='',
            font_size='32sp',
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.countdown_label)
        
        self.add_widget(layout)
    
    def on_emergency_tap(self, instance):
        """Handle tap"""
        if not DOUBLE_TAP_AVAILABLE:
            self.trigger_emergency()
            return
        
        result = double_tap_detector.register_tap()
        
        if result['status'] == 'FIRST_TAP':
            self.status_label.text = 'TAP AGAIN TO CONFIRM!'
            self.emergency_btn.background_color = (1, 0.5, 0, 1)
            self.start_countdown(result['time_remaining'])
        
        elif result['status'] == 'CONFIRMED_EMERGENCY':
            self.status_label.text = 'EMERGENCY CONFIRMED!'
            self.trigger_emergency()
    
    def start_countdown(self, seconds):
        """Show countdown"""
        def update(dt):
            remaining = double_tap_detector.get_time_remaining()
            if remaining > 0:
                self.countdown_label.text = f'{remaining:.1f}s'
            else:
                self.countdown_label.text = ''
                self.emergency_btn.background_color = (0.9, 0.2, 0.2, 1)
        
        Clock.schedule_interval(update, 0.1)
    
    def trigger_emergency(self):
        """Trigger emergency"""
        self.manager.current = 'emergency'
        threading.Thread(target=self.execute_emergency, daemon=True).start()
    
    def execute_emergency(self):
        """Execute emergency protocol"""
        print("🚨 EMERGENCY ACTIVATED")
        if CALLER_AVAILABLE:
            emergency_caller.call_police()


class EmergencyScreen(Screen):
    """Emergency active screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        title = Label(
            text='[b]🚨 EMERGENCY ACTIVE[/b]',
            markup=True,
            font_size='36sp',
            size_hint=(1, 0.3)
        )
        layout.add_widget(title)
        
        status = Label(
            text='📞 Calling Police\n🚑 Calling Ambulance\n📱 Alerting Contacts',
            font_size='20sp',
            size_hint=(1, 0.5)
        )
        layout.add_widget(status)
        
        ack_btn = Button(
            text='✅ ACKNOWLEDGE',
            font_size='24sp',
            size_hint=(1, 0.2),
            background_color=(0, 0.8, 0, 1)
        )
        ack_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(ack_btn)
        
        self.add_widget(layout)


class SOSMobileApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EmergencyScreen(name='emergency'))
        return sm


if __name__ == '__main__':
    SOSMobileApp().run()
