# import os, sys, subprocess, time

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# def run(script, args=None):
#     path = os.path.join(BASE_DIR, script)
#     return subprocess.Popen([sys.executable, path] + (args or []))

# # start all three
# p1 = run("tts.py")
# p2 = run("main.py")
# p3 = run("inference.py", ["--vulkan", "--device", "Vulkan0"])

# print("Running. Press Ctrl+C to stop.")

# try:
#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     print("\nStopping...")
#     for p in [p1, p2, p3]:
#         try:
#             p.terminate()
#         except:
#             pass

import os, sys, subprocess, time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run(script, args=None):
    path = os.path.join(BASE_DIR, script)
    return subprocess.Popen([sys.executable, path] + (args or []))

# ── device selection ───────────────────────────────────────────────────────
print("Select backend:")
print("  1. Vulkan - RTX (fastest)")
print("  2. Vulkan - iGPU")
print("  3. CPU")
choice = input("Enter 1, 2 or 3 [default: 1]: ").strip() or "1"

if choice == "1":
    inf_args = ["--vulkan", "--device", "Vulkan0"]
elif choice == "2":
    inf_args = ["--vulkan", "--device", "Vulkan1"]
else:
    inf_args = ["--cpu"]

# ── launch ─────────────────────────────────────────────────────────────────
p1 = run("tts.py")
p2 = run("main.py")
p3 = run("inference.py", inf_args)

print("\nRunning. Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping...")
    for p in [p1, p2, p3]:
        try:
            p.terminate()
        except:
            pass