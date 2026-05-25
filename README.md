# Hand Gesture Mouse Controller

A Python-based computer vision application that allows you to control your mouse, scroll, minimize windows, and cycle through the Alt-Tab menu entirely using hand gestures via your webcam. Built using OpenCV and MediaPipe. 

## Features & Gestures

### 1-Hand Gestures
- ☝️ **Move Cursor**: Index finger up, others folded.
- 🤏 **Left Click**: Pinch your index finger and thumb together.
- ✌️🤏 **Right Click**: Pinch your middle finger, index finger, and thumb together (like holding a pinch of salt).
- ✋ **Scroll Mode**: Hold all 5 fingers open and move your hand up or down to scroll.
- 🖐️ **Minimize Window**: Hold 4 fingers up, with your thumb curled down/folded in. This will minimize the active window.
- ✊ **Pause**: Make a fist to pause tracking.

### 2-Hand Gestures
- ✋✋ **Alt+Tab Menu**: Hold both hands up and open. Swipe both hands left or right to switch between windows.
- ✊✊ **Select Window**: Close your hands into fists to select the highlighted window.

### Keyboard Controls
- Press **`c`** to cycle through available webcams.
- Press **`q`** to quit the application.

## How to Run It Yourself

Since the project uses specific dependencies (like MediaPipe) that are installed in a local Python virtual environment, you should run it using the environment we set up.

1. Open a Command Prompt or PowerShell terminal.
2. Navigate to your project folder:
   ```cmd
   cd "C:\python projects\hand_gesture_mouse_controller"
   ```
3. Run the script using the virtual environment's Python:
   ```cmd
   .\venv\Scripts\python.exe main.py
   ```

## How to Set It Up on Another PC

If you want to move this project to another computer, **do not copy the `venv` folder**. Virtual environments are tied to the specific computer they were created on.

1. **Copy the code:** Copy the `.py` files, `README.md`, and `requirements.txt` to the new PC.
2. **Install Python:** Make sure the other PC has Python installed (Python 3.11 is recommended).
3. **Set it up:** Open a Command Prompt on the new PC inside the folder where you pasted the files, and run these two commands to create a fresh environment and install the correct dependencies:
   ```cmd
   python -m venv venv
   .\venv\Scripts\pip.exe install -r requirements.txt
   ```
4. **Run it:** Now you can run the app just like normal!
   ```cmd
   .\venv\Scripts\python.exe main.py
   ```

**Safety Feature:** If you ever lose control of the mouse, simply thrust the mouse cursor into the **top-left corner** of your screen. This will instantly trigger the PyAutoGUI failsafe and crash the app safely.
