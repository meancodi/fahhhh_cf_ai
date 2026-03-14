# import keyboard
# import subprocess
# import sys

# def launch_capture():
#     subprocess.Popen([sys.executable, "screen_capture.py"])

# keyboard.add_hotkey("alt+shift+~", launch_capture)

# print("Hotkey active: Alt+Shift+~")
# keyboard.wait()

import keyboard
import subprocess
import sys

capture_proc = None


def launch_capture():
    global capture_proc

    # prevent duplicate capture windows
    if capture_proc and capture_proc.poll() is None:
        print("[HOTKEY] Capture already running")
        return

    print("[HOTKEY] Launching capture")

    capture_proc = subprocess.Popen(
        [sys.executable, "screen_capture.py"]
    )


keyboard.add_hotkey("alt+shift+~", launch_capture)

print("Hotkey active: Alt+Shift+~")

while True:
    keyboard.wait()