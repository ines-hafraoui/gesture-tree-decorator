# app/ornaments/ornament.py
from PIL import Image
import os
from utils.config import ASSETS_PATH

class Ornament:
    def __init__(self, type_id, position):
        path = os.path.join(ASSETS_PATH, "ornaments", f"ornament{type_id}.png")
        self.image = Image.open(path).resize((70, 70))
        self.position = position  # (x,y)
        self.type_id = type_id
        self.tk_img = None
