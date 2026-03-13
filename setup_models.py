from huggingface_hub import hf_hub_download

print("Downloading Qwen2.5-VL-3B-Instruct GGUF...")
hf_hub_download(
    repo_id="ggml-org/Qwen2.5-VL-3B-Instruct-GGUF",
    filename="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
    local_dir="./models/qwen2.5-vl-3b"
)

print("Downloading mmproj...")
hf_hub_download(
    repo_id="ggml-org/Qwen2.5-VL-3B-Instruct-GGUF",
    filename="mmproj-Qwen2.5-VL-3B-Instruct-Q8_0.gguf",
    local_dir="./models/qwen2.5-vl-3b"
)

print("Done. Models saved to ./models/qwen2.5-vl-3b/")