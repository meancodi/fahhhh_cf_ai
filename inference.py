import os, sys, time, subprocess
from PIL import Image

LLAMA_CLI_VULKAN = "./llama-bin-vulkan/llama-mtmd-cli.exe"
LLAMA_CLI_CPU    = "./llama-bin/llama-mtmd-cli.exe"
MODEL_PATH       = "./models/qwen2.5-vl-3b/Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf"
MMPROJ           = "./models/qwen2.5-vl-3b/mmproj-Qwen2.5-VL-3B-Instruct-Q8_0.gguf"

TRIGGER_FILE     = "trigger.txt"
OUTPUT_FILE      = "output.txt"
TEMP_IMAGE       = "./temp_capture.png"

PROMPT = (
    "This is a screenshot of a computer screen. "
    "Describe exactly what is shown: if it is a chart describe the data and trends, "
    "if it is code describe what it does, if it is a UI describe the elements. "
    "Be specific and concise. One to two sentences only."
)

def get_backend():
    if len(sys.argv) > 1 and sys.argv[1] == "--cpu":
        return "cpu"
    elif len(sys.argv) > 1 and sys.argv[1] == "--vulkan":
        return "vulkan"
    else:
        print("Select inference backend:")
        print("  1. Vulkan (recommended, uses iGPU/dGPU)")
        print("  2. CPU only")
        choice = input("Enter 1 or 2: ").strip()
        return "vulkan" if choice == "1" else "cpu"

def preprocess_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img.thumbnail((672, 672))
    img.save(TEMP_IMAGE)
    return TEMP_IMAGE

# def describe_image(image_path, backend):
#     processed = preprocess_image(image_path)

#     cli = LLAMA_CLI_VULKAN if backend == "vulkan" else LLAMA_CLI_CPU
#     ngl = "999" if backend == "vulkan" else "0"

#     cmd = [
#         cli,
#         "-m",       MODEL_PATH,
#         "--mmproj", MMPROJ,
#         "--image",  processed,
#         "-p",       PROMPT,
#         "-n",       "80",
#         "--temp",   "0",
#         "-t",       "16",
#         "-ngl",     ngl,
#         "-c",       "4096",
#     ]

#     result = subprocess.run(cmd, capture_output=True, text=True)

#     # Clean up temp file
#     if os.path.exists(TEMP_IMAGE):
#         os.remove(TEMP_IMAGE)

#     return result.stdout.strip()


def describe_image(image_path, backend, vulkan_device=None):
    t0 = time.time()
    processed = preprocess_image(image_path)
    print(f"Preprocess: {time.time()-t0:.2f}s")

    cli = LLAMA_CLI_VULKAN if backend == "vulkan" else LLAMA_CLI_CPU
    ngl = "999" if backend == "vulkan" else "0"

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
    if backend == "vulkan" and vulkan_device:
        cmd += ["--device", vulkan_device]

    t1 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Inference: {time.time()-t1:.2f}s")

    if os.path.exists(TEMP_IMAGE):
        os.remove(TEMP_IMAGE)

    return result.stdout.strip()

def main():
    backend = get_backend()
    print(f"\nBackend: {backend.upper()}")
    print("Watching for captures... (press Ctrl+C to stop)\n")

    while True:
        if os.path.exists(TRIGGER_FILE):
            image_path = open(TRIGGER_FILE).read().strip()
            os.remove(TRIGGER_FILE)

            print(f"Capture received: {image_path}")
            t = time.time()

            try:
                caption = describe_image(image_path, backend)
                elapsed = time.time() - t

                with open(OUTPUT_FILE, "w") as f:
                    f.write(caption)

                print(f"Done in {elapsed:.2f}s: {caption}\n")

            except Exception as e:
                print(f"Error: {e}\n")

        time.sleep(0.2)

if __name__ == "__main__":
    main()