import keyboard
import subprocess
import sys

def launch_capture():
    subprocess.Popen([sys.executable, "screen_capture.py"])

keyboard.add_hotkey("alt+shift+~", launch_capture)

print("Hotkey active: Alt+Shift+~")
keyboard.wait()