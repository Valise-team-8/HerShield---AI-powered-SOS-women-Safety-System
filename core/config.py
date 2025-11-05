# === Demo Configuration - Replace with Real Values ===
EMERGENCY_CONTACTS = ["+1234567890"]  # Replace with real emergency contact numbers
ALERT_EMAIL = "demo@example.com"  # Replace with real email address
TWILIO_SID = "DEMO_TWILIO_SID"  # Replace with real Twilio SID if using Twilio
TWILIO_AUTH = "DEMO_TWILIO_AUTH"  # Replace with real Twilio Auth Token
# Option 1: Use a purchased Twilio phone number
TWILIO_PHONE = None  # Will be set after purchasing
# Option 2: Use Messaging Service SID (recommended for flexibility)
TWILIO_MESSAGING_SERVICE_SID = "DEMO_MESSAGING_SID"  # Replace with real Messaging Service SID

# Note: This system works without Twilio - uses free email-to-SMS gateways
