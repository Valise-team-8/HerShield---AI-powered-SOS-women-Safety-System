# AI Powered SOS Application

Women Safety & Emergency Response System

## Features

✅ **Custom Keywords** - Set your own safe word ("Help", "Red", "Code", etc.)  
✅ **Double-Tap Emergency** - Tap twice within 7 seconds to confirm  
✅ **AI Detection** - Auto-detects screams, distress, physical struggle  
✅ **Auto-Confirm** - AI confirms emergency if you can't tap  
✅ **Emergency Calling** - Calls police (100), ambulance (108) automatically  
✅ **Live Streaming** - Real-time video/audio to cloud  
✅ **Offline Mode** - SMS alerts when no internet  
✅ **Evidence Safe** - Cloud backup even if phone destroyed  

## Quick Start

### Desktop
```bash
pip install -r requirements.txt
python main_redesigned.py
```

### Mobile (Android)
```bash
pip install buildozer cython
buildozer android debug
# Install bin/aisos-1.0-arm64-v8a-debug.apk on phone
```

## How to Use

### Emergency Activation
1. **Tap Button** - Tap red button twice within 7 seconds
2. **Voice** - Say your custom keyword ("Help", "Red", etc.)

### What Happens
- 📞 Calls police & ambulance
- 📱 Alerts emergency contacts
- 📍 Shares live location
- 📹 Records video evidence
- 🎤 Records audio evidence
- ☁️ Uploads to cloud

## Configuration

### Custom Keywords
```python
from core.custom_keyword_manager import keyword_manager
keyword_manager.add_keyword("help")
keyword_manager.add_keyword("red")
```

### Emergency Contacts
Edit `config/user_config.json`

### SMS (Offline Mode)
Create `config/sms_config.json`:
```json
{
  "twilio_account_sid": "YOUR_SID",
  "twilio_auth_token": "YOUR_TOKEN",
  "twilio_phone_number": "+1234567890"
}
```

## Testing
```bash
python test_all_features.py
```

## Project Structure
```
core/
├── custom_keyword_manager.py    # Custom keywords
├── double_tap_detector.py       # 7-second tap system
├── ai_7second_analyzer.py       # AI analysis
├── emergency_caller.py          # Call services
├── live_streaming.py            # Video/audio streaming
├── sms_service.py               # Offline SMS
├── distress_detection.py        # Video distress detection
└── firebase_service.py          # Cloud storage

main_redesigned.py               # Desktop UI
mobile_app.py                    # Mobile UI
buildozer.spec                   # Android build config
```

## Requirements

- Python 3.8+
- Camera (optional)
- Microphone (optional)
- GPS (optional)
- Internet (optional - works offline)

## License

Open Source

## Support

Emergency: Call 100 (Police) or 108 (Ambulance)
