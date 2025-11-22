# app/ornaments/manager.py
from ornaments.ornament import Ornament

class OrnamentManager:
    def __init__(self):
        self.ornaments = []
        self.positions = [
            (150, 120), (200, 240),
            (120, 330), (250, 360),
            (160, 430)
        ]

    def add_ornament(self, type_id):
        idx = len(self.ornaments) % len(self.positions)
        pos = self.positions[idx]
        self.ornaments.append(Ornament(type_id, pos))

    def remove_last(self):
        if self.ornaments:
            self.ornaments.pop()
