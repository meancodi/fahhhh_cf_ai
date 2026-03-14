import sys, os, time, subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
TRIGGER_FILE = os.path.join(BASE_DIR, "trigger.txt")
OUTPUT_FILE  = os.path.join(BASE_DIR, "output.txt")

# ── backend detection ──────────────────────────────────────────────────────
def detect_backends():
    cuda_bin   = os.path.join(BASE_DIR, "llama-bin-cuda",   "llama-mtmd-cli.exe")
    vulkan_bin = os.path.join(BASE_DIR, "llama-bin-vulkan", "llama-mtmd-cli.exe")
    devices, fastest = [], None
    if os.path.exists(cuda_bin):
        devices.append("CUDA (fastest)")
        fastest = "CUDA"
    if os.path.exists(vulkan_bin):
        devices.append("Vulkan (fastest)" if not fastest else "Vulkan")
        if not fastest:
            fastest = "Vulkan"
    devices.append("CPU")
    if not fastest:
        fastest = "CPU"
    return devices, fastest

def kill_proc(proc):
    if proc and proc.poll() is None:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

def kill_powershell():
    subprocess.run(
        ["taskkill", "/F", "/IM", "powershell.exe"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

def launch(script, args=None):
    path = os.path.join(BASE_DIR, script)
    return subprocess.Popen([sys.executable, path] + (args or []))

# ── UI ─────────────────────────────────────────────────────────────────────
class Controller(QWidget):

    def __init__(self):
        super().__init__()

        self.proc_hotkey  = None
        self.proc_tts     = None
        self.proc_infer   = None
        self.capture_time = None
        self.state        = "idle"
        self.last_caption = ""

        self.devices, self.fastest = detect_backends()
        self._build_ui()

        QTimer.singleShot(300, self.start_system)

        self.timer = QTimer()
        self.timer.timeout.connect(self._poll)
        self.timer.start(200)

    # ── UI ─────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setWindowTitle("Visual Contextualizer")
        self.setFixedSize(380, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)

        layout = QVBoxLayout()
        layout.setSpacing(6)

        # backend row
        row = QHBoxLayout()
        row.addWidget(QLabel("Backend:"))
        self.backend_box = QComboBox()
        self.backend_box.addItems(self.devices)
        for i in range(self.backend_box.count()):
            if self.fastest in self.backend_box.itemText(i):
                self.backend_box.setCurrentIndex(i)
                break
        self.backend_box.currentIndexChanged.connect(self._on_backend_change)
        row.addWidget(self.backend_box)
        layout.addLayout(row)

        # status
        self.status_lbl = QLabel("Starting...")
        self.status_lbl.setStyleSheet("font-weight:bold; font-size:13px;")
        layout.addWidget(self.status_lbl)

        # inference time
        self.time_lbl = QLabel("Inference time: —")
        self.time_lbl.setStyleSheet("color:gray; font-size:11px;")
        layout.addWidget(self.time_lbl)

        # caption
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        layout.addWidget(self.text_box)

        # buttons row
        btn_row = QHBoxLayout()

        self.stop_btn = QPushButton("⏹ Stop TTS")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop_tts)
        btn_row.addWidget(self.stop_btn)

        layout.addLayout(btn_row)
        self.setLayout(layout)

    # ── state ──────────────────────────────────────────────────────────────
    def _set_state(self, state):
        self.state = state
        labels = {
            "ready":      "Ready — press Alt+Shift+~",
            "processing": "Processing...",
            "speaking":   "Speaking...",
            "stopped":    "Stopped",
            "starting":   "Starting...",
        }
        self.status_lbl.setText(labels.get(state, state))
        self.stop_btn.setEnabled(state == "speaking")

    # ── process control ────────────────────────────────────────────────────
    def start_system(self):
        backend = self.backend_box.currentText().split()[0].lower()
        print(f"[UI] Starting — backend={backend}")
        self._set_state("starting")

        self.proc_hotkey = launch("main.py")
        self.proc_tts    = launch("tts.py")
        self.proc_infer  = launch("inference.py", [f"--{backend}"])

        self._set_state("ready")

    def _restart_all(self):
        kill_proc(self.proc_hotkey)
        kill_proc(self.proc_tts)
        kill_proc(self.proc_infer)
        kill_powershell()
        self.proc_hotkey = self.proc_tts = self.proc_infer = None
        # clean up stale files
        for f in [TRIGGER_FILE, OUTPUT_FILE]:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass
        QTimer.singleShot(500, self.start_system)

    def _on_backend_change(self):
        if self.state in ("processing", "speaking"):
            return
        print("[UI] Backend changed — restarting")
        self._restart_all()

    # stop TTS only — keep inference alive
    def _on_stop_tts(self):
        kill_powershell()
        # remove output so tts.py doesn't re-read it
        try:
            if os.path.exists(OUTPUT_FILE):
                os.remove(OUTPUT_FILE)
        except Exception:
            pass
        self.text_box.append("\n[Stopped]")
        self._set_state("ready")

    # ── poll ───────────────────────────────────────────────────────────────
    def _poll(self):

        # trigger appeared → processing
        if os.path.exists(TRIGGER_FILE) and self.state == "ready":
            try:
                content = open(TRIGGER_FILE).read().strip()
                if content == "CANCELLED":
                    self.status_lbl.setText("Capture cancelled.")
                elif content:
                    self.capture_time = time.time()
                    self.text_box.clear()
                    self._set_state("processing")
            except Exception:
                pass

        # output appeared → show caption, set speaking
        if os.path.exists(OUTPUT_FILE) and self.state == "processing":
            try:
                caption = open(OUTPUT_FILE).read().strip()
                if caption and caption != self.last_caption:
                    self.last_caption = caption
                    elapsed = time.time() - self.capture_time if self.capture_time else 0
                    self.time_lbl.setText(f"Inference time: {elapsed:.2f}s")
                    self.text_box.setText(caption)
                    self._set_state("speaking")
            except Exception:
                pass

        # output gone → tts done, back to ready
        if not os.path.exists(OUTPUT_FILE) and self.state == "speaking":
            self._set_state("ready")


# ── entry point ────────────────────────────────────────────────────────────
app = QApplication(sys.argv)
ui  = Controller()
ui.show()
sys.exit(app.exec_())