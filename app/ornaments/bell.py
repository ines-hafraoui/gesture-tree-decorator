# app/ornaments/garland.py
from ornaments.ornament import Ornament
from ornaments.effects import apply_mosaic

class Bell(Ornament):
    def __init__(self, position):
        super().__init__(type_id=2, position=position)
        self.scale = 0.05
        self.direction = 0.002

    def update(self):
        self.image = apply_mosaic(self.original_image, scale=self.scale)
        
        # oscillate pixelation level
        self.scale += self.direction
        if self.scale > 0.1 or self.scale < 0.03:
            self.direction *= -1

        