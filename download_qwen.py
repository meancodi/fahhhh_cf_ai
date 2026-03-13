from huggingface_hub import snapshot_download
path = snapshot_download(
    repo_id='Qwen/Qwen2.5-VL-3B-Instruct',
    local_dir='./models/qwen2.5-vl-3b'
)
print('Downloaded to:', path)