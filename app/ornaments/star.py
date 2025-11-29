# app/ornaments/star.py
from ornaments.ornament import Ornament
from ornaments.effects import apply_brightness

class Star(Ornament):
    def __init__(self, position):
        super().__init__(type_id=5, position=position)
        self.brightness = 0
        self.delta = 20  # bigger steps for visible effect

    def update(self):
        # Always start from original image
        self.image = apply_brightness(self.original_image, self.brightness)

        self.brightness += self.delta

        # Bounce between -100 and +100 for stronger pulse
        if self.brightness > 100 or self.brightness < -100:
            self.delta *= -1