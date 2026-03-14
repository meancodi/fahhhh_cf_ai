# import sys
# import os
# import time
# import subprocess

# from PyQt5.QtWidgets import (
#     QApplication, QWidget, QLabel, QPushButton,
#     QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit
# )

# from PyQt5.QtCore import Qt, QTimer


# TRIGGER_FILE = "trigger.txt"
# OUTPUT_FILE = "output.txt"

# def detect_backends():

#     cuda_available = os.path.exists("./llama-bin-cuda/llama-mtmd-cli.exe")
#     vulkan_available = os.path.exists("./llama-bin-vulkan/llama-mtmd-cli.exe")

#     devices = []
#     fastest = None

#     if cuda_available:
#         devices.append("CUDA (fastest)")
#         fastest = "CUDA"

#     if vulkan_available:
#         if not fastest:
#             devices.append("Vulkan (fastest)")
#             fastest = "Vulkan"
#         else:
#             devices.append("Vulkan")

#     devices.append("CPU")

#     if not fastest:
#         fastest = "CPU"

#     return devices, fastest

# class Controller(QWidget):

#     def __init__(self):
#         super().__init__()

#         self.proc_hotkey = None
#         self.proc_tts = None
#         self.proc_infer = None

#         self.capture_time = None
#         self.current_state = "idle"

#         self.init_ui()

#         # auto start system
#         QTimer.singleShot(300, self.start_system)

#         # single watcher for system state
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_state)
#         self.timer.start(200)


#     # ---------------- UI ----------------

#     def init_ui(self):

#         self.setWindowTitle("Screen AI")
#         self.setFixedSize(360,260)
#         self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)

#         layout = QVBoxLayout()

#         row = QHBoxLayout()
#         row.addWidget(QLabel("Device"))

#         devices, fastest = detect_backends()

#         self.backend = QComboBox()
#         self.backend.addItems(devices)

#         self.fastest_backend = fastest
#         self.backend.currentIndexChanged.connect(self.device_changed)

#         row.addWidget(self.backend)
#         layout.addLayout(row)

#         self.status = QLabel("Starting...")
#         layout.addWidget(self.status)

#         self.time_label = QLabel("Inference time: -")
#         layout.addWidget(self.time_label)

#         self.text = QTextEdit()
#         self.text.setReadOnly(True)
#         layout.addWidget(self.text)

#         row2 = QHBoxLayout()

#         self.stop_btn = QPushButton("Stop")
#         self.stop_btn.clicked.connect(self.stop_system)

#         row2.addWidget(self.stop_btn)

#         layout.addLayout(row2)

#         self.setLayout(layout)


#     # ---------------- PROCESS CONTROL ----------------

#     def kill_process(self, proc):

#         if proc and proc.poll() is None:

#             subprocess.run(
#                 ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
#                 stdout=subprocess.DEVNULL,
#                 stderr=subprocess.DEVNULL
#             )


#     def start_system(self):

#         backend = self.backend.currentText().lower()

#         print(f"[UI] Starting system using {backend}")

#         inf_cmd = [sys.executable, "inference.py", f"--{backend}"]

#         self.proc_hotkey = subprocess.Popen(
#             [sys.executable, "main.py"]
#         )

#         self.proc_tts = subprocess.Popen(
#             [sys.executable, "tts.py"]
#         )

#         self.proc_infer = subprocess.Popen(inf_cmd)

#         self.set_state("ready")


#     def stop_system(self):

#         print("[UI] Stopping processes")

#         self.kill_process(self.proc_hotkey)
#         self.kill_process(self.proc_tts)
#         self.kill_process(self.proc_infer)

#         subprocess.run(
#             ["taskkill", "/F", "/IM", "powershell.exe"],
#             stdout=subprocess.DEVNULL,
#             stderr=subprocess.DEVNULL
#         )

#         self.proc_hotkey = None
#         self.proc_tts = None
#         self.proc_infer = None

#         self.set_state("stopped")

#         QTimer.singleShot(600, self.start_system)


#     def device_changed(self):

#         device = self.backend.currentText()

#         print(f"[UI] Device changed -> {device}")

#         self.status.setText(f"Switching to {device}...")

#         self.stop_system()


#     # ---------------- STATE MACHINE ----------------

#     def set_state(self, state):

#         if state == self.current_state:
#             return

#         self.current_state = state

#         if state == "ready":
#             self.status.setText("Ready. Press Alt+Shift+~")
#             self.capture_time = None

#         elif state == "processing":
#             self.status.setText("Processing...")
#             self.text.clear()
#             self.capture_time = time.time()

#         elif state == "speaking":
#             self.status.setText("Speaking...")

#         elif state == "stopped":
#             self.status.setText("Stopped")


#     # ---------------- STATE WATCHER ----------------

#     def update_state(self):

#         # capture started
#         if os.path.exists(TRIGGER_FILE):

#             try:
#                 content = open(TRIGGER_FILE).read().strip()

#                 if content != "CANCELLED":
#                     if self.current_state == "ready":
#                         print("[UI] Capture detected")
#                         self.set_state("processing")

#             except:
#                 pass


#         # inference finished
#         if os.path.exists(OUTPUT_FILE):

#             try:
#                 text = open(OUTPUT_FILE).read().strip()

#                 if text:

#                     if self.current_state != "speaking":

#                         print("[UI] Output received")

#                         self.text.setText(text)
#                         self.set_state("speaking")

#                         if self.capture_time:
#                             elapsed = time.time() - self.capture_time
#                             self.time_label.setText(
#                                 f"Inference time: {elapsed:.2f} s"
#                             )

#             except:
#                 pass


#         # return to ready after speech
#         if not os.path.exists(OUTPUT_FILE):

#             if self.current_state == "speaking":
#                 self.set_state("ready")


# # ---------------- MAIN ----------------

# app = QApplication(sys.argv)

# ui = Controller()
# ui.show()

# sys.exit(app.exec_())

import sys
import os
import time
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit
)

from PyQt5.QtCore import Qt, QTimer


TRIGGER_FILE = "trigger.txt"
OUTPUT_FILE = "output.txt"


# ---------------- BACKEND DETECTION ----------------

def detect_backends():

    cuda_bin = "./llama-bin-cuda/llama-mtmd-cli.exe"
    vulkan_bin = "./llama-bin-vulkan/llama-mtmd-cli.exe"

    cuda_available = os.path.exists(cuda_bin)
    vulkan_available = os.path.exists(vulkan_bin)

    devices = []
    fastest = None

    if cuda_available:
        devices.append("CUDA (fastest)")
        fastest = "CUDA"

    if vulkan_available:
        if fastest:
            devices.append("Vulkan")
        else:
            devices.append("Vulkan (fastest)")
            fastest = "Vulkan"

    devices.append("CPU")

    if not fastest:
        fastest = "CPU"

    return devices, fastest


# ---------------- UI ----------------

class Controller(QWidget):

    def __init__(self):
        super().__init__()

        self.proc_hotkey = None
        self.proc_tts = None
        self.proc_infer = None

        self.capture_time = None
        self.current_state = "idle"

        self.devices, self.fastest_backend = detect_backends()

        self.init_ui()

        QTimer.singleShot(300, self.start_system)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_state)
        self.timer.start(200)


    # ---------------- UI SETUP ----------------

    def init_ui(self):

        self.setWindowTitle("Screen AI")
        self.setFixedSize(360,260)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)

        layout = QVBoxLayout()

        row = QHBoxLayout()
        row.addWidget(QLabel("Device"))

        self.backend = QComboBox()
        self.backend.addItems(self.devices)
        self.backend.currentIndexChanged.connect(self.device_changed)

        row.addWidget(self.backend)

        layout.addLayout(row)

        # auto select fastest backend
        for i in range(self.backend.count()):
            if self.fastest_backend in self.backend.itemText(i):
                self.backend.setCurrentIndex(i)
                break

        self.status = QLabel("Starting...")
        layout.addWidget(self.status)

        self.time_label = QLabel("Inference time: -")
        layout.addWidget(self.time_label)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

        row2 = QHBoxLayout()

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_system)

        row2.addWidget(self.stop_btn)

        layout.addLayout(row2)

        self.setLayout(layout)


    # ---------------- PROCESS CONTROL ----------------

    def kill_process(self, proc):

        if proc and proc.poll() is None:

            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )


    def start_system(self):

        backend_text = self.backend.currentText()
        backend = backend_text.split()[0].lower()

        print(f"[UI] Starting system using {backend}")

        inf_cmd = [sys.executable, "inference.py", f"--{backend}"]

        self.proc_hotkey = subprocess.Popen([sys.executable, "main.py"])
        self.proc_tts = subprocess.Popen([sys.executable, "tts.py"])
        self.proc_infer = subprocess.Popen(inf_cmd)

        self.set_state("ready")


    def stop_system(self):

        print("[UI] Stopping processes")

        self.kill_process(self.proc_hotkey)
        self.kill_process(self.proc_tts)
        self.kill_process(self.proc_infer)

        subprocess.run(
            ["taskkill", "/F", "/IM", "powershell.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        self.proc_hotkey = None
        self.proc_tts = None
        self.proc_infer = None

        self.set_state("stopped")

        QTimer.singleShot(600, self.start_system)


    def device_changed(self):

        device = self.backend.currentText()

        print(f"[UI] Device changed -> {device}")

        self.status.setText(f"Switching to {device}...")

        self.stop_system()


    # ---------------- STATE MACHINE ----------------

    def set_state(self, state):

        if state == self.current_state:
            return

        self.current_state = state

        if state == "ready":
            self.status.setText("Ready. Press Alt+Shift+~")
            self.capture_time = None

        elif state == "processing":
            self.status.setText("Processing...")
            self.text.clear()
            self.capture_time = time.time()

        elif state == "speaking":
            self.status.setText("Speaking...")

        elif state == "stopped":
            self.status.setText("Stopped")


    # ---------------- STATE WATCHER ----------------

    def update_state(self):

        # capture started
        if os.path.exists(TRIGGER_FILE):

            try:
                content = open(TRIGGER_FILE).read().strip()

                if content != "CANCELLED":
                    if self.current_state == "ready":
                        print("[UI] Capture detected")
                        self.set_state("processing")

            except:
                pass


        # inference finished
        if os.path.exists(OUTPUT_FILE):

            try:
                text = open(OUTPUT_FILE).read().strip()

                if text:

                    if self.current_state != "speaking":

                        print("[UI] Output received")

                        self.text.setText(text)
                        self.set_state("speaking")

                        if self.capture_time:
                            elapsed = time.time() - self.capture_time
                            self.time_label.setText(
                                f"Inference time: {elapsed:.2f} s"
                            )

            except:
                pass


        # return to ready
        if not os.path.exists(OUTPUT_FILE):

            if self.current_state == "speaking":
                self.set_state("ready")


# ---------------- MAIN ----------------

app = QApplication(sys.argv)

ui = Controller()
ui.show()

sys.exit(app.exec_())