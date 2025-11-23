# app/gui/window.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import time
from vision.camera_thread import CameraThread
from vision.hand_detector import HandGesture
from gui.renderer import TreeRenderer
from ornaments.manager import OrnamentManager
from utils.config import ASSETS_PATH

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gesture Tree Decorator")

        # Core systems
        self.camera = CameraThread()
        self.detector = HandGesture()
        self.manager = OrnamentManager()
        self.renderer = TreeRenderer(self.manager)
        self.last_add_time = 0
        self.add_cooldown = 1

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

    def _update_preview(self, frame):
        """ Convert camera frame to Tkinter image and display """
        try:
            img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.preview_label.imgtk = img
            self.preview_label.config(image=img)
        except Exception as e:
            print("Preview update failed:", e)

    def _update_finger_count(self, count):
        """ Detect finger count and add ornament if cooldown passed """
        self.mode_var.set(f"Fingers: {count}")

        now = time.time()
        if count != 0 and now - self.last_add_time > self.add_cooldown:
            self.manager.add_ornament(count)
            self.last_add_time = now

    def _update(self):
        """
        Periodic update loop:
        - Update webcam preview
        - Run hand detector
        - Toggle menu visibility
        """
        if self.camera.running:
            frame = self.camera.read_frame()
            if frame is not None:
                finger_count, annotated_frame = self.detector.process(frame)
                self._update_preview(annotated_frame) #
                self._update_finger_count(finger_count) #
        else:
            self.preview_label.config(image="")
            self.mode_var.set("Idle")
            self.menu_frame.grid_remove()
        
        self.renderer.render(self.tree_canvas)
        self.root.after(30, self._update)

    def run(self):
        self.root.mainloop()
