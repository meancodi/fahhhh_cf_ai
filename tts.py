import os, time, platform, subprocess

OUTPUT_FILE = "output.txt"

def speak(text):
    system = platform.system()
    if system == "Windows":
        # Write text to temp file to avoid any quote/special char issues
        temp_file = "./temp_speech.txt"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(text)
        subprocess.run([
            "powershell", "-Command",
            f'Add-Type -AssemblyName System.Speech; '
            f'$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
            f'$s.Speak([System.IO.File]::ReadAllText("{temp_file}"))'
        ])
        os.remove(temp_file)
    elif system == "Linux":
        subprocess.run(["espeak", text])
    elif system == "Darwin":
        subprocess.run(["say", text])
        
print("TTS ready. Watching for descriptions...\n")

while True:
    if os.path.exists(OUTPUT_FILE):
        text = open(OUTPUT_FILE).read().strip()
        os.remove(OUTPUT_FILE)
        if text:
            print(f"Speaking: {text}")
            speak(text)
    time.sleep(0.2)