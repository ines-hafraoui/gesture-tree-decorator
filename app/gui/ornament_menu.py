# app/gui/ornament_menu.py
import tkinter as tk
from PIL import Image, ImageTk
from utils.config import ASSETS_PATH
import os

class OrnamentMenu:
    """Horizontal menu using canvas with a moving selection box"""
    def __init__(self, parent, num_ornaments=5):
        self.parent = parent
        self.num_ornaments = num_ornaments
        self.images = []
        self.tk_images = []
        self.selected_index = None
        self.box_id = None
        self.box_color = "green"  # default for add
        self.load_images()

    def load_images(self):
        self.images.clear()
        self.tk_images.clear()
        for i in range(1, self.num_ornaments + 1):
            path = os.path.join(ASSETS_PATH, "ornaments", f"ornament{i}.png")
            if os.path.exists(path):
                img = Image.open(path).resize((50, 50))
                self.images.append(img)
                self.tk_images.append(ImageTk.PhotoImage(img))
            else:
                self.images.append(None)
                self.tk_images.append(None)

    def render(self, canvas, y=10):
        canvas.delete("all")
        canvas.update_idletasks()
        canvas_width = int(canvas.winfo_width()) or 300

        num_imgs = len(self.tk_images)
        thumb_width = 50
        if num_imgs <= 1:
            positions = [canvas_width // 2]
        else:
            spacing = (canvas_width - thumb_width) / (num_imgs - 1)
            positions = [int(i * spacing) for i in range(num_imgs)]

        # Draw thumbnails
        for i, tk_img in enumerate(self.tk_images):
            if tk_img is not None:
                canvas.create_image(positions[i], y, anchor="nw", image=tk_img)

        # Draw selection box if something is selected
        if self.selected_index is not None:
            x0 = positions[self.selected_index] - 5
            y0 = y - 5
            x1 = positions[self.selected_index] + thumb_width + 5
            y1 = y + thumb_width + 5
            self.box_id = canvas.create_rectangle(x0, y0, x1, y1, outline=self.box_color, width=3)

        # Keep references
        canvas.menu_images = self.tk_images
        canvas.selection_box = self.box_id

    def select(self, idx, canvas, color="green"):
        """Set selected index and box color, then redraw"""
        if 0 <= idx < self.num_ornaments:
            self.selected_index = idx
            self.box_color = color
            self.render(canvas)