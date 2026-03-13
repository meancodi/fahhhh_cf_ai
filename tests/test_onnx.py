import onnxruntime_genai as og
from PIL import Image
import sys, time, io

MODEL_PATH = "./models/phi-3.5-vision-onnx/cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4"

print("Loading model...")
model = og.Model(MODEL_PATH)
processor = model.create_multimodal_processor()
tokenizer_stream = processor.create_stream()
print("Model ready.\n")

image_path = sys.argv[1] if len(sys.argv) > 1 else "test.png"

# Save resized image to temp file — og.Images.open needs a file path
image = Image.open(image_path).convert("RGB")
image.thumbnail((640, 640))
temp_path = "./temp_resized.png"
image.save(temp_path)

prompt = "<|user|>\n<|image_1|>\nIn one sentence, describe the visual layout and purpose of this screen region for a visually impaired user.<|end|>\n<|assistant|>\n"

images = og.Images.open(temp_path)
inputs = processor(prompt, images=images)

params = og.GeneratorParams(model)
params.set_search_options(max_length=100, temperature=0)  # kwargs not dict

generator = og.Generator(model, params)
generator.append_tokens(inputs["input_ids"][0])  # new API — append after generator creation

print(f"Image: {image_path}")
print("Running inference...")

t = time.time()
response = ""
while not generator.is_done():
    generator.generate_next_token()
    token = tokenizer_stream.decode(generator.get_next_tokens()[0])
    response += token

print(f"Inference time: {time.time() - t:.2f}s")
print("Response:", response)