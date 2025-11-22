# app/gui/renderer.py
from PIL import Image, ImageTk
import os
from utils.config import ASSETS_PATH

class TreeRenderer:
    def __init__(self, ornament_manager):
        self.manager = ornament_manager
        tree_path = os.path.join(ASSETS_PATH, "tree.png")
        self.tree_img = Image.open(tree_path).resize((600, 580))

    def render(self, canvas):
        canvas.delete("all")

        # Draw tree
        tk_tree = ImageTk.PhotoImage(self.tree_img)
        canvas.image_ref = tk_tree
        canvas.create_image(0, 0, anchor="nw", image=tk_tree)

        # Draw ornaments
        for ornament in self.manager.ornaments:
            tk_img = ImageTk.PhotoImage(ornament.image)
            ornament.tk_img = tk_img
            x, y = ornament.position
            canvas.create_image(x, y, anchor="center", image=tk_img)
