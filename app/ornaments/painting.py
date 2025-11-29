# app/ornaments/painting.py
from ornaments.ornament import Ornament

class Painting(Ornament):
    def __init__(self, position, ref_image=None):
        super().__init__(type_id=3, position=position)
        self.ref_image = ref_image  
