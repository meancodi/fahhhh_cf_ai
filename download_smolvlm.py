
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='HuggingFaceTB/SmolVLM-256M-Instruct',
    local_dir='./models/smolvlm-256m'
)
print('Done')
