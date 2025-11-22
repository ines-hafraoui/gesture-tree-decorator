# app/gui/assets.py
from PIL import Image
import os
from utils.config import ASSETS_PATH

def load_asset(path, size=None):
    full = os.path.join(ASSETS_PATH, path)
    img = Image.open(full)
    if size:
        img = img.resize(size)
    return img
