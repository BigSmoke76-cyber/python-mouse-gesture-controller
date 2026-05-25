"""
Hand Gesture Mouse Controller
==============================
Control your mouse cursor using hand gestures detected via your webcam.

Gestures (1 hand):
    ☝️  Index finger up          → Move cursor
    🤏  Index + Thumb pinch      → Left click
    ✌️🤏 Middle+Index+Thumb pinch → Right click
    ✋  All fingers open          → Scroll mode (move hand up/down)
    🖐️  4 fingers up (thumb down) → Minimize active window
    ✊  Fist (all fingers closed) → Pause / no action

Gestures (2 hands):
    ✋✋ Both hands open           → Open Alt+Tab window switcher
    Move hands left/right        → Navigate between windows
    ✊✊ Close hands (fist)        → Select window

Controls:
    Press 'q' to quit.

Author: Built with Antigravity
"""

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import config


# ─────────────────────────────────────────────────────────────
# Safety: PyAutoGUI failsafe — move mouse to top-left corner
# of the screen to abort instantly.
# ─────────────────────────────────────────────────────────────
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0  # Remove default pause between pyautogui calls for responsiveness


# ─────────────────────────────────────────────────────────────
# MediaPipe Hands setup
# ─────────────────────────────────────────────────────────────
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Landmark indices (MediaPipe hand model)
# Each finger has: TIP, DIP, PIP, MCP
FINGER_TIPS = [4, 8, 12, 16, 20]        # Thumb, Index, Middle, Ring, Pinky
FINGER_PIPS = [3, 6, 10, 14, 18]        # PIP joints (one below tip — used for "finger up" check)


def get_finger_states(landmarks, frame_width, frame_height):
    """
    Determine which fingers are up (extended) and which are down (folded).

    Returns a list of 5 booleans: [thumb, index, middle, ring, pinky]
    where True means the finger is up/extended.
    """
    fingers = []

    # --- Thumb ---
    # To work for both hands, we check if the thumb tip is further from the pinky base than the thumb IP joint is.
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    pinky_mcp = landmarks[17]

    dist_tip = get_distance(thumb_tip, pinky_mcp, frame_width, frame_height)
    dist_ip = get_distance(thumb_ip, pinky_mcp, frame_width, frame_height)

    if dist_tip > dist_ip:
        fingers.append(True)   # Thumb is extended
    else:
        fingers.append(False)  # Thumb is curled in

    # --- Other four fingers ---
    # A finger is "up" if its tip is above (lower y value) its PIP joint.
    for tip_idx, pip_idx in zip(FINGER_TIPS[1:], FINGER_PIPS[1:]):
        if landmarks[tip_idx].y < landmarks[pip_idx].y:
            fingers.append(True)
        else:
            fingers.append(False)

    return fingers


def get_distance(landmark1, landmark2, frame_width, frame_height):
    """
    Calculate the Euclidean distance between two landmarks in pixel space.
    """
    x1, y1 = int(landmark1.x * frame_width), int(landmark1.y * frame_height)
    x2, y2 = int(landmark2.x * frame_width), int(landmark2.y * frame_height)
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def classify_gesture(fingers, landmarks, frame_width, frame_height):
    """
    Classify the current hand pose into a named gesture.

    Args:
        fingers: List of 5 booleans from get_finger_states().
        landmarks: MediaPipe hand landmarks.
        frame_width: Frame width in pixels.
        frame_height: Frame height in pixels.

    Returns:
        A string: "MOVE", "LEFT_CLICK", "RIGHT_CLICK", "SCROLL", "FIST", or "UNKNOWN"
    """
    thumb, index, middle, ring, pinky = fingers

    # ── Fist: all fingers down ──
    if not any(fingers):
        return "FIST"

    # ── Scroll: all fingers up ──
    if all(fingers):
        return "SCROLL"

    # ── Minimize Window: 4 fingers up, thumb down ──
    if not thumb and index and middle and ring and pinky:
        return "MINIMIZE"

    # ── Check for pinch gestures (thumb + another finger close together) ──
    index_thumb_dist = get_distance(landmarks[4], landmarks[8], frame_width, frame_height)
    middle_thumb_dist = get_distance(landmarks[4], landmarks[12], frame_width, frame_height)

    is_index_pinch = index_thumb_dist < config.PINCH_THRESHOLD
    is_middle_pinch = middle_thumb_dist < config.PINCH_THRESHOLD

    # Right click: 3-finger pinch (thumb + index + middle)
    if is_index_pinch and is_middle_pinch:
        return "RIGHT_CLICK"

    # Left click: thumb + index pinch
    elif is_index_pinch:
        return "LEFT_CLICK"

    # Pre-click deadzone: stops the cursor from moving right before a click happens to prevent slipping
    elif index_thumb_dist < config.PINCH_THRESHOLD + 40 and index:
        return "PRE_CLICK"

    # ── Move: only index finger up ──
    if index and not middle and not ring and not pinky:
        return "MOVE"

    return "UNKNOWN"


def draw_hud(frame, gesture, fps, cam_index):
    """
    Draw the heads-up display overlay on the frame.
    Shows the current gesture, FPS, and camera index.
    """
    h, w, _ = frame.shape
    color = config.HUD_COLOR

    # ── Gesture label ──
    # Background rectangle for readability
    gesture_text = f"Gesture: {gesture}"
    text_size = cv2.getTextSize(gesture_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
    cv2.rectangle(frame, (10, 10), (20 + text_size[0], 20 + text_size[1] + 10), (0, 0, 0), -1)
    cv2.putText(frame, gesture_text, (15, 15 + text_size[1]),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # ── FPS counter ──
    if config.SHOW_FPS:
        fps_text = f"FPS: {int(fps)}"
        fps_size = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        cv2.rectangle(frame, (w - fps_size[0] - 20, 10),
                      (w - 5, 20 + fps_size[1] + 10), (0, 0, 0), -1)
        cv2.putText(frame, fps_text, (w - fps_size[0] - 15, 15 + fps_size[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # ── Active zone rectangle ──
    pad = config.FRAME_REDUCTION
    cv2.rectangle(frame, (pad, pad), (w - pad, h - pad), (50, 50, 50), 1)

    # ── Camera index ──
    cam_text = f"Camera: {cam_index}"
    cam_size = cv2.getTextSize(cam_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
    cam_y = 55 if config.SHOW_FPS else 20
    cv2.rectangle(frame, (w - cam_size[0] - 20, cam_y),
                  (w - 5, cam_y + cam_size[1] + 15), (0, 0, 0), -1)
    cv2.putText(frame, cam_text, (w - cam_size[0] - 15, cam_y + cam_size[1] + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

    # ── Instructions ──
    instructions = "'q' Quit | 'c' Switch Camera | Failsafe: mouse to top-left"
    cv2.putText(frame, instructions, (10, h - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (150, 150, 150), 1)


def main():
    """Main application loop."""

    # ── Camera state ──
    cam_index = config.CAMERA_INDEX

    # ── Initialize webcam ──
    cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)  # DirectShow is faster on Windows
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, config.TARGET_FPS)

    if not cap.isOpened():
        print("ERROR: Could not open webcam. Make sure no other app is using it.")
        return

    # ── Get screen dimensions ──
    screen_w, screen_h = pyautogui.size()
    print(f"Screen resolution: {screen_w} x {screen_h}")
    print(f"Camera {cam_index} | Resolution: {config.FRAME_WIDTH} x {config.FRAME_HEIGHT}")
    print("Starting hand gesture mouse controller...")
    print("Press 'q' to quit | Press 'c' to switch camera.")
    print("Move mouse to the top-left corner for emergency stop.\n")

    # ── State variables ──
    prev_x, prev_y = 0, 0           # Previous smoothed cursor position
    last_click_time = 0              # Timestamp of last click (for debouncing)
    prev_scroll_y = None             # Previous y-position for scroll delta
    prev_time = time.time()          # For FPS calculation
    fps = 0

    # Alt-Tab state variables
    is_alt_tabbing = False
    alt_tab_start_x = 0

    # ── MediaPipe Hands ──
    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:

        try:
            while True:
                # ── Capture frame ──
                ret, frame = cap.read()
                if not ret:
                    print("ERROR: Failed to read frame from webcam.")
                    break

                # Flip horizontally for mirror effect (more natural control)
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape

                # Convert BGR → RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                gesture = "NO HAND"

                if results.multi_hand_landmarks:
                    # ── Draw landmarks ──
                    if config.SHOW_LANDMARKS:
                        for hl in results.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(
                                frame, hl, mp_hands.HAND_CONNECTIONS,
                                mp_drawing_styles.get_default_hand_landmarks_style(),
                                mp_drawing_styles.get_default_hand_connections_style()
                            )

                    # ══════════════════════════════════════════
                    # 2-Hand Gesture: Alt-Tab Window Switcher
                    # ══════════════════════════════════════════
                    if len(results.multi_hand_landmarks) == 2:
                        gesture = "ALT_TAB_MODE"
                        h1_fingers = get_finger_states(results.multi_hand_landmarks[0].landmark, w, h)
                        h2_fingers = get_finger_states(results.multi_hand_landmarks[1].landmark, w, h)

                        # Both hands OPEN -> Start or navigate Alt-Tab
                        if all(h1_fingers) and all(h2_fingers):
                            # Average X coordinate of both wrists
                            cx = (results.multi_hand_landmarks[0].landmark[0].x * w +
                                  results.multi_hand_landmarks[1].landmark[0].x * w) / 2

                            if not is_alt_tabbing:
                                is_alt_tabbing = True
                                alt_tab_start_x = cx
                                pyautogui.keyDown('alt')
                                pyautogui.press('tab')
                            else:
                                # Move right/left based on X movement
                                if cx - alt_tab_start_x > config.ALT_TAB_SENSITIVITY:
                                    pyautogui.press('tab')
                                    alt_tab_start_x = cx
                                elif cx - alt_tab_start_x < -config.ALT_TAB_SENSITIVITY:
                                    pyautogui.hotkey('shift', 'tab')
                                    alt_tab_start_x = cx

                        # Hands CLOSE (fists) -> Release Alt and select window
                        elif not any(h1_fingers) or not any(h2_fingers):
                            if is_alt_tabbing:
                                pyautogui.keyUp('alt')
                                is_alt_tabbing = False

                    # ══════════════════════════════════════════
                    # 1-Hand Gesture: Mouse Control
                    # ══════════════════════════════════════════
                    else:
                        if is_alt_tabbing:
                            pyautogui.keyUp('alt')
                            is_alt_tabbing = False

                        hand_landmarks = results.multi_hand_landmarks[0]
                        landmarks = hand_landmarks.landmark

                        # ── Determine finger states & gesture ──
                        fingers = get_finger_states(landmarks, w, h)
                        gesture = classify_gesture(fingers, landmarks, w, h)

                        # ── Get index fingertip position in pixel space ──
                        index_tip = landmarks[8]
                        ix = int(index_tip.x * w)
                        iy = int(index_tip.y * h)

                        # Draw a circle on the active fingertip
                        tip_color = (0, 255, 0) if gesture == "MOVE" else (0, 0, 255) if "CLICK" in gesture else (255, 200, 0)
                        cv2.circle(frame, (ix, iy), 12, tip_color, cv2.FILLED)
                        cv2.circle(frame, (ix, iy), 15, tip_color, 2)

                        # ── Handle gestures ──
                        pad = config.FRAME_REDUCTION

                        if gesture == "MOVE":
                            # Map fingertip position (within padded zone) to full screen
                            clamped_x = np.clip(ix, pad, w - pad)
                            clamped_y = np.clip(iy, pad, h - pad)

                            # Interpolate to screen coordinates, avoiding 0,0 to prevent PyAutoGUI failsafe
                            screen_x = np.interp(clamped_x, (pad, w - pad), (1, screen_w - 2))
                            screen_y = np.interp(clamped_y, (pad, h - pad), (1, screen_h - 2))

                            # Apply EMA smoothing
                            smooth = config.SMOOTHING_FACTOR
                            curr_x = prev_x + (screen_x - prev_x) * smooth
                            curr_y = prev_y + (screen_y - prev_y) * smooth

                            # Move the cursor
                            pyautogui.moveTo(int(curr_x), int(curr_y))
                            prev_x, prev_y = curr_x, curr_y

                            # Reset scroll state
                            prev_scroll_y = None

                        elif gesture == "LEFT_CLICK":
                            current_time = time.time()
                            if current_time - last_click_time > config.CLICK_COOLDOWN:
                                pyautogui.click()
                                last_click_time = current_time
                                # Visual feedback: flash a circle
                                cv2.circle(frame, (ix, iy), 25, (0, 0, 255), 3)
                            prev_scroll_y = None

                        elif gesture == "RIGHT_CLICK":
                            current_time = time.time()
                            if current_time - last_click_time > config.CLICK_COOLDOWN:
                                pyautogui.rightClick()
                                last_click_time = current_time
                                cv2.circle(frame, (ix, iy), 25, (255, 0, 0), 3)
                            prev_scroll_y = None

                        elif gesture == "SCROLL":
                            # Use the index fingertip y-position to determine scroll direction
                            if prev_scroll_y is not None:
                                delta_y = prev_scroll_y - iy  # Positive = hand moved up = scroll up
                                if abs(delta_y) > 3:  # Dead zone to avoid micro-scrolls
                                    scroll_amount = int(delta_y / abs(delta_y)) * config.SCROLL_SPEED
                                    pyautogui.scroll(scroll_amount)
                            prev_scroll_y = iy

                        elif gesture == "MINIMIZE":
                            current_time = time.time()
                            if current_time - last_click_time > config.CLICK_COOLDOWN:
                                pyautogui.hotkey('win', 'down')
                                last_click_time = current_time
                                cv2.circle(frame, (ix, iy), 35, (255, 0, 255), 3)
                            prev_scroll_y = None

                        elif gesture == "FIST" or gesture == "PRE_CLICK":
                            # Do nothing — safe rest position or freezing right before a click
                            prev_scroll_y = None

                        else:
                            prev_scroll_y = None

                else:
                    # No hand detected — release Alt-Tab if active
                    if is_alt_tabbing:
                        pyautogui.keyUp('alt')
                        is_alt_tabbing = False
                    prev_scroll_y = None

                # ── Calculate FPS ──
                current_time = time.time()
                fps = 1.0 / (current_time - prev_time) if (current_time - prev_time) > 0 else 0
                prev_time = current_time

                # ── Draw HUD ──
                draw_hud(frame, gesture, fps, cam_index)

                # ── Show frame ──
                cv2.imshow("Hand Gesture Mouse Controller", frame)

                # ── Keyboard input ──
                key = cv2.waitKey(1) & 0xFF

                # Exit on 'q'
                if key == ord('q'):
                    print("\nExiting... Goodbye!")
                    break

                # Switch camera on 'c'
                elif key == ord('c'):
                    old_index = cam_index
                    cap.release()

                    # Try each camera index until we find one that works
                    for attempt in range(5):
                        cam_index = (old_index + 1 + attempt) % 5
                        print(f"  Trying camera {cam_index}...")
                        new_cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
                        if new_cap.isOpened():
                            ret_test, _ = new_cap.read()
                            if ret_test:
                                cap = new_cap
                                cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
                                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
                                cap.set(cv2.CAP_PROP_FPS, config.TARGET_FPS)
                                print(f"  Switched to camera {cam_index}.")
                                break
                            else:
                                new_cap.release()
                        else:
                            new_cap.release()
                    else:
                        # No working camera found, reopen the old one
                        print(f"  No other camera found. Reopening camera {old_index}.")
                        cam_index = old_index
                        cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
                        cap.set(cv2.CAP_PROP_FPS, config.TARGET_FPS)

        except KeyboardInterrupt:
            print("\nForce exited.")

    # ── Cleanup ──
    pyautogui.keyUp('alt')  # Failsafe: release Alt if stuck
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
