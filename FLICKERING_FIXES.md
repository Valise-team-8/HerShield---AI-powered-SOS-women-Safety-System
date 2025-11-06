# HerShield Flickering Fixes

## Problem
The immediate emergency protocol window was flickering due to harsh animations.

## Root Causes
1. **Rapid Alpha Changes**: The urgent animation was changing window transparency from 0.8 to 1.0 every 300ms
2. **Harsh Color Flashing**: Text colors were switching between white and yellow every 500ms
3. **Multiple Dialog Creation**: Potential for multiple dialogs to be created simultaneously

## Solutions Applied

### 1. Smooth Alpha Animation
**Before:**
```python
new_alpha = 0.8 if current_alpha >= 1.0 else 1.0
self.dialog.attributes('-alpha', new_alpha)
self.dialog.after(300, urgent_pulse)  # Harsh 300ms jumps
```

**After:**
```python
self.pulse_alpha += self.pulse_direction * 0.05  # Gradual changes
# Range: 0.85 to 1.0 (less dramatic)
self.dialog.after(100, smooth_pulse)  # Smoother 100ms updates
```

### 2. Gentle Color Transitions
**Before:**
```python
new_color = "yellow" if current_color == "white" else "white"  # Harsh switching
self.dialog.after(500, flash)  # Slow, jarring updates
```

**After:**
```python
# Smooth color interpolation
red = int(255)
green = int(255) 
blue = int(255 - (intensity * 100))  # Gradual yellow tint
self.dialog.after(150, gentle_flash)  # Faster, smoother updates
```

### 3. Prevent Multiple Dialogs
**Before:**
```python
ImmediateEmergencyDialog(self.root, text, keywords, alert_count, alert_id)
```

**After:**
```python
if not hasattr(self, 'immediate_dialog') or not self.immediate_dialog:
    self.immediate_dialog = ImmediateEmergencyDialog(...)
```

## Animation Parameters

### Smooth Pulsing
- **Update Rate**: 100ms (10 FPS) for smooth motion
- **Alpha Range**: 0.85 to 1.0 (subtle effect)
- **Step Size**: 0.05 per frame (gradual changes)

### Gentle Color Flashing  
- **Update Rate**: 150ms for smooth color transitions
- **Color Range**: White to light yellow (subtle tint)
- **Transition**: Mathematical interpolation instead of hard switching

## Testing
- Created `test_emergency_dialog.py` to verify smooth animations
- Tested with 60fps-like smoothness (50ms updates)
- Confirmed no harsh flickering or jarring effects

## Result
✅ Emergency dialogs now have smooth, professional animations without flickering
✅ Maintains urgency while being visually comfortable
✅ Prevents multiple dialog creation conflicts