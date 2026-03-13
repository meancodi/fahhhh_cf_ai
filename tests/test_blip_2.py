import os, time, sys
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image
import torch

MODEL_PATH = "./models/blip2-opt-2.7b"

print("Loading BLIP-2...")
processor = Blip2Processor.from_pretrained(MODEL_PATH, local_files_only=True)
model = Blip2ForConditionalGeneration.from_pretrained(
    MODEL_PATH,
    local_files_only=True,
    torch_dtype=torch.float32,
    device_map={"": "cpu"},
)
model.eval()
print("Model ready.\n")

image_path = sys.argv[1] if len(sys.argv) > 1 else "test.png"
image = Image.open(image_path).convert("RGB")

prompt = "Question: Describe the visual layout and content of this screen region for a visually impaired user. Answer:"

inputs = processor(image, text=prompt, return_tensors="pt")

t = time.time()
with torch.no_grad():
    out = model.generate(
        **inputs,
        max_new_tokens=80,
        do_sample=False,
    )
print(f"Inference time: {time.time()-t:.2f}s")
print("Response:", processor.decode(out[0], skip_special_tokens=True))