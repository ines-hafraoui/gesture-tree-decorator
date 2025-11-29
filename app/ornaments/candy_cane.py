# app/ornaments/candy_cane.py
from ornaments.ornament import Ornament
from ornaments.effects import apply_contrast

class CandyCane(Ornament):
    def __init__(self, position):
        super().__init__(type_id=1, position=position)
        self.contrast = 1.0

    def update(self):
        # Apply contrast relative to the original sprite
        self.image = apply_contrast(self.original_image, self.contrast)

        # Update contrast
        self.contrast += 0.02
        if self.contrast > 2.0:
            self.contrast = 1.0
