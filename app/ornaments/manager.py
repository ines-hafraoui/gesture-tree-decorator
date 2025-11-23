# app/ornaments/manager.py
import random
from ornaments.ornament import Ornament

class OrnamentManager:
    def __init__(self):
        self.ornaments = []
        # self.positions = [
        #     (250, 180), (300, 240),
        #     (220, 330), (350, 360),
        #     (260, 430)
        # ]
        self.tree_center_x = 300
        self.tree_bottom_y = 500
        self.tree_top_y = 70
        self.tree_width = 300

    def add_ornament(self, type_id):
        """
        Add an ornament at a random position within the triangular tree area.
        x is random across tree width, y is limited based on x to stay inside tree shape.
        """
        x = random.randint(self.tree_center_x - self.tree_width//2, 
                           self.tree_center_x + self.tree_width//2)
        
        half_width = self.tree_width // 2

        y_min = self.tree_top_y + int((abs(x - self.tree_center_x) / half_width) * (self.tree_bottom_y - self.tree_top_y) * 0.5)
        y = random.randint(y_min, self.tree_bottom_y)

        self.ornaments.append(Ornament(type_id, (x, y)))

    def remove_last(self):
        if self.ornaments:
            self.ornaments.pop()
