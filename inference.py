import os, sys, time, subprocess
from PIL import Image

LLAMA_CLI_CUDA   = "./llama-bin-cuda/llama-mtmd-cli.exe"
LLAMA_CLI_VULKAN = "./llama-bin-vulkan/llama-mtmd-cli.exe"
LLAMA_CLI_CPU    = "./llama-bin/llama-mtmd-cli.exe"
MODEL_PATH       = "./models/qwen2.5-vl-3b/Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf"
MMPROJ           = "./models/qwen2.5-vl-3b/mmproj-Qwen2.5-VL-3B-Instruct-Q8_0.gguf"

TRIGGER_FILE = "trigger.txt"
OUTPUT_FILE  = "output.txt"
TEMP_IMAGE   = "./temp_capture.png"

PROMPT = (
    "This is a screenshot of a computer screen. "
    "Describe exactly what is shown: if it is a chart describe the data and trends, "
    "if it is code describe what it does, if it is a UI describe the elements. "
    "Be specific and concise. One to two sentences only."
)

def get_backend():
    args = sys.argv[1:]
    if "--cpu" in args:
        backend = "cpu"
    elif "--cuda" in args:
        backend = "cuda"
    else:
        backend = "vulkan"

    device = None
    if "--device" in args:
        idx = args.index("--device")
        if idx + 1 < len(args):
            device = args[idx + 1]

    return backend, device

def preprocess_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img.thumbnail((672, 672))
    img.save(TEMP_IMAGE)
    return TEMP_IMAGE

def describe_image(image_path, backend, vulkan_device=None):
    t0 = time.time()
    processed = preprocess_image(image_path)
    print(f"Preprocess: {time.time()-t0:.2f}s")

    if backend == "cuda":
        cli = LLAMA_CLI_CUDA
        ngl = "999"
    elif backend == "vulkan":
        cli = LLAMA_CLI_VULKAN
        ngl = "999"
    else:
        cli = LLAMA_CLI_CPU
        ngl = "0"

    cmd = [
        cli,
        "-m",       MODEL_PATH,
        "--mmproj", MMPROJ,
        "--image",  processed,
        "-p",       PROMPT,
        "-n",       "80",
        "--temp",   "0",
        "-t",       "16",
        "-ngl",     ngl,
        "-c",       "4096",
    ]

    # Vulkan device selection; CUDA auto-detects — no --device flag needed
    if backend == "vulkan" and vulkan_device:
        cmd += ["--device", vulkan_device]

    t1 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Inference: {time.time()-t1:.2f}s")

    if os.path.exists(TEMP_IMAGE):
        os.remove(TEMP_IMAGE)

    return result.stdout.strip()

def main():
    backend, device = get_backend()
    print("Device    :", device or "auto")
    print(f"Backend   : {backend.upper()}")
    print("Watching for captures… (Ctrl+C to stop)\n")

    while True:
        if os.path.exists(TRIGGER_FILE):
            content = open(TRIGGER_FILE).read().strip()
            os.remove(TRIGGER_FILE)

            if content == "CANCELLED":
                print("Capture cancelled — skipping.\n")
                continue

            image_path = content
            print(f"Capture received: {image_path}")
            t = time.time()

            try:
                caption = describe_image(image_path, backend, vulkan_device=device)
                elapsed = time.time() - t

                with open(OUTPUT_FILE, "w") as f:
                    f.write(caption)

                print(f"Done in {elapsed:.2f}s: {caption}\n")

            except Exception as e:
                print(f"Error: {e}\n")

        time.sleep(0.2)

if __name__ == "__main__":
    main()