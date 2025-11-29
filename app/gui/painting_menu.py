import tkinter as tk
from PIL import Image, ImageTk

class PaintingMenu:
    """Horizontal menu for selecting painting reference images"""
    def __init__(self, parent, paths):
        self.parent = parent
        self.paths = paths          # list of image paths
        self.images = []
        self.tk_images = []
        self.positions = []
        self.selected_index = None
        self.box_id = None

        self._load_images()

    def _load_images(self):
        self.images.clear()
        self.tk_images.clear()

        for path in self.paths:
            try:
                img = Image.open(path).resize((50, 50))
                self.images.append(img)
                self.tk_images.append(ImageTk.PhotoImage(img))
            except Exception as e:
                print("Failed to load painting:", path, e)
                self.images.append(None)
                self.tk_images.append(None)

    def render(self, canvas):
        canvas.delete("all")

        canvas_width = canvas.winfo_width()
        if canvas_width < 10:
            canvas_width = 300  # fallback for initialization

        num_imgs = len(self.tk_images)
        thumb_width = 50

        spacing = (canvas_width - thumb_width) / max(num_imgs - 1, 1)
        self.positions = [int(i * spacing) for i in range(num_imgs)]

        for i, img in enumerate(self.tk_images):
            if img:
                canvas.create_image(self.positions[i], 10, anchor="nw", image=img)

        # Draw selection box
        if self.selected_index is not None:
            x = self.positions[self.selected_index]
            canvas.create_rectangle(
                x - 5, 5, x + thumb_width + 5, 65,
                outline="red", width=3
            )

        canvas.painting_menu_refs = self.tk_images

    def select(self, idx, canvas):
        self.selected_index = idx
        self.render(canvas)