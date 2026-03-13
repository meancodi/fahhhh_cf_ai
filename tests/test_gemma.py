import sys, time
from llama_cpp import Llama
import easyocr
from PIL import Image
import numpy as np

MODEL_PATH = "./models/gemma3-4b/gemma-3-4b-it-Q4_K_M.gguf"

print("Loading model...")
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=8,      # use all P-cores on i7-13700HX
    verbose=False,
)
reader = easyocr.Reader(['en'], gpu=False)
print("Ready.\n")

image_path = sys.argv[1] if len(sys.argv) > 1 else "test.png"
image = Image.open(image_path).convert("RGB")

t_total = time.time()

# Stage 1: extract text/structure from screenshot
t = time.time()
ocr_result = reader.readtext(np.array(image), detail=0)
ocr_text = " | ".join(ocr_result) if ocr_result else "No text detected"
print(f"OCR time:  {time.time()-t:.2f}s")
print(f"OCR text:  {ocr_text[:120]}")


# Stage 2: LLM describes it naturally
t = time.time()
prompt = f"""<start_of_turn>user
A visually impaired user captured this screen region. The raw content extracted is:
{ocr_text}

In 1-2 sentences, describe what this screen region shows and its purpose.<end_of_turn>
<start_of_turn>model
"""

response = llm(prompt, max_tokens=80, temperature=0, stop=["<end_of_turn>"])
print(f"LLM time:  {time.time()-t:.2f}s")
print(f"Total time :     {time.time()-t_total:.2f}s")
print("Response:", response["choices"][0]["text"].strip())