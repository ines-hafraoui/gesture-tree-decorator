import random
from ornaments.ornament import Ornament

# Import all the other subclasses we created earlier
from ornaments.star import Star
from ornaments.candy_cane import CandyCane
from ornaments.painting import Painting
from ornaments.bell import Bell
from ornaments.ball import DecorativeBall
# Import global effects
from ornaments.effects import apply_blur
from ornaments.effects import apply_contrast

class OrnamentManager:
    def __init__(self):
        self.ornaments = []

        self.tree_center_x = 300
        self.tree_bottom_y = 500
        self.tree_top_y = 70
        self.tree_width = 300
        # Tree images for global effects
        self.current_tree = None
        self.original_tree = None
        self.global_contrast = 1.0  # start normal

    def set_tree(self, tree_img):
        self.original_tree = tree_img
        self.current_tree = tree_img.copy()

    # --------------------
    # CREATION
    # --------------------
    def create_ornament(self, type_id, position):
        if type_id == 1:
            self.global_contrast += 0.05  # increase contrast per candy cane
            # Cap contrast if needed
            self.global_contrast = min(self.global_contrast, 3.0)
            self.current_tree = apply_contrast(self.original_tree, self.global_contrast)
            return CandyCane(position)  
        elif type_id == 2:
            return Bell(position)
        elif type_id == 3:
            return Painting(position)
        elif type_id == 4:
            return DecorativeBall(position)  # <-- your blur ball
        elif type_id == 5:
            return Star(position)
        else:
            return Ornament(type_id, position)

    def add(self, ornament):
        self.ornaments.append(ornament)

    # --------------------
    # REMOVE
    # --------------------
    def remove_last(self):
        if self.ornaments:
            self.ornaments.pop()

    # --------------------
    # RANDOM TREE PLACEMENT
    # --------------------
    def add_ornament_random(self, type_id):
        x = random.randint(self.tree_center_x - self.tree_width // 2,
                           self.tree_center_x + self.tree_width // 2)

        half_width = self.tree_width // 2

        y_min = self.tree_top_y + int(
            (abs(x - self.tree_center_x) / half_width)
            * (self.tree_bottom_y - self.tree_top_y) * 0.5
        )

        y = random.randint(y_min, self.tree_bottom_y)

        ornament = self.create_ornament(type_id, (x, y))
        self.add(ornament)

    # --------------------
    # UPDATE LOOP
    # --------------------
    def update(self):
        blur_power = self.compute_global_blur()
        ksize = max(3, 2 * blur_power + 1)

        # Compute global contrast from Candy Canes
        for orn in self.ornaments:
            if isinstance(orn, DecorativeBall):
                continue
            if blur_power > 0:
                orn.image = apply_blur(orn.original_image, ksize)
            if isinstance(orn, Painting):
                pass  # Painting update is currently disabled
            orn.update()

    # --------------------
    # BLUR CALCULATION
    # --------------------
    def compute_global_blur(self):
        return sum(
            o.blur_strength
            for o in self.ornaments
            if isinstance(o, DecorativeBall)
        )
