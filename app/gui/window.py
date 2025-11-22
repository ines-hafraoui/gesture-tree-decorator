# app/gui/window.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from vision.camera_thread import CameraThread
from vision.hand_detector import DummyHandDetector
from gui.renderer import TreeRenderer
from ornaments.manager import OrnamentManager
from utils.config import ASSETS_PATH

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Count to Decorate")

        # Core systems
        self.camera = CameraThread()
        self.detector = DummyHandDetector()
        self.manager = OrnamentManager()
        self.renderer = TreeRenderer(self.manager)

        # UI Layout
        self._build_ui()

        # Binding simulated gesture keys 1..5
        self.root.bind("<Key>", self._on_key)

        # Update loop
        self._update()

    def _build_ui(self):
        self.tree_canvas = tk.Canvas(self.root, width=600, height=580)
        self.tree_canvas.grid(row=0, column=0, rowspan=4)

        self.start_btn = ttk.Button(self.root, text="Start Hand Detection",
                                    command=self.toggle_camera)
        self.start_btn.grid(row=0, column=1, pady=5)

        self.mode_var = tk.StringVar(value="Idle")
        ttk.Label(self.root, textvariable=self.mode_var).grid(row=1, column=1)

        self.preview_label = ttk.Label(self.root)
        self.preview_label.grid(row=2, column=1)

        # Ornament menu (initially hidden)
        self.menu_frame = ttk.Frame(self.root)
        self.menu_buttons = []

        for i in range(1, 6):
            btn = ttk.Button(self.menu_frame, text=f"{i}",
                             command=lambda n=i: self._select_ornament(n))
            btn.grid(row=(i-1)//2, column=(i-1)%2, padx=2, pady=2)
            self.menu_buttons.append(btn)

        self.menu_frame.grid(row=3, column=1, pady=10)
        self.menu_frame.grid_remove()

    def toggle_camera(self):
        if not self.camera.running:
            self.camera.start()
            self.start_btn.config(text="Stop Detection")
        else:
            self.camera.stop()
            self.menu_frame.grid_remove()
            self.mode_var.set("Idle")
            self.start_btn.config(text="Start Hand Detection")

    def _select_ornament(self, idx):
        self.manager.add_ornament(idx)
        self.renderer.render(self.tree_canvas)

    def _on_key(self, event):
        if event.char in "12345":
            idx = int(event.char)
            self._select_ornament(idx)

    def _update(self):
        """
        Periodic update loop:
        - Update webcam preview
        - Run hand detector
        - Toggle menu visibility
        """
        frame = self.camera.last_frame

        if frame is not None:
            img = ImageTk.PhotoImage(frame)
            self.preview_label.imgtk = img
            self.preview_label.config(image=img)

            if self.detector.detect(frame):  # Dummy detection
                self.menu_frame.grid()
                self.mode_var.set("Add Mode")
            else:
                self.menu_frame.grid_remove()
                self.mode_var.set("Idle")

        self.renderer.render(self.tree_canvas)
        self.root.after(30, self._update)

    def run(self):
        self.root.mainloop()
