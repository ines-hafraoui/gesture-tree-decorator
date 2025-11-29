from enum import Enum

class State(Enum):
    IDLE = 0
    ORNAMENT_SELECTION = 1
    ORNAMENT_PLACEMENT = 2
    ARTWORK_MENU = 3