# VCLens

> An offline, privacy-first accessibility tool that describes any region of your screen out loud.

Press a hotkey, draw a box, hear a description. Works on charts, code, UI elements, videos — anything visual that standard screen readers miss.

---

## How it works

1. Press **Alt+Shift+~** to activate the region selector
2. Draw a box around any part of your screen
3. Lens runs the region through a local Vision Language Model
4. A spoken description is read aloud instantly

Everything runs on your machine. No internet required after setup. No data leaves your device.

---

## Demo

| Capture | Description |
|---|---|
| Bar chart | *"The chart shows the number of police officers in Crimsville from 2011 to 2019, with a fluctuating trend peaking around 2014."* |
| Code editor | *"The screenshot shows a Python function that reads a file from disk and returns its contents as a string."* |
| Video frame | *"Two people are hugging on a stage under bright lights with a caption visible at the bottom."* |

---

## Requirements

- Python 3.10+
- Windows (Linux and macOS supported with minor changes)
- A GPU with Vulkan support (Intel, AMD, or NVIDIA) — CPU fallback available

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/lens.git
cd lens
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

On Windows:
```powershell
venv\Scripts\activate
```

On Linux/macOS:
```bash
source venv/bin/activate
```

### 3. Download llama.cpp binaries

Download the appropriate build for your machine from the [llama.cpp releases page](https://github.com/ggml-org/llama.cpp/releases/tag/b8292) and extract into the project root:

| Folder | Download |
|---|---|
| `llama-bin-vulkan/` | `llama-b8292-bin-win-vulkan-x64.zip` |
| `llama-bin-cuda/` | `llama-b8292-bin-win-cuda-12.4-x64.zip` *(optional, NVIDIA only)* |
| `llama-bin/` | `llama-b8292-bin-win-cpu-x64.zip` *(CPU fallback)* |

On Windows (PowerShell):

```powershell
# Vulkan (recommended)
curl -L "https://github.com/ggml-org/llama.cpp/releases/download/b8292/llama-b8292-bin-win-vulkan-x64.zip" -o vulkan.zip
Expand-Archive vulkan.zip -DestinationPath ./llama-bin-vulkan/

# CPU fallback
curl -L "https://github.com/ggml-org/llama.cpp/releases/download/b8292/llama-b8292-bin-win-cpu-x64.zip" -o cpu.zip
Expand-Archive cpu.zip -DestinationPath ./llama-bin/

# CUDA (optional, NVIDIA only)
curl -L "https://github.com/ggml-org/llama.cpp/releases/download/b8292/llama-b8292-bin-win-cuda-12.4-x64.zip" -o cuda.zip
Expand-Archive cuda.zip -DestinationPath ./llama-bin-cuda/
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Download the model

```bash
pip install -r requirements.txt
```

### 5. Download the model

The model is not included in the repo (~2.2GB total). Run these commands to download:

```bash
huggingface-cli download ggml-org/Qwen2.5-VL-3B-Instruct-GGUF \
  --include "Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf" \
  --local-dir ./models/qwen2.5-vl-3b

huggingface-cli download ggml-org/Qwen2.5-VL-3B-Instruct-GGUF \
  --include "mmproj-Qwen2.5-VL-3B-Instruct-Q8_0.gguf" \
  --local-dir ./models/qwen2.5-vl-3b
```

On Windows (PowerShell):

```powershell
huggingface-cli download ggml-org/Qwen2.5-VL-3B-Instruct-GGUF `
  --include "Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf" `
  --local-dir ./models/qwen2.5-vl-3b

huggingface-cli download ggml-org/Qwen2.5-VL-3B-Instruct-GGUF `
  --include "mmproj-Qwen2.5-VL-3B-Instruct-Q8_0.gguf" `
  --local-dir ./models/qwen2.5-vl-3b
```

### 6. Run

```bash
python launch.py
```

You will be prompted to select a backend:

```
Select backend:
  1. Vulkan - RTX (fastest)
  2. Vulkan - iGPU
  3. CPU
Enter 1, 2 or 3 [default: 1]:
```

Press **Alt+Shift+~** to start capturing.

---

## Project structure

```
lens/
├── launch.py            # entry point — starts all processes
├── inference.py         # VLM inference loop
├── tts.py               # text-to-speech listener
├── main.py              # global hotkey listener
├── screen_capture.py    # screen region selector (PyQt5)
├── ui_tray.py           # optional GUI (PyQt5)
├── requirements.txt
├── llama-bin/           # llama.cpp CPU binaries (included)
├── llama-bin-vulkan/    # llama.cpp Vulkan binaries (included)
└── models/              # downloaded separately — not in repo
    └── qwen2.5-vl-3b/
        ├── Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf
        └── mmproj-Qwen2.5-VL-3B-Instruct-Q8_0.gguf
```

---

## Performance

Tested on Intel i7-13700HX + NVIDIA RTX 4060 Laptop:

| Backend | Latency |
|---|---|
| Vulkan (RTX 4060) | 4–6s |
| Vulkan (Intel Iris Xe iGPU) | 14–17s |
| CPU only | 13–20s |

---

## Model

**Qwen2.5-VL-3B-Instruct** quantized to Q4_K_M via llama.cpp.

- 4-bit k-quant with mixed precision — attention layers at higher precision than feed-forward layers
- Vision encoder (mmproj) at Q8_0 for accuracy
- Runs on any CPU with AVX2 — Intel 6th gen+ or AMD Ryzen 1st gen+
- ~2.2GB total on disk, ~1.8GB RAM at runtime

---

## Accessibility use case

Standard screen readers describe text but are blind to visual content. Lens fills that gap — on demand, offline, for any visual element on screen. Designed for visually impaired users and neurodivergent users who benefit from audio descriptions of charts, diagrams, and complex UI layouts.

---

## Requirements.txt

```
keyboard
PyQt5
Pillow
huggingface_hub
```

---

## License

MIT