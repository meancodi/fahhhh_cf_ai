import os, sys, subprocess, time

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
CUDA_BIN  = os.path.join(BASE_DIR, "llama-bin-cuda",   "llama-mtmd-cli.exe")
VULKAN_BIN = os.path.join(BASE_DIR, "llama-bin-vulkan", "llama-mtmd-cli.exe")

NVIDIA_KEYWORDS = ["NVIDIA", "GeForce", "Quadro", "RTX", "GTX"]

def run(script, args=None):
    path = os.path.join(BASE_DIR, script)
    return subprocess.Popen([sys.executable, path] + (args or []))

def list_vulkan_devices():
    if not os.path.exists(VULKAN_BIN):
        return []
    try:
        result = subprocess.run(
            [VULKAN_BIN, "--list-devices"],
            capture_output=True, text=True, timeout=10
        )
        devices = []
        for line in (result.stderr + result.stdout).splitlines():
            if line.strip().startswith("Vulkan"):
                parts = line.strip().split(":", 1)
                if len(parts) == 2:
                    devices.append((parts[0].strip(), parts[1].strip()))
        return devices
    except Exception:
        return []

# ── build menu ─────────────────────────────────────────────────────────────
options = []

for dev_id, dev_name in list_vulkan_devices():
    short = dev_name.split("(")[0].strip()[:45]
    is_nvidia = any(kw in dev_name for kw in NVIDIA_KEYWORDS)

    if is_nvidia and os.path.exists(CUDA_BIN):
        options.append((f"CUDA  — {short}", ["--cuda"]))

    options.append((f"Vulkan — {short} ({dev_id})", ["--vulkan", "--device", dev_id]))

options.append(("CPU only", ["--cpu"]))

# ── prompt ─────────────────────────────────────────────────────────────────
print("\nLens — Select backend:")
for i, (label, _) in enumerate(options, 1):
    print(f"  {i}. {label}")

raw = input(f"\nEnter 1-{len(options)} [default: 1]: ").strip() or "1"
try:
    idx = max(0, min(int(raw) - 1, len(options) - 1))
except ValueError:
    idx = 0

label, inf_args = options[idx]
print(f"\nUsing: {label}\n")

# ── launch ─────────────────────────────────────────────────────────────────
p1 = run("tts.py")
p2 = run("main.py")
p3 = run("inference.py", inf_args)

print("Running. Press Ctrl+C to stop.")

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