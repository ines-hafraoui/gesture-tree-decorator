# app/gui/painting_menu.py
import tkinter as tk
from PIL import Image, ImageTk
import os

class PaintingMenu:
    """Horizontal menu for selecting painting reference images"""
    def __init__(self, parent, paths):
        self.parent = parent
        self.paths = paths
        self.tk_images = []
        self.selected_index = None
        self.box_id = None
        self.load_images()

    def load_images(self):
        self.tk_images.clear()
        for path in self.paths:
            if os.path.exists(path):
                img = Image.open(path).resize((50,50))
                self.tk_images.append(ImageTk.PhotoImage(img))
            else:
                self.tk_images.append(None)

    def render(self, canvas):
        canvas.delete("all")
        canvas_width = int(canvas.winfo_width()) or 300
        num_imgs = len(self.tk_images)
        thumb_width = 50
        spacing = (canvas_width - thumb_width) / max(num_imgs - 1, 1)
        self.positions = [int(i * spacing) for i in range(num_imgs)]

        for i, tk_img in enumerate(self.tk_images):
            if tk_img:
                canvas.create_image(self.positions[i], 10, anchor="nw", image=tk_img)

        # Selection box
        if self.selected_index is not None:
            x0 = self.positions[self.selected_index]-5
            y0 = 5
            x1 = x0 + thumb_width + 10
            y1 = 65
            self.box_id = canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=3)

        canvas.painting_images = self.tk_images
        canvas.painting_box = self.box_id

    def select(self, idx, canvas):
        if 0 <= idx < len(self.tk_images):
            self.selected_index = idx
            self.render(canvas)