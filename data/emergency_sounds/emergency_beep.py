
import time
import sys
import os

def emergency_beep():
    """Create emergency beeping sound"""
    for i in range(10):
        if os.name == 'nt':  # Windows
            import winsound
            winsound.Beep(1000, 500)  # 1000Hz for 500ms
            time.sleep(0.2)
            winsound.Beep(1500, 500)  # 1500Hz for 500ms
            time.sleep(0.2)
        else:  # Unix/Linux
            print("\a", end="", flush=True)  # System bell
            time.sleep(0.5)

if __name__ == "__main__":
    emergency_beep()
