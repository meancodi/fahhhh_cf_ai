import subprocess, sys

# Set to "Vulkan0" for RTX, "Vulkan1" for iGPU, None for auto
VULKAN_DEVICE = "Vulkan0"

inf_args = [sys.executable, "inference.py", "--vulkan"]
if VULKAN_DEVICE:
    inf_args += ["--device", VULKAN_DEVICE]

procs = [
    subprocess.Popen([sys.executable, "main.py"]),
    subprocess.Popen([sys.executable, "tts.py"]),
    subprocess.Popen(inf_args),
]

print("All processes started. Press Ctrl+C to stop.\n")

try:
    for p in procs:
        p.wait()
except KeyboardInterrupt:
    print("\nStopping...")
    for p in procs:
        p.terminate()