"""
Configuration settings for Hand Gesture Mouse Controller.
Adjust these values to fine-tune sensitivity and behavior.
"""

# ──────────────────────────────────────────────
# Camera Settings
# ──────────────────────────────────────────────
CAMERA_INDEX = 0          # Webcam device index (0 = default camera)
FRAME_WIDTH = 640         # Capture frame width in pixels
FRAME_HEIGHT = 480        # Capture frame height in pixels
TARGET_FPS = 60           # Target camera FPS

# ──────────────────────────────────────────────
# Cursor Movement
# ──────────────────────────────────────────────
SMOOTHING_FACTOR = 0.15   # EMA smoothing (lower = smoother but laggier, higher = responsive but jittery)
FRAME_REDUCTION = 100     # Padding (px) to shrink the active hand-tracking zone inside the frame

# ──────────────────────────────────────────────
# Gesture Detection
# ──────────────────────────────────────────────
PINCH_THRESHOLD = 55      # Max pixel distance between fingertips to register a pinch
CLICK_COOLDOWN = 0.5      # Seconds to wait between registered clicks (debounce)
SCROLL_SPEED = 120        # Scroll amount per frame when in scroll mode (Windows needs large values like 120)
ALT_TAB_SENSITIVITY = 50  # Pixels to move hands horizontally to switch window

# ──────────────────────────────────────────────
# Display / HUD
# ──────────────────────────────────────────────
SHOW_FPS = True           # Show FPS counter on the video feed
SHOW_LANDMARKS = True     # Draw hand landmarks and connections
HUD_COLOR = (0, 255, 128) # Color for HUD text (BGR format — green)
