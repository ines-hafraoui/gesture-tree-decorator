# app/gui/window.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import time
from vision.camera_thread import CameraThread
from vision.hand_detector import HandGesture
from gui.renderer import TreeRenderer
from gui.state import State
from ornaments.manager import OrnamentManager
from utils.config import ASSETS_PATH
import random

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
        self.cam_width = None
        self.cam_height = None

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

    #Temporary random position generator for ornament placement
    def _random_position(self):
        return (
            random.randint(50, 550),   # X within canvas
            random.randint(80, 520)    # Y within canvas
        )
    
    def _select_ornament(self, idx):
        ornament = self.manager.create_ornament(idx, self._random_position())
        self.manager.add(ornament)
        self.renderer.render(self.tree_canvas)
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

    def _update_finger_count(self, count, hand_detected):
        """ Detect finger count and add/remove ornament if cooldown passed """
        self.mode_var.set(f"Fingers: {count}")

        now = time.time()
        if hand_detected and now - self.last_add_time > self.add_cooldown:
            if count == 0:
                # Remove last ornament when showing 0 fingers (fist)
                self.manager.remove_last()
                self.last_add_time = now
            elif count != 0:
                # Add ornament for 1-5 fingers
                self.manager.add_ornament_random(count)
                self.last_add_time = now

    def _convert_tip_to_canvas(self, tip):
        if tip is None:
            return None

        if self.cam_width is None or self.cam_height is None:
            return None  # resolution unknown yet

        cam_x, cam_y = tip

        # Normalize
        norm_x = cam_x / self.cam_width
        norm_y = cam_y / self.cam_height

        CANVAS_W = 600
        CANVAS_H = 580

        x = int(norm_x * CANVAS_W)
        y = int(norm_y * CANVAS_H)

        return (x, y)

    def _select_ornament(self, idx):
        pos = self._random_position()
        ornament = self.manager.create_ornament(idx, pos)
        self.manager.add(ornament)
        self.renderer.render(self.tree_canvas)

    def _update(self):
        """
        Periodic update loop:
        - Update webcam preview
        - Run hand detector
        - Toggle menu visibility
        """
        if self.camera.running:
            frame = self.camera.read_frame()
            if frame is not None and self.cam_width is None:
                h, w, _ = frame.shape
                self.cam_width = w
                self.cam_height = h
            if frame is not None:
                finger_count, annotated_frame, index_tip_pos = self.detector.process(frame)
                self._update_preview(annotated_frame)
                hand_detected = index_tip_pos is not None
                self._update_finger_count(finger_count, hand_detected) 
                self.mode_var.set(f"Fingers: {finger_count}" if hand_detected else "No hand detected")
                mapped_tip = self._convert_tip_to_canvas(index_tip_pos) 
        else:
            self.preview_label.config(image="")
            self.mode_var.set("Idle")
            self.menu_frame.grid_remove()
        
        self.manager.update()         # <-- UPDATE ORNAMENT EFFECTS
        self.renderer.render(self.tree_canvas)
        self.root.after(1, self._update)

    def run(self):
        self.root.mainloop()
