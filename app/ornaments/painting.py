# app/ornaments/painting.py
from ornaments.ornament import Ornament
from ornaments.effects import apply_histogram_equalization

class Painting(Ornament):
    def __init__(self, position):
        super().__init__(type_id=3, position=position)

    def update(self):
        # self.image = apply_histogram_equalization(self.image)
        pass  # currently disabled for performance reasons