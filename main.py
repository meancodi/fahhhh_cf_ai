# # import keyboard
# # import subprocess
# # import sys

# # def launch_capture():
# #     subprocess.Popen([sys.executable, "screen_capture.py"])

# # keyboard.add_hotkey("alt+shift+~", launch_capture)

# # print("Hotkey active: Alt+Shift+~")
# # keyboard.wait()

# import keyboard
# import subprocess
# import sys

# capture_proc = None


# def launch_capture():
#     global capture_proc

#     # prevent duplicate capture windows
#     if capture_proc and capture_proc.poll() is None:
#         print("[HOTKEY] Capture already running")
#         return

#     print("[HOTKEY] Launching capture")

#     capture_proc = subprocess.Popen(
#         [sys.executable, "screen_capture.py"]
#     )


# keyboard.add_hotkey("alt+shift+~", launch_capture)

# print("Hotkey active: Alt+Shift+~")

# while True:
#     keyboard.wait()

import keyboard
import subprocess
import sys
import time

capture_proc = None
last_trigger = 0
COOLDOWN = 2.0

def launch_capture():
    global capture_proc, last_trigger

    now = time.time()
    if now - last_trigger < COOLDOWN:
        return

    if capture_proc and capture_proc.poll() is None:
        print("[HOTKEY] Capture already running")
        return

    last_trigger = now
    print("[HOTKEY] Launching capture")
    capture_proc = subprocess.Popen([sys.executable, "screen_capture.py"])

keyboard.add_hotkey("alt+shift+~", launch_capture)

print("Hotkey active: Alt+Shift+~")
keyboard.wait()  # single blocking wait — no loop needed