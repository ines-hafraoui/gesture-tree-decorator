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
from gui.ornament_menu import OrnamentMenu
from gui.painting_menu import PaintingMenu
from utils.config import ASSETS_PATH
import random
import os

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
        self.add_cooldown = 0.5  # cooldown between add/remove actions
        self.cam_width = None
        self.cam_height = None

        # Modes & finger stability
        self.mode = "ornament"  # "ornament" or "painting"
        self.last_finger_count = None
        self.finger_stable_since = 0
        self.required_stable_time = 0.25  # seconds

        # Painting menu data
        # Define paths once
        self.painting_paths = [ 
            os.path.join(ASSETS_PATH, "artworks", f"artwork{1}.jpeg"), 
            os.path.join(ASSETS_PATH, "artworks", f"artwork{2}.jpeg"),
            os.path.join(ASSETS_PATH, "artworks", f"artwork{3}.jpeg"),  
            os.path.join(ASSETS_PATH, "artworks", f"artwork{4}.jpeg") 
        ]
        self.painting_menu = None # Will be initialized in _build_ui

        # UI
        self._build_ui()
        self.root.bind("<Key>", self._on_key)

        # Update loop
        self._update()

    def _build_ui(self):
        # Left frame: tree + menu
        left_frame = ttk.Frame(self.root)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=0)
        left_frame.grid_rowconfigure(2, weight=0)
        left_frame.grid_columnconfigure(0, weight=1)

        # Tree canvas
        self.tree_canvas = tk.Canvas(left_frame, width=600, height=580)
        self.tree_canvas.grid(row=0, column=0, sticky="ns")

        # Ornament menu canvas
        self.menu_canvas = tk.Canvas(left_frame, width=600, height=70)
        self.menu_canvas.grid(row=1, column=0, sticky="ew")
        self.menu = OrnamentMenu(self.menu_canvas)
        self.menu.render(self.menu_canvas)

        # Painting menu canvas (hidden initially)
        self.painting_menu_canvas = tk.Canvas(left_frame, width=600, height=70)
        self.painting_menu_canvas.grid(row=2, column=0, sticky="ew")
        self.painting_menu_canvas.grid_remove()  # start hidden

        # Initialize the PaintingMenu instance ONCE
        self.painting_menu = PaintingMenu(self.painting_menu_canvas, self.painting_paths)

        # Right frame: camera preview + controls
        right_frame = ttk.Frame(self.root)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        self.preview_label = ttk.Label(right_frame)
        self.preview_label.grid(row=0, column=0, sticky="nsew", pady=5)

        self.mode_var = tk.StringVar(value="Idle")
        ttk.Label(right_frame, textvariable=self.mode_var).grid(row=1, column=0, pady=5)

        self.start_btn = ttk.Button(right_frame, text="Start Hand Detection",
                                   command=self.toggle_camera)
        self.start_btn.grid(row=2, column=0, pady=5)

    def toggle_camera(self):
        if not self.camera.running:
            self.camera.start()
            self.start_btn.config(text="Stop Detection")
        else:
            self.camera.stop()
            self.mode_var.set("Idle")
            self.start_btn.config(text="Start Hand Detection")

    def _random_position(self):
        return (random.randint(50, 550), random.randint(80, 520))

    def _on_key(self, event):
        if event.char in "12345":
            idx = int(event.char)
            self._manual_add(idx)

    def _manual_add(self, idx):
        """Keyboard/manual selection"""
        pos = self._random_position()
        ref_image = None
        if idx == 3:
            # Enter painting selection mode
            self.mode = "painting"
            self.painting_menu_canvas.grid()
            self.painting_menu.render(self.painting_menu_canvas) # Use existing instance
            return
        ornament = self.manager.create_ornament(idx, pos, ref_image)
        self.manager.add(ornament)
        self.renderer.render(self.tree_canvas)

    def _finger_stable(self, count):
        now = time.time()
        if self.last_finger_count != count:
            self.last_finger_count = count
            self.finger_stable_since = now
            return False
        return (now - self.finger_stable_since) >= self.required_stable_time

    def _handle_ornament_mode(self, count, hand_detected):
        if not hand_detected or not self._finger_stable(count):
            # If hand is not stable, or not detected, ensure painting menu is hidden
            if self.painting_menu_canvas.winfo_ismapped():
                self.painting_menu_canvas.grid_remove()
            return

        now = time.time()
        if now - self.last_add_time < self.add_cooldown:
            return

        if count == 0:
            last = self.manager.remove_last()
            self.last_add_time = now
            if last:
                self.menu.select(last.type_id - 1, self.menu_canvas, color="red")
            
            # Hide painting menu if it was accidentally visible
            if self.painting_menu_canvas.winfo_ismapped():
                 self.painting_menu_canvas.grid_remove()
                 
        elif count == 3:
            # Enter painting selection
            self.mode = "painting"
            
            # Check if the canvas is already visible to avoid unnecessary render calls
            if not self.painting_menu_canvas.winfo_ismapped():
                self.painting_menu_canvas.grid()
                self.painting_menu.render(self.painting_menu_canvas) # RENDER ONLY ONCE ON MODE ENTRY

            # Reset the selection upon entering the mode
            if self.painting_menu.selected_index is not None:
                self.painting_menu.select(None, self.painting_menu_canvas)
                
        else:
            self.manager.add_ornament_random(count)
            self.last_add_time = now
            self.menu.select(count - 1, self.menu_canvas, color="green")
            
            # Hide painting menu if it was accidentally visible
            if self.painting_menu_canvas.winfo_ismapped():
                 self.painting_menu_canvas.grid_remove()

    def _handle_painting_mode(self, count, hand_detected):
        if not self.painting_menu or not self._finger_stable(count):
            return
            
        now = time.time()
        n = len(self.painting_paths)
        
        # 1. Selection logic (Hand is present, count is 1 to N)
        if hand_detected and 1 <= count <= n:
            idx = count - 1
            # Select the painting based on the finger count (1 to N)
            self.painting_menu.select(idx, self.painting_menu_canvas)
            
        # 2. Confirmation/Cancellation logic (Hand is closed OR hand disappears)
        # We use a stable count of 0 (either closed hand or no hand detected)
        elif count == 0 and now - self.last_add_time >= self.add_cooldown:
            
            if self.painting_menu.selected_index is not None:
                # Add the selected ornament
                selected_idx = self.painting_menu.selected_index
                
                # Check if the path exists before attempting to open
                if os.path.exists(self.painting_paths[selected_idx]):
                    ref_img = Image.open(self.painting_paths[selected_idx])
                    self.manager.add_ornament_random(3,ref_image=ref_img)
                    self.renderer.render(self.tree_canvas)
                    self.menu.select(3 - 1, self.menu_canvas, color="green")
                else:
                    print(f"Error: Painting file not found at {self.painting_paths[selected_idx]}.")
            
            # Transition back to ornament mode (happens regardless of whether an item was added)
            self.painting_menu_canvas.grid_remove()
            self.mode = "ornament"
            self.last_add_time = now

        # If the hand is detected but the finger count is > N (out of selection range),
        # or if the hand is not detected but the count is not stable, we do nothing.

    def _update_preview(self, frame):
        try:
            img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.preview_label.imgtk = img
            self.preview_label.config(image=img)
        except Exception as e:
            print("Preview update failed:", e)

    def _update(self):
        if self.camera.running:
            frame = self.camera.read_frame()
            if frame is not None and self.cam_width is None:
                h, w, _ = frame.shape
                self.cam_width = w
                self.cam_height = h
            if frame is not None:
                count, annotated, tip = self.detector.process(frame)
                hand_detected = tip is not None
                self._update_preview(annotated)
                
                # Update mode variable for display before handling mode logic
                self.mode_var.set(f"Mode: {self.mode.capitalize()} | Fingers: {count}" if hand_detected else "No hand detected")

                if self.mode == "ornament":
                    self._handle_ornament_mode(count, hand_detected)
                elif self.mode == "painting":
                    self._handle_painting_mode(count, hand_detected)

        else:
            self.preview_label.config(image="")
            self.mode_var.set("Idle")

        self.manager.update()
        self.renderer.render(self.tree_canvas)
        self.root.after(30, self._update)

    def run(self):
        self.root.mainloop()