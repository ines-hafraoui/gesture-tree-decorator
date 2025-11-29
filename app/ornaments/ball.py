# app/ornaments/ball.py
from ornaments.ornament import Ornament

class DecorativeBall(Ornament):
    def __init__(self, position):
        # type_id = 4 (your system)
        super().__init__(4, position)
        self.blur_strength = 1  # contributes to global blur

    def update(self):
        pass  # ball stays sharp
