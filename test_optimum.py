import os, sys, time
os.environ["HF_HOME"] = "./models/hf_cache"

from pathlib import Path
from optimum.intel import OVModelForVisualCausalLM
from transformers import AutoProcessor
from PIL import Image

MODEL_ID   = "HuggingFaceTB/SmolVLM-256M-Instruct"
EXPORT_DIR = "./models/hf_cache/smolvlm-ov-int8"

print("Loading model...")
processor = AutoProcessor.from_pretrained(MODEL_ID)

# Check if already exported
if Path(EXPORT_DIR).exists() and any(Path(EXPORT_DIR).glob("*.xml")):
    print("Found cached OV model, loading...")
    model = OVModelForVisualCausalLM.from_pretrained(
        MODEL_ID,
        export=True,
        load_in_8bit=True,
        save_directory=EXPORT_DIR,
    )
else:
    print("Exporting to OpenVINO (one-time, ~2 min)...")
    model = OVModelForVisualCausalLM.from_pretrained(
        MODEL_ID,
        export=True,
        load_in_8bit=True,
        save_directory=EXPORT_DIR,
    )
print("Model ready.\n")

image_path = sys.argv[1] if len(sys.argv) > 1 else "test.png"
image = Image.open(image_path).convert("RGB")

messages = [{
    "role": "user",
    "content": [
        {"type": "image"},
        {"type": "text", "text": (
            "This is a screenshot of a computer screen. "
            "Describe exactly what is shown: if it is a chart describe the data and trends, "
            "if it is code describe what it does, "
            "if it is a UI describe the elements and their purpose. "
            "Be specific and concise. One to two sentences only."
        )}
    ]
}]

prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = processor(text=prompt, images=[image], return_tensors="pt")

t = time.time()
output = model.generate(**inputs, max_new_tokens=80, do_sample=False)
print(f"Inference time: {time.time()-t:.2f}s")

trimmed = output[:, inputs["input_ids"].shape[1]:]
print("Response:", processor.decode(trimmed[0], skip_special_tokens=True))