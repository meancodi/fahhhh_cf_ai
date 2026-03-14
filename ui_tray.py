import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer


OUTPUT_FILE = "output.txt"



class Controller(QWidget):

    def __init__(self):
        super().__init__()

        self.proc_hotkey = None
        self.proc_tts = None
        self.proc_infer = None

        self.init_ui()

        QTimer.singleShot(500, self.start_system)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_output)
        self.timer.start(300)

    def init_ui(self):

        self.setWindowTitle("Screen AI")
        self.setFixedSize(340,230)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)

        layout = QVBoxLayout()

        row = QHBoxLayout()

        row.addWidget(QLabel("Device"))

        self.backend = QComboBox()
        self.backend.addItems(["Vulkan", "CUDA", "CPU"])
        self.backend.currentIndexChanged.connect(self.device_changed)

        row.addWidget(self.backend)

        layout.addLayout(row)

        self.status = QLabel("Starting...")
        layout.addWidget(self.status)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

        row2 = QHBoxLayout()

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_system)

        row2.addWidget(self.stop_btn)

        layout.addLayout(row2)

        self.setLayout(layout)

    # -------------------------
    # PROCESS CONTROL
    # -------------------------

    def kill_process(self, proc):

        if proc and proc.poll() is None:

            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

    def start_system(self):

        backend = self.backend.currentText().lower()

        print(f"[UI] Starting system using {backend}")

        inf_cmd = [sys.executable, "inference.py", f"--{backend}"]

        self.proc_hotkey = subprocess.Popen(
            [sys.executable, "main.py"]
        )

        self.proc_tts = subprocess.Popen(
            [sys.executable, "tts.py"]
        )

        self.proc_infer = subprocess.Popen(inf_cmd)

        self.status.setText("Ready. Press Alt+Shift+~")

    def stop_system(self):

        print("[UI] Stopping processes")

        self.kill_process(self.proc_hotkey)
        self.kill_process(self.proc_tts)
        self.kill_process(self.proc_infer)

        # also stop any active speech synthesizer
        subprocess.run(
            ["taskkill", "/F", "/IM", "powershell.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        self.proc_hotkey = None
        self.proc_tts = None
        self.proc_infer = None

        self.status.setText("Stopped")

        QTimer.singleShot(600, self.start_system)

    # -------------------------
    # DEVICE CHANGE
    # -------------------------

    def device_changed(self):

        device = self.backend.currentText()

        print(f"[UI] Device changed -> {device}")

        self.status.setText(f"Switching to {device}...")

        self.stop_system()

    # -------------------------
    # OUTPUT MONITOR
    # -------------------------

    def check_output(self):

        if os.path.exists(OUTPUT_FILE):

            try:
                text = open(OUTPUT_FILE).read().strip()

                if text:
                    self.text.setText(text)
                    self.status.setText("Speaking...")

            except:
                pass


app = QApplication(sys.argv)

ui = Controller()
ui.show()

sys.exit(app.exec_())