import subprocess, sys, time

LLAMA_CLI  = "./llama-bin/llama-mtmd-cli.exe"
MODEL_PATH = "./models/gemma3-4b/gemma-3-4b-it-Q4_K_M.gguf"
MMPROJ = "./models/gemma3-4b/mmproj-gemma-3-4b-it-q8_0.gguf"

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
    "-ngl",     "0",
]

print("Running inference...")
t = time.time()
result = subprocess.run(cmd, capture_output=True, text=True)
print(f"Inference time: {time.time()-t:.2f}s")
print("Response:", result.stdout.strip())
if result.returncode != 0:
    print("stderr:", result.stderr[-500:])