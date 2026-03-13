import subprocess, sys, time

LLAMA_CLI = "./llama-bin-cuda/llama-mtmd-cli.exe"
MODEL_PATH = "./models/qwen2.5-vl-3b/Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf"
MMPROJ     = "./models/qwen2.5-vl-3b/mmproj-Qwen2.5-VL-3B-Instruct-Q8_0.gguf"

image_path = sys.argv[1] if len(sys.argv) > 1 else "test.png"

prompt = (
    "This is a screenshot of a computer screen. "
    "Describe exactly what is shown: if it is a chart describe the data and trends, "
    "if it is code describe what it does, if it is a UI describe the elements. "
    "Be specific and concise. One to two sentences only."
)

cmd = [
    LLAMA_CLI,
    "-m",       MODEL_PATH,
    "--mmproj", MMPROJ,
    "--image",  image_path,
    "-p",       prompt,
    "-n",       "80",
    "--temp",   "0",
    "-t",       "16",
    "-ngl",     "999",
]

print("Running inference...")
# Before subprocess, time just the image encoding by running with -n 1
cmd_vision_only = cmd.copy()
cmd_vision_only[cmd_vision_only.index("-n") + 1] = "1"
t = time.time()
subprocess.run(cmd_vision_only, capture_output=True, text=True)
print(f"Vision encoder time: {time.time()-t:.2f}s")

# Then full run
t = time.time()
result = subprocess.run(cmd, capture_output=True, text=True)
print(f"Full inference time: {time.time()-t:.2f}s")

print("Response:", result.stdout.strip())
if result.returncode != 0:
    print("stderr:", result.stderr[-500:])