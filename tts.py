# import os, time, platform, subprocess

# OUTPUT_FILE = "output.txt"

# def speak(text):
#     system = platform.system()
#     if system == "Windows":
#         # Write text to temp file to avoid any quote/special char issues
#         temp_file = "./temp_speech.txt"
#         with open(temp_file, "w", encoding="utf-8") as f:
#             f.write(text)
#         subprocess.run([
#             "powershell", "-Command",
#             f'Add-Type -AssemblyName System.Speech; '
#             f'$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
#             f'$s.Speak([System.IO.File]::ReadAllText("{temp_file}"))'
#         ])
#         os.remove(temp_file)
#     elif system == "Linux":
#         subprocess.run(["espeak", text])
#     elif system == "Darwin":
#         subprocess.run(["say", text])
        
# print("TTS ready. Watching for descriptions...\n")

# while True:
#     if os.path.exists(OUTPUT_FILE):
#         text = open(OUTPUT_FILE).read().strip()
#         os.remove(OUTPUT_FILE)
#         if text:
#             print(f"Speaking: {text}")
#             speak(text)
#     time.sleep(0.2)

import os
import time
import platform
import subprocess

OUTPUT_FILE = "output.txt"
TEMP_FILE = "speech.txt"

system = platform.system()

print("TTS ready")


speech_proc = None


def stop_speech():
    global speech_proc

    if speech_proc and speech_proc.poll() is None:

        try:
            if system == "Windows":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(speech_proc.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                speech_proc.kill()
        except:
            pass


def speak(text):

    global speech_proc

    stop_speech()

    with open(TEMP_FILE, "w", encoding="utf-8") as f:
        f.write(text)

    if system == "Windows":

        cmd = [
            "powershell",
            "-Command",
            f'Add-Type -AssemblyName System.Speech; '
            f'$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
            f'$s.Speak([System.IO.File]::ReadAllText("{TEMP_FILE}"))'
        ]

        speech_proc = subprocess.Popen(cmd)

    elif system == "Linux":

        speech_proc = subprocess.Popen(
            ["espeak", "-f", TEMP_FILE]
        )

    elif system == "Darwin":

        speech_proc = subprocess.Popen(
            ["say", "-f", TEMP_FILE]
        )


while True:

    if os.path.exists(OUTPUT_FILE):

        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                text = f.read().strip()

            os.remove(OUTPUT_FILE)

            if text:
                print("Speaking:", text)
                speak(text)

        except Exception as e:
            print("TTS error:", e)

    time.sleep(0.2)