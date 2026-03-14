
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


# class Controller(QWidget):

#     def __init__(self):
#         super().__init__()

#         self.proc_hotkey = None
#         self.proc_tts = None
#         self.proc_infer = None

#         self.capture_started = False
#         self.capture_time = None

#         self.init_ui()

#         # auto start system
#         QTimer.singleShot(400, self.start_system)

#         # monitor capture start
#         self.capture_timer = QTimer()
#         self.capture_timer.timeout.connect(self.check_capture)
#         self.capture_timer.start(150)

#         # monitor inference output
#         self.output_timer = QTimer()
#         self.output_timer.timeout.connect(self.check_output)
#         self.output_timer.start(200)


#     # ---------------- UI ----------------

#     def init_ui(self):

#         self.setWindowTitle("Screen AI")
#         self.setFixedSize(360,250)
#         self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)

#         layout = QVBoxLayout()

#         # device selector
#         row = QHBoxLayout()

#         row.addWidget(QLabel("Device"))

#         self.backend = QComboBox()
#         self.backend.addItems(["Vulkan", "CUDA", "CPU"])
#         self.backend.currentIndexChanged.connect(self.device_changed)

#         row.addWidget(self.backend)

#         layout.addLayout(row)

#         # status
#         self.status = QLabel("Starting...")
#         layout.addWidget(self.status)

#         # inference time
#         self.time_label = QLabel("Inference time: -")
#         layout.addWidget(self.time_label)

#         # description
#         self.text = QTextEdit()
#         self.text.setReadOnly(True)
#         layout.addWidget(self.text)

#         # stop button
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

#         self.status.setText("Ready. Press Alt+Shift+~")
#         self.time_label.setText("Inference time: -")


#     def stop_system(self):

#         print("[UI] Stopping processes")

#         self.kill_process(self.proc_hotkey)
#         self.kill_process(self.proc_tts)
#         self.kill_process(self.proc_infer)

#         # also stop speech engine
#         subprocess.run(
#             ["taskkill", "/F", "/IM", "powershell.exe"],
#             stdout=subprocess.DEVNULL,
#             stderr=subprocess.DEVNULL
#         )

#         self.proc_hotkey = None
#         self.proc_tts = None
#         self.proc_infer = None

#         self.capture_started = False
#         self.capture_time = None

#         self.status.setText("Stopped")

#         # restart automatically
#         QTimer.singleShot(600, self.start_system)


#     # ---------------- DEVICE CHANGE ----------------

#     def device_changed(self):

#         device = self.backend.currentText()

#         print(f"[UI] Device changed -> {device}")

#         self.status.setText(f"Switching to {device}...")

#         self.stop_system()


#     # ---------------- CAPTURE DETECTION ----------------

#     def check_capture(self):

#         if os.path.exists(TRIGGER_FILE):

#             if not self.capture_started:

#                 try:

#                     content = open(TRIGGER_FILE).read().strip()

#                     if content != "CANCELLED":

#                         print("[UI] Capture detected")

#                         self.capture_started = True
#                         self.capture_time = time.time()

#                         self.text.clear()
#                         self.status.setText("Processing...")

#                 except:
#                     pass


#     # ---------------- OUTPUT MONITOR ----------------

#     def check_output(self):

#         if os.path.exists(OUTPUT_FILE):

#             try:

#                 text = open(OUTPUT_FILE).read().strip()

#                 if text:

#                     self.text.setText(text)
#                     self.status.setText("Speaking...")

#                     if self.capture_time:

#                         elapsed = time.time() - self.capture_time
#                         self.time_label.setText(
#                             f"Inference time: {elapsed:.2f} s"
#                         )

#                     self.capture_started = False
#                     self.capture_time = None

#             except:
#                 pass

#         else:

#             if not self.capture_started:

#                 if self.status.text() != "Ready. Press Alt+Shift+~":

#                     self.status.setText("Ready. Press Alt+Shift+~")


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



class Controller(QWidget):

    def __init__(self):
        super().__init__()

        self.proc_hotkey = None
        self.proc_tts = None
        self.proc_infer = None

        self.capture_time = None
        self.current_state = "idle"

        self.init_ui()

        # auto start system
        QTimer.singleShot(300, self.start_system)

        # single watcher for system state
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_state)
        self.timer.start(200)


    # ---------------- UI ----------------

    def init_ui(self):

        self.setWindowTitle("Screen AI")
        self.setFixedSize(360,260)
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


        # return to ready after speech
        if not os.path.exists(OUTPUT_FILE):

            if self.current_state == "speaking":
                self.set_state("ready")


# ---------------- MAIN ----------------

app = QApplication(sys.argv)

ui = Controller()
ui.show()

sys.exit(app.exec_())