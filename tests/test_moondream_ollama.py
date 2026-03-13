import requests
import base64
import sys
import time
from PIL import Image
import io

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "moondream"

image_path = sys.argv[1] if len(sys.argv) > 1 else "test.png"

image = Image.open(image_path).convert("RGB")
image.thumbnail((640, 640))
buf = io.BytesIO()
image.save(buf, format="PNG")
img_b64 = base64.b64encode(buf.getvalue()).decode()

payload = {
    "model": MODEL,
    "prompt": (
        "In one or two sentences, describe the visual layout and purpose "
        "of this screen region for a visually impaired user."
    ),
    "images": [img_b64],
    "stream": False,
    "options": {
        "num_predict": 80,
        "temperature": 0,
    }
}

print(f"Image: {image_path}")
print("Running inference...")

t = time.time()
response = requests.post(OLLAMA_URL, json=payload)
elapsed = time.time() - t

result = response.json()
print(f"Inference time: {elapsed:.2f}s")
print("Response:", result["response"])