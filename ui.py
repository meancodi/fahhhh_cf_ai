import os, sys, time, threading, subprocess, platform
from PIL import Image, ImageDraw
import tkinter as tk
import keyboard
import pystray

SYSTEM       = platform.system()
TRIGGER_FILE = "./trigger.txt"
OUTPUT_FILE  = "./output.txt"

DISCRETE_GPU_KEYWORDS = ["NVIDIA", "GeForce", "Quadro", "RTX", "GTX", "Radeon RX", "Radeon Pro"]

def detect_vulkan_device():
    try:
        cli = "./llama-bin-vulkan/llama-mtmd-cli.exe" if SYSTEM == "Windows" else "./llama-bin-vulkan/llama-mtmd-cli"
        result = subprocess.run([cli, "--list-devices"], capture_output=True, text=True, timeout=10)
        output = result.stderr + result.stdout
        devices = []
        for line in output.splitlines():
            if line.strip().startswith("Vulkan"):
                parts = line.strip().split(":", 1)
                if len(parts) == 2:
                    devices.append((parts[0].strip(), parts[1].strip()))
        if not devices:
            return None
        for dev_id, dev_name in devices:
            if not any(kw in dev_name for kw in DISCRETE_GPU_KEYWORDS):
                return dev_id
        return devices[0][0]
    except Exception as e:
        print(f"Device detection failed: {e}")
        return None

def make_tray_icon():
    img  = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((4,  20, 60, 44), fill="#cdd6f4")
    draw.ellipse((22, 24, 42, 40), fill="#1e1e2e")
    draw.ellipse((28, 27, 34, 33), fill="#cdd6f4")
    return img

class OverlayApp:
    def __init__(self, root):
        self.root          = root
        self.backend       = tk.StringVar(value="vulkan")
        self.running       = True
        self.tray          = None
        self.vulkan_device = None
        self.inf_proc      = None   # inference.py process
        self.tts_proc      = None   # tts.py process

        # ── window ──
        root.title("Visual Contextualizer")
        root.geometry("360x220")
        root.resizable(False, False)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.92)
        root.configure(bg="#1e1e2e")
        root.protocol("WM_DELETE_WINDOW", self.quit_app)
        root.bind("<ButtonPress-1>", self._drag_start)
        root.bind("<B1-Motion>",     self._drag_motion)

        # ── top row ──
        top = tk.Frame(root, bg="#1e1e2e")
        top.pack(fill="x", padx=12, pady=(10, 0))

        tk.Label(top, text="Backend:", bg="#1e1e2e",
                 fg="#cdd6f4", font=("Segoe UI", 9)).pack(side="left")

        for label, val in [("Vulkan", "vulkan"), ("CPU", "cpu")]:
            tk.Radiobutton(
                top, text=label, variable=self.backend, value=val,
                bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244",
                activebackground="#1e1e2e", activeforeground="#cdd6f4",
                font=("Segoe UI", 9),
                command=self._on_backend_change,
            ).pack(side="left", padx=6)

        tk.Button(
            top, text="—", command=self.minimize_to_tray,
            bg="#313244", fg="#cdd6f4", relief="flat",
            font=("Segoe UI", 11), cursor="hand2", bd=0
        ).pack(side="right")

        # ── status ──
        self.status_var = tk.StringVar(value="starting...")
        self.status_label = tk.Label(
            root, textvariable=self.status_var,
            bg="#313244", fg="#f38ba8",
            font=("Segoe UI", 9, "bold"),
            padx=10, pady=3
        )
        self.status_label.pack(pady=(8, 0))

        # ── caption ──
        caption_frame = tk.Frame(root, bg="#313244")
        caption_frame.pack(fill="both", expand=True, padx=12, pady=(6, 0))

        scrollbar = tk.Scrollbar(caption_frame)
        scrollbar.pack(side="right", fill="y")

        self.caption_text = tk.Text(
            caption_frame,
            bg="#313244", fg="#cdd6f4",
            font=("Segoe UI", 9), wrap="word",
            relief="flat", bd=0, padx=8, pady=6,
            yscrollcommand=scrollbar.set,
            state="disabled", height=4,
        )
        self.caption_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.caption_text.yview)
        self.set_caption("Starting inference and TTS processes...")

        # ── stop button ──
        self.stop_btn = tk.Button(
            root, text="⏹ Stop", command=self.stop,
            bg="#f38ba8", fg="#1e1e2e", relief="flat",
            font=("Segoe UI", 9, "bold"), cursor="hand2",
            state="disabled", bd=0, pady=4
        )
        self.stop_btn.pack(fill="x", padx=12, pady=(4, 8))

        # ── hotkey ──
        keyboard.add_hotkey("alt+shift+`", self._on_hotkey)

        # ── tray ──
        threading.Thread(target=self._setup_tray, daemon=True).start()

        # ── start subprocesses + monitor ──
        threading.Thread(target=self._init, daemon=True).start()

    # ── init: detect device, launch inference + tts ───────────────────────
    def _init(self):
        self.vulkan_device = detect_vulkan_device()
        self._launch_inference()
        self._launch_tts()
        self.root.after(0, self.set_status, "idle",
                        "Ready — press Alt+Shift+` to capture")
        self._monitor_loop()

    def _launch_inference(self):
        backend = self.backend.get()
        args = [sys.executable, "inference.py", f"--{backend}"]
        if self.vulkan_device:
            args += ["--device", self.vulkan_device]
        self.inf_proc = subprocess.Popen(args)
        print(f"inference.py started (pid {self.inf_proc.pid})")

    def _launch_tts(self):
        self.tts_proc = subprocess.Popen([sys.executable, "tts.py"])
        print(f"tts.py started (pid {self.tts_proc.pid})")

    def _kill_inference(self):
        if self.inf_proc and self.inf_proc.poll() is None:
            self.inf_proc.terminate()
            try:
                self.inf_proc.wait(timeout=3)
            except Exception:
                self.inf_proc.kill()
        self.inf_proc = None

    def _kill_tts(self):
        if self.tts_proc and self.tts_proc.poll() is None:
            self.tts_proc.terminate()
            try:
                self.tts_proc.wait(timeout=3)
            except Exception:
                self.tts_proc.kill()
        self.tts_proc = None

    # ── monitor loop: watch output.txt to update UI status ────────────────
    def _monitor_loop(self):
        processing = False
        while self.running:
            # trigger written → processing started
            if os.path.exists(TRIGGER_FILE) and not processing:
                processing = True
                backend = self.backend.get()
                self.root.after(0, self.set_status, "processing",
                                f"Analysing ({backend})...")
                self.root.after(0, self._enable_stop_btn)

            # output written → inference done, tts speaking
            if os.path.exists(OUTPUT_FILE) and processing:
                caption = open(OUTPUT_FILE).read().strip()
                processing = False
                self.root.after(0, self.set_status, "speaking",
                                caption)
                # wait briefly then set idle (tts handles actual speech timing)
                threading.Thread(
                    target=self._wait_then_idle,
                    args=(caption,), daemon=True
                ).start()
                self.root.after(0, self._disable_stop_btn)

            time.sleep(0.2)

    def _wait_then_idle(self, caption):
        # poll until output.txt is gone (tts.py deletes it when done speaking)
        # tts.py deletes it immediately on read, so just wait a moment
        time.sleep(0.5)
        if self.running:
            self.root.after(0, self.set_status, "idle", caption)

    # ── backend switch: restart inference ─────────────────────────────────
    def _on_backend_change(self):
        if self.status_var.get() == "idle":
            self._kill_inference()
            self._launch_inference()

    # ── stop ──────────────────────────────────────────────────────────────
    def stop(self):
        if os.path.exists(TRIGGER_FILE):
            os.remove(TRIGGER_FILE)
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)
        self.root.after(0, self.set_status, "idle", "Stopped.")
        self.root.after(0, self._disable_stop_btn)

    def _enable_stop_btn(self):
        self.stop_btn.config(state="normal")

    def _disable_stop_btn(self):
        self.stop_btn.config(state="disabled")

    # ── drag ──────────────────────────────────────────────────────────────
    def _drag_start(self, event):
        self._x = event.x
        self._y = event.y

    def _drag_motion(self, event):
        x = self.root.winfo_x() + (event.x - self._x)
        y = self.root.winfo_y() + (event.y - self._y)
        self.root.geometry(f"+{x}+{y}")

    # ── status ────────────────────────────────────────────────────────────
    STATUS_COLORS = {
        "idle":       "#a6e3a1",
        "capturing":  "#89dceb",
        "processing": "#fab387",
        "speaking":   "#cba6f7",
        "starting...":"#f38ba8",
    }

    def set_status(self, status, caption=None):
        self.status_var.set(status)
        self.status_label.config(fg=self.STATUS_COLORS.get(status, "#cdd6f4"))
        if caption is not None:
            self.set_caption(caption)
        if self.tray:
            self.tray.title = f"Visual Contextualizer — {status}"

    def set_caption(self, text):
        self.caption_text.config(state="normal")
        self.caption_text.delete("1.0", "end")
        self.caption_text.insert("end", text)
        self.caption_text.config(state="disabled")

    # ── hotkey ────────────────────────────────────────────────────────────
    def _on_hotkey(self):
        if self.status_var.get() == "idle":
            self.root.after(0, self.set_status, "capturing")
            subprocess.Popen([sys.executable, "screen_capture.py"])

    # ── tray ──────────────────────────────────────────────────────────────
    def _setup_tray(self):
        self.tray = pystray.Icon(
            "visual_contextualizer",
            make_tray_icon(),
            "Visual Contextualizer",
            menu=pystray.Menu(
                pystray.MenuItem("Restore", self.restore_from_tray, default=True),
                pystray.MenuItem("Quit",    self.quit_app),
            )
        )
        self.tray.run_detached()

    def minimize_to_tray(self):
        self.root.withdraw()

    def restore_from_tray(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)
        self.root.after(0, self.root.lift)

    # ── quit ──────────────────────────────────────────────────────────────
    def quit_app(self, icon=None, item=None):
        self.running = False
        keyboard.unhook_all()
        self._kill_inference()
        self._kill_tts()
        if os.path.exists(TRIGGER_FILE):
            os.remove(TRIGGER_FILE)
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)
        if self.tray:
            self.tray.stop()
        self.root.after(0, self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    app  = OverlayApp(root)
    root.mainloop()