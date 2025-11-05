#!/usr/bin/env python3
"""
Voice alert system for emergency services using Twilio
Makes calls to emergency numbers with confirmation and voicemail
"""

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from core.config import TWILIO_SID, TWILIO_AUTH, TWILIO_PHONE, TWILIO_MESSAGING_SERVICE_SID
from core.user_config import user_config
import datetime

# Emergency numbers for India
EMERGENCY_NUMBERS = {
    "police": ["100", "112"],
    "medical": ["102", "108"]
}

def generate_twiml_message(reason, location):
    """Generate TwiML for voice call with confirmation and voicemail"""
    response = VoiceResponse()

    # Initial message
    response.say("Emergency alert from HerShield safety system. "
                f"Reason: {reason}. Location: {location}. "
                "Press 1 to confirm you are responding to this emergency. "
                "If you do not respond, a voicemail will be recorded.",
                voice='alice')

    # Gather input
    gather = response.gather(num_digits=1, action='/voice/confirm', method='POST', timeout=10)
    gather.say("Press 1 if you can respond to this emergency call.")

    # If no response, record voicemail
    response.say("No response received. Please leave a message after the beep.")
    response.record(action='/voice/voicemail', method='POST', max_length=30, transcribe=True)
    response.say("Thank you. Emergency services have been notified.")

    return str(response)

def make_emergency_call(service_type, reason, location):
    """Make voice call to emergency services"""
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)

        # Get emergency numbers for the service type
        numbers = EMERGENCY_NUMBERS.get(service_type, [])
        if not numbers:
            print(f"[ERROR] No numbers configured for {service_type}")
            return False

        # Generate TwiML
        twiml = generate_twiml_message(reason, location)

        success_count = 0
        for number in numbers:
            try:
                # Format number for India
                if not number.startswith('+91'):
                    number = f"+91{number}"

                print(f"[VOICE CALL] Calling {service_type} emergency: {number}")

                # Make the call
                call = client.calls.create(
                    to=number,
                    from_=TWILIO_PHONE or TWILIO_MESSAGING_SERVICE_SID,  # Use phone or messaging service
                    twiml=twiml,
                    timeout=30  # 30 second timeout
                )

                print(f"[VOICE CALL] Call initiated: {call.sid}")
                success_count += 1

            except Exception as e:
                print(f"[VOICE ERROR] Failed to call {number}: {e}")

        return success_count > 0

    except Exception as e:
        print(f"[VOICE ERROR] {e}")
        return False

def send_voice_alert(reason="Emergency alert", location=None):
    """Send voice alerts to emergency services"""
    print("[VOICE ALERT] Initiating emergency voice calls...")

    if not location:
        location = "Location not available"

    # Call police
    police_success = make_emergency_call("police", reason, location)

    # Call medical
    medical_success = make_emergency_call("medical", reason, location)

    if police_success or medical_success:
        print("[VOICE ALERT] Emergency calls initiated")
        return True
    else:
        print("[VOICE ERROR] Failed to initiate any emergency calls")
        return False

# Webhook handlers for TwiML (would need a web server)
def handle_voice_confirmation():
    """Handle confirmation response from emergency services"""
    response = VoiceResponse()
    response.say("Emergency confirmed. Help is on the way.", voice='alice')
    return str(response)

def handle_voicemail():
    """Handle voicemail recording"""
    response = VoiceResponse()
    response.say("Voicemail recorded. Emergency services notified.", voice='alice')
    return str(response)