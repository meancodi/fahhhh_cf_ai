# Adaptive Visual Contextualizer

An accessibility tool that lets visually impaired and neurodivergent users select any region of their screen via a hotkey and receive a spoken natural language description of what's shown — charts, code, UI elements, or any visual content.

---

## How it works

1. Press `Alt+Shift+~` to trigger the screen selector
2. Draw a box around any screen region
3. The region is sent to a local VLM (Qwen2.5-VL-3B) for analysis
4. A spoken description is read aloud via the OS speech engine

Everything runs locally — no internet required after setup.

---

## Project structure

```
project/
├── main.py              # global hotkey listener
├── screen_capture.py    # PyQt5 region selector, writes trigger.txt
├── inference.py         # VLM inference loop, reads trigger.txt, writes output.txt
├── tts.py               # TTS loop, reads output.txt and speaks
├── requirements.txt
└── models/              # created by model download step (not committed)
```

---

## Requirements

### Python dependencies

```bash
pip install -r requirements.txt
```

### llama.cpp binaries

Download the appropriate build for your OS from:
https://github.com/ggml-org/llama.cpp/releases/tag/b8292

| OS | Vulkan (recommended) | CPU fallback |
|---|---|---|
| Windows | `llama-b8292-bin-win-vulkan-x64.zip` | `llama-b8292-bin-win-cpu-x64.zip` |
| Linux | `llama-b8292-bin-ubuntu-vulkan-x64.tar.gz` | `llama-b8292-bin-ubuntu-x64.tar.gz` |
| macOS (Apple Silicon) | — | `llama-b8292-bin-macos-arm64.tar.gz` |
| macOS (Intel) | — | `llama-b8292-bin-macos-x64.tar.gz` |

Extract Vulkan build to `./llama-bin-vulkan/` and CPU build to `./llama-bin/`.

> macOS uses Metal automatically — no separate Vulkan binary needed. Use `--cpu` flag which maps to Metal on Mac.

### Linux TTS

```bash
sudo apt install espeak
```

Windows and macOS have speech engines built in — no setup needed.

### Models

Download Qwen2.5-VL-3B GGUF and mmproj:

```bash
huggingface-cli download ggml-org/Qwen2.5-VL-3B-Instruct-GGUF \
  --include "Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf" \
  --local-dir ./models/qwen2.5-vl-3b

huggingface-cli download ggml-org/Qwen2.5-VL-3B-Instruct-GGUF \
  --include "mmproj-Qwen2.5-VL-3B-Instruct-Q8_0.gguf" \
  --local-dir ./models/qwen2.5-vl-3b
```

Total download size: ~2.2 GB

---

## Running

Open three terminals:

```bash
# Terminal 1 — inference engine (choose backend)
python inference.py --vulkan    # recommended: uses iGPU/dGPU via Vulkan
python inference.py --cpu       # fallback: CPU only

# Terminal 2 — TTS listener
python tts.py

# Terminal 3 — hotkey listener
python main.py
```

Then press `Alt+Shift+~` and draw a box on screen.

---

## Performance

Tested on Intel i7-13700HX:

| Backend | Inference time |
|---|---|
| Vulkan (iGPU) | ~6–7s |
| CPU only | ~13s |

The model stays loaded between captures — only the first capture after startup pays the full load time.

---

## Model

**Qwen2.5-VL-3B-Instruct Q4_K_M** via llama.cpp

- 4-bit quantized — ~2GB on disk, ~1.8GB RAM
- Handles charts, graphs, code, UI elements, and mixed content
- mmproj Q8_0 — quantized vision encoder for faster image processing
- Runs on any CPU with AVX2 (Intel 6th gen+ / AMD Ryzen 1st gen+)

### Quantization methods used

| Component | Method | Effect |
|---|---|---|
| Language model | Q4_K_M (4-bit, k-quant) | 70% size reduction, ~95% quality retained |
| Vision encoder (mmproj) | Q8_0 (8-bit) | 50% size reduction, ~99% quality retained |

Q4_K_M uses a mixed quantization strategy where attention and feed-forward layers are quantized at different bit depths based on sensitivity — more important layers keep higher precision. This gives better quality than uniform Q4 at the same file size.

---

## Accessibility note

This tool is designed for:
- Visually impaired users who need screen reader support for visual content
- Neurodivergent users who benefit from audio descriptions of complex visual layouts
- Any user who needs on-demand narration of charts, dashboards, or unfamiliar UI

Standard screen readers describe text but fail on images, charts, and unlabeled UI elements. This tool fills that gap with natural language descriptions read aloud on demand.

---

## .gitignore

```
models/*
!models/.gitkeep
llama*/
temp_capture.png
temp_speech.txt
trigger.txt
output.txt
screenshots/
__pycache__/
*.pyc
venv/
.env
```