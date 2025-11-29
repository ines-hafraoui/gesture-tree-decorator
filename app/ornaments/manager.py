import random
from ornaments.ornament import Ornament
import numpy as np
from PIL import Image

# Import all the other subclasses we created earlier
from ornaments.star import Star
from ornaments.candy_cane import CandyCane
from ornaments.painting import Painting
from ornaments.bell import Bell
from ornaments.ball import DecorativeBall
# Import global effects
from ornaments.effects import apply_blur
from ornaments.effects import apply_contrast
from ornaments.effects import apply_histogram_specification

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

    # CREATION
    def create_ornament(self, type_id, position, ref_image=None):
        if type_id == 1:
            self.global_contrast += 0.05  # increase contrast per candy cane
            # Cap contrast if needed
            self.global_contrast = min(self.global_contrast, 3.0)
            self.current_tree = apply_contrast(self.original_tree, self.global_contrast)
            return CandyCane(position)  
        elif type_id == 2:
            return Bell(position)
        elif type_id == 3:
            return Painting(position, ref_image=ref_image)
        elif type_id == 4:
            return DecorativeBall(position)  
        elif type_id == 5:
            return Star(position)
        else:
            return Ornament(type_id, position)

    def add(self, ornament):
        self.ornaments.append(ornament)

    # REMOVE
    def remove_last(self):
        if self.ornaments:
            return self.ornaments.pop()
        return None


    # RANDOM TREE PLACEMENT
    def add_ornament_random(self, type_id):
        # Try multiple positions to find one with good spacing
        best_position = None
        best_min_distance = 0
        max_attempts = 20  # Number of positions to try
        min_spacing = 60  # Minimum distance between ornaments
        
        for _ in range(max_attempts):
            x = random.randint(self.tree_center_x - self.tree_width // 2,
                               self.tree_center_x + self.tree_width // 2)

            half_width = self.tree_width // 2

            y_min = self.tree_top_y + int(
                (abs(x - self.tree_center_x) / half_width)
                * (self.tree_bottom_y - self.tree_top_y) * 0.5
            )

            y = random.randint(y_min, self.tree_bottom_y)
            
            # Calculate minimum distance to existing ornaments
            min_distance = float('inf')
            for orn in self.ornaments:
                dx = x - orn.position[0]
                dy = y - orn.position[1]
                distance = (dx * dx + dy * dy) ** 0.5
                min_distance = min(min_distance, distance)
            
            # If no ornaments exist yet, use this position
            if not self.ornaments:
                best_position = (x, y)
                break
            
            # Keep track of the position with best spacing
            if min_distance > best_min_distance:
                best_min_distance = min_distance
                best_position = (x, y)
                
                # If we found a position with good spacing, use it
                if min_distance >= min_spacing:
                    break

        ornament = self.create_ornament(type_id, best_position)
        self.add(ornament)

    # UPDATE LOOP
    def update(self):
        # Check if any Painting exists for histogram specification
        painting_refs = [o.ref_image for o in self.ornaments if isinstance(o, Painting) and o.ref_image is not None]
        if painting_refs:
            # Use the last added Painting as reference
            ref_img = painting_refs[-1]
            # Convert self.current_tree to np.array
            tree_np = np.array(self.original_tree)
            tree_matched = apply_histogram_specification(tree_np, np.array(ref_img))
            self.current_tree = Image.fromarray(tree_matched)

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

    # BLUR CALCULATION
    def compute_global_blur(self):
        return sum(
            o.blur_strength
            for o in self.ornaments
            if isinstance(o, DecorativeBall)
        )
