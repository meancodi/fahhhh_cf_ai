import os
os.environ["HF_HUB_CACHE"] = os.path.abspath("./models/hf_cache")
os.environ["HF_HOME"] = os.path.abspath("./models/hf_cache")

from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import sys, torch, time

print("Downloading/loading model into ./models/hf_cache ...")
model = AutoModelForCausalLM.from_pretrained(
    "vikhyatk/moondream2",
    revision="2025-06-21",
    trust_remote_code=True,
    device_map={"": "cpu"},
    torch_dtype=torch.float32,
)
tokenizer = AutoTokenizer.from_pretrained(
    "vikhyatk/moondream2",
    revision="2025-06-21",
)
print("Model ready.\n")

image_path = sys.argv[1] if len(sys.argv) > 1 else "test.png"
image = Image.open(image_path).convert("RGB")
image.thumbnail((640, 640))

prompt = (
    "In one sentence, describe the visual layout and purpose "
    "of this screen region for a visually impaired user."
)

print("Running inference...")
t = time.time()
result = model.query(image, prompt)
print(f"Inference time: {time.time() - t:.2f}s")
print("Response:", result["answer"])